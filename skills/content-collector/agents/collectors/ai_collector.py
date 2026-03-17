#!/usr/bin/env python3
"""
AI Collector Agent - AI内容收集器
支持自定义搜索来源和关键词
"""

import argparse
import subprocess
import sys
import json
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
        
        print(f"  使用搜索关键词: {self.search_queries}")
        
        # 使用 coze-web-search 搜索
        for query in self.search_queries:
            print(f"  搜索: {query}")
            
            try:
                result = subprocess.run(
                    ["npx", "ts-node", "skills/coze-web-search/scripts/search.ts",
                     "-q", query, "--time-range", "1w", "--count", "10"],
                    capture_output=True,
                    text=True,
                    timeout=60,
                    cwd="/workspace/projects/workspace"
                )
                
                # 解析搜索结果
                # 尝试解析输出中的URL和标题
                lines = result.stdout.split('\n')
                for line in lines:
                    line = line.strip()
                    if line.startswith('http') and line not in seen_urls:
                        seen_urls.add(line)
                        content_items.append({
                            "title": f"AI相关内容",
                            "url": line,
                            "source": self._extract_domain(line),
                            "date": "",
                            "summary": ""
                        })
            
            except Exception as e:
                print(f"  ⚠️ 搜索失败: {e}")
        
        # 尝试从RSS获取内容（如果有配置）
        rss_feeds = self.config.get_rss_feeds(self.kb_key)
        if rss_feeds:
            print(f"  从 {len(rss_feeds)} 个RSS源获取内容...")
            # TODO: 实现RSS解析
        
        if content_items:
            print(f"  ✅ 搜索到 {len(content_items)} 条内容")
            return content_items
        
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
