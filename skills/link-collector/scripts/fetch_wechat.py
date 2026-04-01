#!/usr/bin/env python3
"""
微信文章抓取脚本
支持多种方式获取微信公众号文章内容
"""

import argparse
import json
import re
import sys
import time
from pathlib import Path
from urllib.parse import urlparse, unquote

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


class WechatArticleFetcher:
    """微信文章获取器"""
    
    def __init__(self):
        self.session = None
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
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
    
    def extract_url_from_text(self, text):
        """从文本中提取微信文章URL"""
        # 匹配 mp.weixin.qq.com 的链接
        pattern = r'https?://mp\.weixin\.qq\.com/s/[a-zA-Z0-9_-]+'
        matches = re.findall(pattern, text)
        return matches[0] if matches else None
    
    def fetch_with_requests(self, url, timeout=30):
        """
        使用 requests 获取文章内容
        适用于简单的反爬场景
        """
        if not HAS_REQUESTS:
            return None, "requests 未安装"
        
        try:
            print(f"[方法1] 使用 requests 抓取: {url[:50]}...")
            response = self.session.get(url, timeout=timeout, allow_redirects=True)
            response.raise_for_status()
            
            # 检查是否被拦截
            if 'antispam' in response.text or '访问频繁' in response.text:
                return None, "被反爬虫拦截"
            
            return response.text, None
            
        except Exception as e:
            return None, f"requests 抓取失败: {str(e)}"
    
    def fetch_with_playwright(self, url, timeout=60):
        """
        使用 Playwright 渲染页面获取内容
        适用于复杂的反爬场景
        """
        if not HAS_PLAYWRIGHT:
            return None, "playwright 未安装，请运行: pip install playwright && playwright install"
        
        try:
            print(f"[方法2] 使用 Playwright 渲染: {url[:50]}...")
            
            with sync_playwright() as p:
                # 启动浏览器
                browser = p.chromium.launch(headless=True)
                context = browser.new_context(
                    user_agent=self.headers['User-Agent'],
                    viewport={'width': 1920, 'height': 1080}
                )
                
                # 设置请求头
                context.set_extra_http_headers({
                    'Accept-Language': 'zh-CN,zh;q=0.9'
                })
                
                page = context.new_page()
                
                # 拦截图片和CSS，加快加载
                page.route("**/*.{png,jpg,jpeg,gif,css,woff,woff2}", lambda route: route.abort())
                
                # 访问页面
                page.goto(url, wait_until='networkidle', timeout=timeout*1000)
                
                # 等待文章加载
                page.wait_for_selector('#js_content, #activity_name', timeout=10000)
                
                # 等待一下，确保JS渲染完成
                time.sleep(2)
                
                # 获取HTML内容
                html = page.content()
                
                browser.close()
                return html, None
                
        except Exception as e:
            return None, f"Playwright 渲染失败: {str(e)}"
    
    def parse_article(self, html):
        """
        解析微信文章HTML，提取关键信息
        """
        if not HAS_BS4:
            return self._parse_with_regex(html)
        
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            # 提取标题
            title = ""
            title_selectors = ['#activity_name', 'h1.rich_media_title', '.rich_media_title', 'h1']
            for selector in title_selectors:
                title_elem = soup.select_one(selector)
                if title_elem:
                    title = title_elem.get_text(strip=True)
                    break
            
            # 提取公众号名称
            author = ""
            author_selectors = ['#js_name', '.profile_nickname', '.rich_media_meta_nickname']
            for selector in author_selectors:
                author_elem = soup.select_one(selector)
                if author_elem:
                    author = author_elem.get_text(strip=True)
                    break
            
            # 提取发布时间
            publish_time = ""
            time_selectors = ['#publish_time', '.rich_media_meta_text', '#js_publish_time']
            for selector in time_selectors:
                time_elem = soup.select_one(selector)
                if time_elem:
                    publish_time = time_elem.get_text(strip=True)
                    break
            
            # 提取正文内容
            content = ""
            content_selectors = ['#js_content', '.rich_media_content']
            for selector in content_selectors:
                content_elem = soup.select_one(selector)
                if content_elem:
                    # 移除 script 和 style
                    for script in content_elem.find_all(['script', 'style']):
                        script.decompose()
                    content = content_elem.get_text(separator='\n', strip=True)
                    break
            
            # 提取图片
            images = []
            img_selectors = ['#js_content img', '.rich_media_content img']
            for selector in img_selectors:
                img_elems = soup.select(selector)
                for img in img_elems:
                    src = img.get('data-src') or img.get('src')
                    if src:
                        images.append(src)
            
            # 提取原文链接（处理重定向）
            original_url = ""
            url_elem = soup.select_one('#js_share_source')
            if url_elem:
                original_url = url_elem.get('href', '')
            
            return {
                'title': title,
                'author': author,
                'publish_time': publish_time,
                'content': content[:5000],  # 限制长度
                'content_length': len(content),
                'images': images[:10],  # 限制图片数量
                'url': original_url
            }
            
        except Exception as e:
            return {'error': f'解析失败: {str(e)}'}
    
    def _parse_with_regex(self, html):
        """
        使用正则表达式解析（备用方案）
        """
        try:
            # 提取标题
            title_match = re.search(r'<h1[^>]*class="[^"]*rich_media_title[^"]*"[^>]*>(.*?)</h1>', html, re.DOTALL)
            title = re.sub(r'<[^>]+>', '', title_match.group(1)).strip() if title_match else ""
            
            # 提取内容
            content_match = re.search(r'<div[^>]*id="js_content"[^>]*>(.*?)</div>', html, re.DOTALL)
            content = re.sub(r'<[^>]+>', ' ', content_match.group(1)).strip() if content_match else ""
            
            return {
                'title': title,
                'author': "",
                'publish_time': "",
                'content': content[:5000],
                'content_length': len(content),
                'images': [],
                'url': ""
            }
        except Exception as e:
            return {'error': f'正则解析失败: {str(e)}'}
    
    def fetch(self, url, method='auto'):
        """
        抓取微信文章的主函数
        
        Args:
            url: 微信文章URL
            method: 抓取方法 ('requests', 'playwright', 'auto')
        
        Returns:
            (article_data, error_message)
        """
        # 验证URL
        if not url.startswith('http'):
            url = 'https://' + url
        
        if 'mp.weixin.qq.com' not in url:
            return None, "不是有效的微信文章链接"
        
        html = None
        error = None
        
        # 根据方法选择抓取方式
        if method == 'requests':
            html, error = self.fetch_with_requests(url)
        elif method == 'playwright':
            html, error = self.fetch_with_playwright(url)
        else:  # auto
            # 先尝试 requests
            html, error = self.fetch_with_requests(url)
            
            # 如果失败，尝试 playwright
            if not html and HAS_PLAYWRIGHT:
                print(f"requests 失败，尝试 Playwright...")
                html, error = self.fetch_with_playwright(url)
        
        if not html:
            return None, error or "所有抓取方法均失败"
        
        # 解析文章内容
        article = self.parse_article(html)
        article['source_url'] = url
        
        return article, None


