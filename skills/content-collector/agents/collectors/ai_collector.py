#!/usr/bin/env python3
"""
AI Collector Agent - AI内容收集器
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
                
                # 解析搜索结果 (简化版)
                # 实际应解析 TS 输出格式
                lines = result.stdout.split('\n')
                for line in lines:
                    if line.startswith('http'):
                        # 提取URL和标题
                        content_items.append({
                            "title": f"AI相关内容 - {query[:20]}...",
                            "url": line.strip(),
                            "source": "web_search",
                            "date": "",
                            "summary": ""
                        })
            
            except Exception as e:
                print(f"  ⚠️ 搜索失败: {e}")
        
        # 如果没有搜索到，返回一些固定示例内容
        if not content_items:
            print("  ⚠️ 搜索未返回结果，使用示例数据")
            content_items = [
                {
                    "title": "大家来帮忙:30多名OpenAI、谷歌员工力挺Anthropic起诉美政府",
                    "url": "https://m.sohu.com/a/994458281_114984/",
                    "source": "手机搜狐网",
                    "date": "2026-03-10",
                    "summary": "30多名OpenAI、谷歌员工支持Anthropic就五角大楼AI合同提起的诉讼"
                },
                {
                    "title": "2026年3月AI观察:OpenAI推GPT-5.4，Google强化Gemini轻量化",
                    "url": "https://blog.csdn.net/cucibala/article/details/158836932",
                    "source": "CSDN博客",
                    "date": "2026-03-09",
                    "summary": "OpenAI推出GPT-5.4，Google强化Gemini，Anthropic押注企业级AI"
                },
                {
                    "title": "Claude日注册量破百万，应用商店反超ChatGPT",
                    "url": "https://cj.sina.com.cn/article/norm_detail",
                    "source": "新浪财经",
                    "date": "2026-03-07",
                    "summary": "Claude日注册量突破百万，在应用商店排名反超ChatGPT"
                }
            ]
        
        return content_items
    
    def classify_content(self, item):
        """AI内容分类"""
        title = item.get("title", "").lower()
        
        if any(kw in title for kw in ["发布", "融资", "openai", "anthropic", "google", "news"]):
            return "news"
        elif any(kw in title for kw in ["工具", "教程", "技巧", "prompt"]):
            return "tools"
        elif any(kw in title for kw in ["论文", "原理", "分析", "研究"]):
            return "research"
        elif any(kw in title for kw in ["案例", "实践", "经验"]):
            return "cases"
        
        return "news"  # 默认


def main():
    parser = argparse.ArgumentParser(description="AI Content Collector Agent")
    parser.add_argument("--week", default="current",
                       help="目标周次")
    
    args = parser.parse_args()
    
    collector = AICollector()
    collector.collect(args.week)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
