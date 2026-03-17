#!/usr/bin/env python3
"""
Game Collector Agent - 游戏内容收集器
支持自定义搜索来源和关键词
"""

import argparse
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from base import BaseCollector


class GameCollector(BaseCollector):
    """游戏内容收集器"""
    
    kb_key = "game-development"
    kb_name = "游戏开发"
    kb_icon = "🎮"
    modules = ["engine", "design", "tech", "art", "audio", "indie"]
    module_names = {
        "engine": "🎮 游戏引擎",
        "design": "🎯 游戏设计",
        "tech": "💻 开发技术",
        "art": "🎨 美术资源",
        "audio": "🎵 音频音效",
        "indie": "🏆 独立游戏"
    }
    
    def search_content(self, week_str, year, week_num):
        """搜索游戏相关内容"""
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
                            "title": f"游戏开发相关内容",
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
        """游戏内容分类"""
        title = item.get("title", "").lower()
        summary = item.get("summary", "").lower()
        text = title + " " + summary
        
        if any(kw in text for kw in ["unity", "unreal", "godot", "引擎", "engine"]):
            return "engine"
        elif any(kw in text for kw in ["设计", "机制", "玩法", "关卡", "design", "mechanic"]):
            return "design"
        elif any(kw in text for kw in ["代码", "技术", "算法", "tech", "code", "programming", "shader"]):
            return "tech"
        elif any(kw in text for kw in ["美术", "模型", "动画", "art", "model", "animation", "贴图"]):
            return "art"
        elif any(kw in text for kw in ["音效", "音乐", "音频", "audio", "sound", "music"]):
            return "audio"
        elif any(kw in text for kw in ["独立", "indie", "独立游戏", "个人开发"]):
            return "indie"
        
        return "engine"


def main():
    parser = argparse.ArgumentParser(description="Game Content Collector Agent")
    parser.add_argument("--week", default="current")
    args = parser.parse_args()
    
    collector = GameCollector()
    items = collector.collect(args.week)
    
    return 0 if items else 1


if __name__ == "__main__":
    sys.exit(main())
