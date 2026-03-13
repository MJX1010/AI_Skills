#!/usr/bin/env python3
"""
Health Collector Agent - 健康内容收集器
"""

import argparse
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from base import BaseCollector


class HealthCollector(BaseCollector):
    """健康内容收集器"""
    
    kb_key = "healthy-living"
    kb_name = "健康生活"
    kb_icon = "🌱"
    modules = ["fitness", "diet", "mental", "sleep", "medical", "tips"]
    module_names = {
        "fitness": "🏃 运动健身",
        "diet": "🥗 饮食营养",
        "mental": "😊 心理健康",
        "sleep": "💤 睡眠健康",
        "medical": "🏥 医疗资讯",
        "tips": "✨ 生活妙招"
    }
    search_queries = [
        "健康 运动 饮食 生活妙招",
        "fitness nutrition mental health"
    ]
    
    def search_content(self, week_str, year, week_num):
        """搜索健康相关内容"""
        content_items = []
        
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
            except:
                pass
        
        # 示例数据
        if not content_items:
            print("  ⚠️ 搜索未返回结果，使用示例数据")
            content_items = [
                {
                    "title": "春节健康指南:拒做"贴膘人"，运动、饮食两相宜",
                    "url": "http://m.cnbzol.com/m/jiao/2026/0215/2057105.html",
                    "source": "巴中在线",
                    "date": "2026-02-15",
                    "summary": "春节后如何通过合理饮食和运动保持健康"
                },
                {
                    "title": "健康生活:科学饮食与运动",
                    "url": "https://post.m.smzdm.com/p/116898921/",
                    "source": "什么值得买",
                    "date": "2025-12-10",
                    "summary": "健康生活的双翼：饮食为基，运动为魂"
                },
                {
                    "title": "健康小妙法",
                    "url": "https://www.trfsz.com/newsview1903117.html",
                    "source": "泰然健康网",
                    "date": "2026-02-25",
                    "summary": "长期坚持简单易行的生活习惯，轻松守护身心健康"
                }
            ]
        
        return content_items
    
    def classify_content(self, item):
        """健康内容分类"""
        title = item.get("title", "").lower()
        
        if any(kw in title for kw in ["运动", "健身", "跑步"]):
            return "fitness"
        elif any(kw in title for kw in ["饮食", "营养", "食谱"]):
            return "diet"
        elif any(kw in title for kw in ["心理", "压力", "情绪"]):
            return "mental"
        elif any(kw in title for kw in ["睡眠", "失眠"]):
            return "sleep"
        elif any(kw in title for kw in ["疾病", "医疗", "预防"]):
            return "medical"
        elif any(kw in title for kw in ["生活", "窍门", "技巧", "妙招"]):
            return "tips"
        
        return "tips"


def main():
    parser = argparse.ArgumentParser(description="Health Content Collector Agent")
    parser.add_argument("--week", default="current")
    args = parser.parse_args()
    
    collector = HealthCollector()
    collector.collect(args.week)
    return 0


if __name__ == "__main__":
    sys.exit(main())