def main():
    parser = argparse.ArgumentParser(description='微信文章抓取工具')
    parser.add_argument('url', help='微信文章URL')
    parser.add_argument('--method', '-m', default='auto', 
                        choices=['requests', 'playwright', 'auto'],
                        help='抓取方法 (默认: auto)')
    parser.add_argument('--output', '-o', help='输出文件路径')
    parser.add_argument('--format', '-f', default='json', 
                        choices=['json', 'markdown', 'txt'],
                        help='输出格式 (默认: json)')
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("微信文章抓取工具")
    print("=" * 60)
    print()
    
    # 创建获取器
    fetcher = WechatArticleFetcher()
    
    # 抓取文章
    article, error = fetcher.fetch(args.url, method=args.method)
    
    if error:
        print(f"❌ 抓取失败: {error}")
        sys.exit(1)
    
    # 格式化输出
    if args.format == 'json':
        output = json.dumps(article, ensure_ascii=False, indent=2)
    elif args.format == 'markdown':
        output = f"# {article.get('title', '无标题')}\n\n"
        output += f"**公众号**: {article.get('author', '未知')}\n\n"
        output += f"**发布时间**: {article.get('publish_time', '未知')}\n\n"
        output += f"**原文链接**: {article.get('source_url', '')}\n\n"
        output += "---\n\n"
        output += article.get('content', '')
    else:  # txt
        output = f"标题: {article.get('title', '无标题')}\n"
        output += f"公众号: {article.get('author', '未知')}\n"
        output += f"发布时间: {article.get('publish_time', '未知')}\n"
        output += f"原文链接: {article.get('source_url', '')}\n"
        output += "-" * 60 + "\n"
        output += article.get('content', '')
    
    # 输出到文件或控制台
    if args.output:
        Path(args.output).write_text(output, encoding='utf-8')
        print(f"✅ 已保存到: {args.output}")
    else:
        print(output)
    
    # 打印统计信息
    print()
    print("📊 抓取统计:")
    print(f"   标题: {article.get('title', '无')}")
    print(f"   公众号: {article.get('author', '无')}")
    print(f"   内容长度: {article.get('content_length', 0)} 字符")
    print(f"   图片数量: {len(article.get('images', []))}")


if __name__ == "__main__":
    main()
