#!/usr/bin/env python3
"""
Health Collector Agent - 健康内容收集器
支持自定义搜索来源和关键词
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
    
    def search_content(self, week_str, year, week_num):
        """搜索健康相关内容"""
        content_items = []
        seen_urls = set()
        
        print(f"  使用搜索关键词: {self.search_queries}")
        
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
                
                lines = result.stdout.split('\n')
                for line in lines:
                    line = line.strip()
                    if line.startswith('http') and line not in seen_urls:
                        seen_urls.add(line)
                        content_items.append({
                            "title": f"健康生活相关内容",
                            "url": line,
                            "source": self._extract_domain(line),
                            "date": "",
                            "summary": ""
                        })
            except Exception as e:
                print(f"  ⚠️ 搜索失败: {e}")
        
        if content_items:
            print(f"  ✅ 搜索到 {len(content_items)} 条内容")
            return content_items
        
        print("  ⚠️ 未搜索到任何内容")
        print("  💡 提示: 可以手动添加文章或检查搜索配置")
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
        """健康内容分类"""
        title = item.get("title", "").lower()
        summary = item.get("summary", "").lower()
        text = title + " " + summary
        
        if any(kw in text for kw in ["运动", "健身", "跑步", "瑜伽", "exercise", "fitness", "锻炼"]):
            return "fitness"
        elif any(kw in text for kw in ["饮食", "营养", "食谱", "减肥", "diet", "nutrition", "健康餐"]):
            return "diet"
        elif any(kw in text for kw in ["心理", "压力", "情绪", "冥想", "mental", "psychology", "焦虑"]):
            return "mental"
        elif any(kw in text for kw in ["睡眠", "失眠", "作息", "sleep", "insomnia", "早睡"]):
            return "sleep"
        elif any(kw in text for kw in ["疾病", "医疗", "预防", "medical", "disease", "健康检查", "体检"]):
            return "medical"
        elif any(kw in text for kw in ["生活", "窍门", "技巧", "妙招", "tips", "trick", "小窍门"]):
            return "tips"
        
        return "tips"


def main():
    parser = argparse.ArgumentParser(description="Health Content Collector Agent")
    parser.add_argument("--week", default="current")
    args = parser.parse_args()
    
    collector = HealthCollector()
    items = collector.collect(args.week)
    
    return 0 if items else 1


if __name__ == "__main__":
    sys.exit(main())
