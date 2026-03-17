#!/usr/bin/env python3
"""
AI Collector Agent - AI内容收集器
支持自定义搜索来源和关键词
"""

import argparse
import subprocess
import sys
import json
import re
from pathlib import Path

# 导入基类
sys.path.insert(0, str(Path(__file__).parent))
from base import BaseCollector


class AICollector(BaseCollector):
    """AI内容收集器 - 支持自定义来源"""
    
    kb_key = "ai-latest-news"
    kb_name = "AI最新资讯"
    kb_icon = "🤖"
    modules = ["news", "tools", "research", "cases"]
    module_names = {
        "news": "📰 行业资讯",
        "tools": "🛠️ 工具技巧",
        "research": "📚 深度研究",
        "cases": "💡 案例分享"
    }
    
    def search_content(self, week_str, year, week_num):
        """搜索AI相关内容"""
        content_items = []
        seen_urls = set()  # 去重
        
        # 获取权威来源
        auth_sources = self.config.get_authoritative_sources(self.kb_key)
        # 筛选国内科技媒体
        china_tech_sites = [
            "qbitai.com",      # 量子位
            "36kr.com",        # 36氪
            "huxiu.com",       # 虎嗅网
            "ifanr.com",       # 爱范儿
            "sspai.com",       # 少数派
            "zhihu.com",       # 知乎
            "jiqizhixin.com",  # 机器之心
        ]
        sites_to_search = [s for s in auth_sources if any(cs in s for cs in china_tech_sites)]
        
        print(f"  目标来源: {', '.join(sites_to_search[:5])}...")
        
        # 从指定网站搜索
        for site in sites_to_search[:5]:  # 限制前5个来源
            for query in self.search_queries[:3]:  # 限制前3个关键词
                print(f"  搜索 [{site}]: {query[:30]}...")
                
                try:
                    result = subprocess.run(
                        ["npx", "ts-node", "skills/coze-web-search/scripts/search.ts",
                         "-q", query,
                         "--time-range", self.time_range,
                         "--count", "5",
                         "--sites", site,
                         "--format", "json"],
                        capture_output=True,
                        text=True,
                        timeout=60,
                        cwd="/workspace/projects/workspace"
                    )
                    
                    if result.returncode == 0:
                        # 解析JSON结果
                        try:
                            # 找到JSON输出部分
                            json_match = re.search(r'\{.*\}', result.stdout, re.DOTALL)
                            if json_match:
                                data = json.loads(json_match.group())
                                web_items = data.get('web_items', [])
                                
                                for item in web_items:
                                    url = item.get('url', '')
                                    if url and url not in seen_urls:
                                        seen_urls.add(url)
                                        content_items.append({
                                            "title": item.get('title', '无标题'),
                                            "url": url,
                                            "source": item.get('site_name') or self._extract_domain(url),
                                            "date": item.get('publish_time', '')[:10] if item.get('publish_time') else '',
                                            "summary": item.get('snippet', '')[:200]
                                        })
                        except json.JSONDecodeError:
                            pass
                
                except Exception as e:
                    print(f"  ⚠️ 搜索失败: {e}")
        
        # 如果没有从特定来源找到内容，进行通用搜索
        if len(content_items) < 3:
            print(f"  从指定来源获取内容较少，进行通用搜索...")
            for query in self.search_queries[:2]:
                try:
                    result = subprocess.run(
                        ["npx", "ts-node", "skills/coze-web-search/scripts/search.ts",
                         "-q", query,
                         "--time-range", self.time_range,
                         "--count", "10",
                         "--format", "json"],
                        capture_output=True,
                        text=True,
                        timeout=60,
                        cwd="/workspace/projects/workspace"
                    )
                    
                    if result.returncode == 0:
                        try:
                            json_match = re.search(r'\{.*\}', result.stdout, re.DOTALL)
                            if json_match:
                                data = json.loads(json_match.group())
                                web_items = data.get('web_items', [])
                                
                                for item in web_items:
                                    url = item.get('url', '')
                                    if url and url not in seen_urls:
                                        seen_urls.add(url)
                                        content_items.append({
                                            "title": item.get('title', '无标题'),
                                            "url": url,
                                            "source": item.get('site_name') or self._extract_domain(url),
                                            "date": item.get('publish_time', '')[:10] if item.get('publish_time') else '',
                                            "summary": item.get('snippet', '')[:200]
                                        })
                        except json.JSONDecodeError:
                            pass
                        
                        if len(content_items) >= 10:  # 限制总数
                            break
                            
                except Exception as e:
                    print(f"  ⚠️ 搜索失败: {e}")
        
        if content_items:
            print(f"  ✅ 搜索到 {len(content_items)} 条内容")
            return content_items[:15]  # 限制最多15条
        
        # 如果没有搜索到任何内容，提示用户
        print("  ⚠️ 未搜索到任何内容")
        print("  💡 提示: 可以手动添加文章或检查搜索配置")
        print(f"     配置文件: skills/content-collector/config/sources.yaml")
        
        return []
    
    def _extract_domain(self, url: str) -> str:
        """从URL提取域名"""
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            domain = parsed.netloc
            if domain.startswith('www.'):
                domain = domain[4:]
            return domain
        except:
            return "未知来源"
    
    def classify_content(self, item):
        """AI内容分类"""
        title = item.get("title", "").lower()
        summary = item.get("summary", "").lower()
        text = title + " " + summary
        
        if any(kw in text for kw in ["发布", "融资", "openai", "anthropic", "google", "news", "收购", "合并", "投资"]):
            return "news"
        elif any(kw in text for kw in ["工具", "教程", "技巧", "prompt", "how to", "插件", "应用"]):
            return "tools"
        elif any(kw in text for kw in ["论文", "原理", "分析", "研究", "paper", "research", "arxiv"]):
            return "research"
        elif any(kw in text for kw in ["案例", "实践", "经验", "实战", "项目", "案例"]):
            return "cases"
        
        return "news"  # 默认


def main():
    parser = argparse.ArgumentParser(description="AI Content Collector Agent")
    parser.add_argument("--week", default="current",
                       help="目标周次")
    
    args = parser.parse_args()
    
    collector = AICollector()
    items = collector.collect(args.week)
    
    return 0 if items else 1


if __name__ == "__main__":
    sys.exit(main())
