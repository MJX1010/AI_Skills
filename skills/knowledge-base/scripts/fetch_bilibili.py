#!/usr/bin/env python3
"""
B站视频内容抓取脚本
支持抓取B站视频信息（标题、UP主、简介、标签等）
"""

import argparse
import json
import re
import sys
import time
from pathlib import Path
from urllib.parse import urlparse, unquote, parse_qs

# 尝试导入可选依赖
try:
    import requests
    from requests.adapters import HTTPAdapter
    from urllib3.util.retry import Retry
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False
    print("警告: requests 未安装，部分功能不可用")

try:
    from bs4 import BeautifulSoup
    HAS_BS4 = True
except ImportError:
    HAS_BS4 = False
    print("警告: beautifulsoup4 未安装，HTML解析功能受限")

try:
    from playwright.sync_api import sync_playwright
    HAS_PLAYWRIGHT = True
except ImportError:
    HAS_PLAYWRIGHT = False


class BilibiliVideoFetcher:
    """B站视频获取器"""
    
    def __init__(self):
        self.session = None
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
            'Accept-Encoding': 'gzip, deflate, br',
            'Referer': 'https://search.bilibili.com/',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0',
        }
        
        if HAS_REQUESTS:
            self.session = requests.Session()
            self.session.headers.update(self.headers)
            # 配置重试策略
            retry_strategy = Retry(
                total=3,
                backoff_factor=1,
                status_forcelist=[429, 500, 502, 503, 504],
            )
            adapter = HTTPAdapter(max_retries=retry_strategy)
            self.session.mount("http://", adapter)
            self.session.mount("https://", adapter)
    
    def extract_bvid_from_url(self, url):
        """从URL中提取BV号"""
        # 匹配BV号格式
        patterns = [
            r'BV[a-zA-Z0-9]{10}',  # 标准BV号
            r'av(\d+)',  # 旧版AV号
            r'b23\.tv/([a-zA-Z0-9]+)',  # 短链接
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                if pattern.startswith('av'):
                    return {'type': 'av', 'id': match.group(1)}
                elif 'b23.tv' in pattern:
                    return {'type': 'short', 'id': match.group(1)}
                else:
                    return {'type': 'bv', 'id': match.group(0)}
        
        return None
    
    def resolve_short_url(self, short_url):
        """解析B站短链接获取真实URL"""
        if not HAS_REQUESTS:
            return None
        
        try:
            # 短链接可能需要跟随重定向
            response = self.session.head(short_url, allow_redirects=True, timeout=10)
            return response.url
        except Exception as e:
            print(f"解析短链接失败: {e}")
            return None
    
    def fetch_with_api(self, bvid):
        """
        使用B站API获取视频信息（绕过反爬）
        这是推荐方法，因为API有较少的限制
        """
        if not HAS_REQUESTS:
            return None, "requests 未安装"
        
        try:
            print(f"[方法1] 使用B站API获取: {bvid}...")
            
            # B站视频详情API
            api_url = f'https://api.bilibili.com/x/web-interface/view?bvid={bvid}'
            
            response = self.session.get(api_url, timeout=15)
            data = response.json()
            
            if data.get('code') != 0:
                return None, f"API错误: {data.get('message', '未知错误')}"
            
            video_data = data.get('data', {})
            
            # 构建返回数据
            result = {
                'bvid': video_data.get('bvid', bvid),
                'aid': video_data.get('aid', ''),
                'title': video_data.get('title', ''),
                'description': video_data.get('desc', ''),
                'duration': video_data.get('duration', 0),
                'pubdate': video_data.get('pubdate', 0),
                'ctime': video_data.get('ctime', 0),
                'view_count': video_data.get('stat', {}).get('view', 0),
                'like_count': video_data.get('stat', {}).get('like', 0),
                'coin_count': video_data.get('stat', {}).get('coin', 0),
                'favorite_count': video_data.get('stat', {}).get('favorite', 0),
                'share_count': video_data.get('stat', {}).get('share', 0),
                'reply_count': video_data.get('stat', {}).get('reply', 0),
                'danmaku_count': video_data.get('stat', {}).get('danmaku', 0),
                'owner': {
                    'mid': video_data.get('owner', {}).get('mid', ''),
                    'name': video_data.get('owner', {}).get('name', ''),
                    'face': video_data.get('owner', {}).get('face', ''),
                },
                'pic': video_data.get('pic', ''),
                'tname': video_data.get('tname', ''),  # 分区名称
                'copyright': video_data.get('copyright', 0),  # 1=原创, 2=转载
                'videos': video_data.get('videos', 1),  # 分P数量
                'tags': [],
                'pages': [],
            }
            
            # 获取标签
            cid = video_data.get('cid', '')
            if cid:
                tags_data = self.fetch_tags(bvid)
                if tags_data:
                    result['tags'] = tags_data
            
            # 获取分P信息
            pages = video_data.get('pages', [])
            result['pages'] = [
                {
                    'cid': p.get('cid', ''),
                    'page': p.get('page', 1),
                    'part': p.get('part', ''),  # 分P标题
                    'duration': p.get('duration', 0),
                }
                for p in pages
            ]
            
            return result, None
            
        except Exception as e:
            return None, f"API获取失败: {str(e)}"
    
    def fetch_tags(self, bvid):
        """获取视频标签"""
        try:
            api_url = f'https://api.bilibili.com/x/tag/archive/tags?bvid={bvid}'
            response = self.session.get(api_url, timeout=10)
            data = response.json()
            
            if data.get('code') == 0:
                tags = data.get('data', [])
                return [tag.get('tag_name', '') for tag in tags if tag.get('tag_name')]
            return []
        except:
            return []
    
    def fetch_with_playwright(self, url, timeout=60):
        """
        使用 Playwright 渲染页面获取内容
        适用于API被限制的情况
        """
        if not HAS_PLAYWRIGHT:
            return None, "playwright 未安装，请运行: pip install playwright && playwright install"
        
        try:
            print(f"[方法2] 使用 Playwright 渲染: {url[:60]}...")
            
            with sync_playwright() as p:
                # 启动浏览器，使用更真实的配置
                browser = p.chromium.launch(
                    headless=True,
                    args=['--disable-blink-features=AutomationControlled']
                )
                
                context = browser.new_context(
                    user_agent=self.headers['User-Agent'],
                    viewport={'width': 1920, 'height': 1080},
                    locale='zh-CN',
                    timezone_id='Asia/Shanghai',
                )
                
                # 设置额外的浏览器指纹
                context.add_init_script("""
                    Object.defineProperty(navigator, 'webdriver', {
                        get: () => undefined
                    });
                    Object.defineProperty(navigator, 'plugins', {
                        get: () => [1, 2, 3]
                    });
                """)
                
                page = context.new_page()
                
                # 拦截非必要资源，加快加载
                page.route("**/*.{png,jpg,jpeg,gif,css,woff,woff2,mp4,webm}", 
                          lambda route: route.abort())
                
                # 访问页面
                page.goto(url, wait_until='networkidle', timeout=timeout*1000)
                
                # 等待视频页面关键元素
                try:
                    page.wait_for_selector(
                        'h1.video-title, .video-title, .title, [class*="title"]',
                        timeout=15000
                    )
                except:
                    pass  # 有些页面结构不同
                
                # 等待一下，确保JS渲染完成
                time.sleep(3)
                
                # 获取页面HTML
                html = page.content()
                
                # 尝试从页面脚本中提取__INITIAL_STATE__
                scripts = page.query_selector_all('script')
                initial_state = None
                for script in scripts:
                    content = script.inner_text()
                    if '__INITIAL_STATE__' in content:
                        # 提取JSON数据
                        match = re.search(r'window\._{2}INITIAL_STATE__\s*=\s*({.+?});', content)
                        if match:
                            try:
                                initial_state = json.loads(match.group(1))
                                break
                            except:
                                pass
                
                browser.close()
                
                if initial_state:
                    return {'type': 'initial_state', 'data': initial_state}, None
                else:
                    return {'type': 'html', 'data': html}, None
                
        except Exception as e:
            return None, f"Playwright 渲染失败: {str(e)}"
    
    def parse_from_initial_state(self, initial_state):
        """从页面初始状态解析视频信息"""
        try:
            video_info = initial_state.get('videoInfo', {})
            
            result = {
                'bvid': video_info.get('bvid', ''),
                'aid': video_info.get('aid', ''),
                'title': video_info.get('title', ''),
                'description': video_info.get('desc', ''),
                'duration': video_info.get('duration', 0),
                'pic': video_info.get('pic', ''),
                'pubdate': video_info.get('pubdate', 0),
                'owner': {
                    'mid': video_info.get('owner', {}).get('mid', ''),
                    'name': video_info.get('owner', {}).get('name', ''),
                    'face': video_info.get('owner', {}).get('face', ''),
                },
                'stat': video_info.get('stat', {}),
                'tags': [tag.get('tag_name', '') for tag in video_info.get('tags', [])],
                'tname': video_info.get('tname', ''),
            }
            
            # 添加统计数据
            stat = result.get('stat', {})
            result['view_count'] = stat.get('view', 0)
            result['like_count'] = stat.get('like', 0)
            result['coin_count'] = stat.get('coin', 0)
            result['favorite_count'] = stat.get('favorite', 0)
            result['share_count'] = stat.get('share', 0)
            result['reply_count'] = stat.get('reply', 0)
            result['danmaku_count'] = stat.get('danmaku', 0)
            
            return result
            
        except Exception as e:
            return {'error': f'解析initial_state失败: {str(e)}'}
    
    def parse_from_html(self, html):
        """从HTML解析视频信息（备用方案）"""
        if not HAS_BS4:
            return self._parse_with_regex(html)
        
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            result = {}
            
            # 提取标题
            title_selectors = [
                'h1.video-title',
                '.video-title',
                '[data-e2e="video-title"]',
                'h1.title',
            ]
            for selector in title_selectors:
                elem = soup.select_one(selector)
                if elem:
                    result['title'] = elem.get_text(strip=True)
                    break
            
            # 提取UP主
            owner_selectors = [
                '.up-name',
                '.username',
                '[data-e2e="up-name"]',
                '.up-info .name',
            ]
            for selector in owner_selectors:
                elem = soup.select_one(selector)
                if elem:
                    result['owner'] = {'name': elem.get_text(strip=True)}
                    break
            
            # 提取简介
            desc_selectors = [
                '.desc-info-text',
                '.video-desc',
                '[data-e2e="video-desc"]',
                '.desc',
            ]
            for selector in desc_selectors:
                elem = soup.select_one(selector)
                if elem:
                    result['description'] = elem.get_text(strip=True)
                    break
            
            # 提取播放量等数据
            stat_selectors = [
                '.view-text',
                '.video-data .view',
                '[data-e2e="video-view"]',
            ]
            for selector in stat_selectors:
                elem = soup.select_one(selector)
                if elem:
                    text = elem.get_text(strip=True)
                    # 解析数字
                    match = re.search(r'[\d\.]+', text)
                    if match:
                        result['view_count'] = match.group(0)
                    break
            
            return result
            
        except Exception as e:
            return {'error': f'HTML解析失败: {str(e)}'}
    
    def _parse_with_regex(self, html):
        """使用正则表达式解析（最后备用方案）"""
        try:
            result = {}
            
            # 提取标题
            title_match = re.search(r'<h1[^>]*class="[^"]*video-title[^"]*"[^>]*>(.*?)</h1>', html, re.DOTALL)
            if title_match:
                result['title'] = re.sub(r'<[^>]+>', '', title_match.group(1)).strip()
            
            # 提取UP主
            owner_match = re.search(r'class="[^"]*up-name[^"]*"[^>]*>(.*?)</', html, re.DOTALL)
            if owner_match:
                result['owner'] = {'name': re.sub(r'<[^>]+>', '', owner_match.group(1)).strip()}
            
            # 提取简介
            desc_match = re.search(r'class="[^"]*desc-info[^"]*"[^>]*>(.*?)</div>', html, re.DOTALL)
            if desc_match:
                result['description'] = re.sub(r'<[^>]+>', ' ', desc_match.group(1)).strip()
            
            return result
            
        except Exception as e:
            return {'error': f'正则解析失败: {str(e)}'}
    
    def fetch(self, url, method='auto'):
        """
        抓取B站视频的主函数
        
        Args:
            url: B站视频URL
            method: 抓取方法 ('api', 'playwright', 'auto')
        
        Returns:
            (video_data, error_message)
        """
        # 处理短链接
        if 'b23.tv' in url:
            print(f"🔍 解析短链接...")
            resolved_url = self.resolve_short_url(url)
            if resolved_url:
                url = resolved_url
                print(f"   真实URL: {url}")
        
        # 提取BV号
        bvid_info = self.extract_bvid_from_url(url)
        if not bvid_info:
            return None, "无法从URL中提取BV号"
        
        bvid = bvid_info['id']
        id_type = bvid_info['type']
        
        print(f"📹 识别到 {id_type.upper()}: {bvid}")
        
        video_data = None
        error = None
        
        # 根据方法选择抓取方式
        if method == 'api' and id_type == 'bv':
            video_data, error = self.fetch_with_api(bvid)
        elif method == 'playwright':
            raw_data, error = self.fetch_with_playwright(url)
            if raw_data:
                if raw_data['type'] == 'initial_state':
                    video_data = self.parse_from_initial_state(raw_data['data'])
                else:
                    video_data = self.parse_from_html(raw_data['data'])
        else:  # auto
            # 优先使用API（最可靠）
            if id_type == 'bv':
                video_data, error = self.fetch_with_api(bvid)
            
            # 如果API失败，尝试Playwright
            if not video_data and HAS_PLAYWRIGHT:
                print(f"API获取失败，尝试 Playwright...")
                raw_data, error = self.fetch_with_playwright(url)
                if raw_data:
                    if raw_data['type'] == 'initial_state':
                        video_data = self.parse_from_initial_state(raw_data['data'])
                    else:
                        video_data = self.parse_from_html(raw_data['data'])
        
        if not video_data:
            return None, error or "所有抓取方法均失败"
        
        # 添加源URL
        video_data['source_url'] = url
        
        # 格式化发布时间
        if 'pubdate' in video_data and video_data['pubdate']:
            import datetime
            video_data['publish_time_formatted'] = datetime.datetime.fromtimestamp(
                video_data['pubdate']
            ).strftime('%Y-%m-%d %H:%M:%S')
        
        return video_data, None


def format_duration(seconds):
    """格式化时长"""
    if not seconds:
        return "未知"
    minutes = int(seconds) // 60
    secs = int(seconds) % 60
    if minutes >= 60:
        hours = minutes // 60
        minutes = minutes % 60
        return f"{hours}:{minutes:02d}:{secs:02d}"
    return f"{minutes}:{secs:02d}"


def format_number(num):
    """格式化数字"""
    if not num:
        return "0"
    try:
        num = int(num)
        if num >= 10000:
            return f"{num/10000:.1f}万"
        return str(num)
    except:
        return str(num)


def main():
    parser = argparse.ArgumentParser(description='B站视频内容抓取工具')
    parser.add_argument('url', help='B站视频URL (支持BV号、AV号、短链接)')
    parser.add_argument('--method', '-m', default='auto', 
                        choices=['api', 'playwright', 'auto'],
                        help='抓取方法 (默认: auto)')
    parser.add_argument('--output', '-o', help='输出文件路径')
    parser.add_argument('--format', '-f', default='json', 
                        choices=['json', 'markdown', 'txt'],
                        help='输出格式 (默认: json)')
    parser.add_argument('--archive', '-a', action='store_true',
                        help='同时归档到链接收藏')
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("B站视频内容抓取工具")
    print("=" * 60)
    print()
    
    # 创建获取器
    fetcher = BilibiliVideoFetcher()
    
    # 抓取视频
    video, error = fetcher.fetch(args.url, method=args.method)
    
    if error:
        print(f"❌ 抓取失败: {error}")
        sys.exit(1)
    
    # 格式化输出
    if args.format == 'json':
        output = json.dumps(video, ensure_ascii=False, indent=2)
    elif args.format == 'markdown':
        output = f"# {video.get('title', '无标题')}\n\n"
        output += f"![封面]({video.get('pic', '')})\n\n"
        output += f"**UP主**: [{video.get('owner', {}).get('name', '未知')}](https://space.bilibili.com/{video.get('owner', {}).get('mid', '')})\n\n"
        output += f"**发布时间**: {video.get('publish_time_formatted', '未知')}\n\n"
        output += f"**视频时长**: {format_duration(video.get('duration', 0))}\n\n"
        output += f"**播放量**: {format_number(video.get('view_count', 0))}\n\n"
        output += f"**点赞**: {format_number(video.get('like_count', 0))} | **投币**: {format_number(video.get('coin_count', 0))} | **收藏**: {format_number(video.get('favorite_count', 0))}\n\n"
        
        if video.get('tags'):
            output += f"**标签**: {', '.join(video.get('tags', []))}\n\n"
        
        output += f"**视频链接**: [{video.get('bvid', '点击观看')}]({video.get('source_url', '')})\n\n"
        output += "---\n\n"
        output += f"## 简介\n\n{video.get('description', '暂无简介')}\n\n"
        
        # 分P信息
        if video.get('pages') and len(video.get('pages', [])) > 1:
            output += "## 分P列表\n\n"
            for page in video.get('pages', []):
                output += f"- P{page.get('page', 1)}: {page.get('part', '无标题')} ({format_duration(page.get('duration', 0))})\n"
            output += "\n"
            
    else:  # txt
        output = f"标题: {video.get('title', '无标题')}\n"
        output += f"UP主: {video.get('owner', {}).get('name', '未知')}\n"
        output += f"发布时间: {video.get('publish_time_formatted', '未知')}\n"
        output += f"视频时长: {format_duration(video.get('duration', 0))}\n"
        output += f"播放量: {format_number(video.get('view_count', 0))}\n"
        output += f"点赞: {format_number(video.get('like_count', 0))}\n"
        output += f"标签: {', '.join(video.get('tags', []))}\n"
        output += f"视频链接: {video.get('source_url', '')}\n"
        output += "-" * 60 + "\n"
        output += f"简介:\n{video.get('description', '暂无简介')}\n"
    
    # 输出到文件或控制台
    if args.output:
        Path(args.output).write_text(output, encoding='utf-8')
        print(f"✅ 已保存到: {args.output}")
    else:
        print(output)
    
    # 打印统计信息
    print()
    print("📊 抓取统计:")
    print(f"   标题: {video.get('title', '无')}")
    print(f"   UP主: {video.get('owner', {}).get('name', '无')}")
    print(f"   BV号: {video.get('bvid', '无')}")
    print(f"   时长: {format_duration(video.get('duration', 0))}")
    print(f"   播放量: {format_number(video.get('view_count', 0))}")
    print(f"   标签: {', '.join(video.get('tags', [])[:5])}")
    
    # 归档到链接收藏
    if args.archive:
        print()
        print("📦 开始归档...")
        try:
            from archive_manager import LinkArchiveManager
            from classify_links import classify_link
            
            manager = LinkArchiveManager()
            
            # 分类
            url = video.get('source_url', '')
            title = video.get('title', '')
            desc = video.get('description', '')
            
            kb_key, confidence, reason = classify_link(url, title, desc)
            print(f"📊 自动分类: {kb_key} (置信度: {confidence:.2f})")
            
            # 构建摘要
            summary = f"【{video.get('owner', {}).get('name', '未知')}】{desc[:200]}..." if desc else ''
            
            # 构建来源信息
            source = f"Bilibili · {video.get('publish_time_formatted', '未知')}"
            
            # 归档
            category_map = {
                'ai-latest-news': 'bilibili-videos',
                'game-dev': 'bilibili-videos',
                'healthy-living': 'bilibili-videos',
                'link-collection': 'bilibili-videos'
            }
            category = category_map.get(kb_key, 'bilibili-videos')
            
            doc_path = manager.add_link(
                category=category,
                url=url,
                title=title,
                summary=summary,
                source=source,
                tags=['B站视频', 'bilibili'] + video.get('tags', [])[:5]
            )
            
            print(f"✅ 已归档到: {doc_path}")
            
        except Exception as e:
            print(f"❌ 归档失败: {e}")


if __name__ == "__main__":
    main()
