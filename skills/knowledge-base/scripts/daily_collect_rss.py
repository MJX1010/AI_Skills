#!/usr/bin/env python3
"""
RSS 采集脚本 - 替代 coze-web-search
从配置的 RSS 源采集文章，支持多线程并行
"""

import argparse
import json
import re
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta
from pathlib import Path
from urllib.parse import urlparse

import feedparser
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# 配置
WORKSPACE = Path("/workspace/projects/workspace")
MEMORY_DIR = WORKSPACE / "memory"
STATE_DIR = MEMORY_DIR / "state"
CONFIG_FILE = WORKSPACE / "config" / "content_sources.yaml"
COLLECTED_URLS_FILE = STATE_DIR / "collected-urls.json"

# 知识库配置
KB_CONFIG = {
    "ai-latest-news": {
        "name": "🤖 AI最新资讯",
        "space_id": "7616519632920251572",
        "keywords": ["ai", "人工智能", "gpt", "claude", "openai", "anthropic", "llm", "大模型", "机器学习"]
    },
    "game-development": {
        "name": "🎮 游戏开发",
        "space_id": "7616735513310924004",
        "keywords": ["game", "游戏", "unity", "unreal", "godot", "indie", "gamedev"]
    },
    "healthy-living": {
        "name": "🌱 健康生活",
        "space_id": "7616737910330510558",
        "keywords": ["健康", "health", "健身", "运动", "饮食", "心理", "生活"]
    }
}

# RSS 源配置（硬编码，作为 content_sources.yaml 的备选）
RSS_SOURCES = {
    "ai-latest-news": [
        {"name": "机器之心", "url": "https://www.jiqizhixin.com/rss"},
        {"name": "量子位", "url": "https://www.qbitai.com/rss"},
    ],
    "game-development": [
        {"name": "Godot News", "url": "https://godotengine.org/news"},
    ],
    "healthy-living": [
        {"name": "丁香医生", "url": "https://dxy.com/rss"},
    ]
}


class RSSCollector:
    """RSS 采集器"""
    
    def __init__(self, days: int = 2):
        self.days = days
        self.session = requests.Session()
        retry_strategy = Retry(total=3, backoff_factor=1)
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
    def fetch_feed(self, source: dict) -> list:
        """获取单个 RSS 源"""
        articles = []
        try:
            print(f"  📡 采集: {source['name']}")
            
            # 使用 requests 获取内容（支持超时）
            response = self.session.get(
                source['url'], 
                headers=self.headers, 
                timeout=30
            )
            response.raise_for_status()
            
            # 解析 RSS 内容
            feed = feedparser.parse(response.content)
            
            if feed.bozo:
                print(f"    ⚠️ 警告: {feed.bozo_exception}")
            
            cutoff_date = datetime.now() - timedelta(days=self.days)
            
            for entry in feed.entries[:20]:  # 只取最近20条
                # 解析发布时间
                published = self._parse_date(entry)
                if not published:
                    continue
                
                # 只收集最近 N 天的内容
                if published < cutoff_date:
                    continue
                
                article = {
                    "id": self._generate_id(entry.get('link', '')),
                    "title": entry.get('title', '无标题'),
                    "url": entry.get('link', ''),
                    "source_name": source['name'],
                    "published_at": published.isoformat(),
                    "summary": entry.get('summary', entry.get('description', ''))[:500],
                    "collected_at": datetime.now().isoformat()
                }
                articles.append(article)
            
            print(f"    ✅ 获取 {len(articles)} 篇文章")
            
        except Exception as e:
            print(f"    ❌ 采集失败: {e}")
        
        return articles
    
    def _parse_date(self, entry) -> datetime:
        """解析发布时间"""
        date_fields = ['published_parsed', 'updated_parsed', 'created_parsed']
        
        for field in date_fields:
            if hasattr(entry, field) and getattr(entry, field):
                try:
                    t = getattr(entry, field)
                    return datetime(*t[:6])
                except:
                    continue
        
        # 备选：从字符串解析
        date_strings = ['published', 'updated', 'created', 'date']
        for field in date_strings:
            if hasattr(entry, field):
                try:
                    return datetime.fromisoformat(getattr(entry, field).replace('Z', '+00:00'))
                except:
                    continue
        
        # 默认返回当前时间（不过滤）
        return datetime.now()
    
    def _generate_id(self, url: str) -> str:
        """生成文章唯一 ID"""
        import hashlib
        return hashlib.sha256(url.encode()).hexdigest()[:16]
    
    def collect_all(self, kb_key: str = None) -> dict:
        """并行采集所有 RSS 源"""
        print(f"\n🚀 开始 RSS 采集 (最近 {self.days} 天)")
        print("="*60)
        
        all_articles = []
        sources = []
        
        # 选择数据源
        if kb_key and kb_key in RSS_SOURCES:
            sources = RSS_SOURCES[kb_key]
        else:
            for kb_sources in RSS_SOURCES.values():
                sources.extend(kb_sources)
        
        # 并行采集
        with ThreadPoolExecutor(max_workers=5) as executor:
            future_to_source = {
                executor.submit(self.fetch_feed, source): source 
                for source in sources
            }
            
            for future in as_completed(future_to_source):
                articles = future.result()
                all_articles.extend(articles)
        
        print("="*60)
        print(f"✅ 采集完成: 共 {len(all_articles)} 篇文章")
        
        return {
            "collection_time": datetime.now().isoformat(),
            "source": "rss",
            "days": self.days,
            "articles": all_articles
        }


class ContentClassifier:
    """内容分类器"""
    
    @staticmethod
    def classify(title: str, summary: str) -> tuple:
        """分类到知识库和模块"""
        text = (title + " " + summary).lower()
        
        # AI 关键词
        ai_keywords = ["ai", "人工智能", "gpt", "claude", "openai", "anthropic", "llm", "大模型", "深度学习", "神经网络"]
        if any(kw in text for kw in ai_keywords):
            kb = "ai-latest-news"
            if any(kw in text for kw in ["工具", "tool", "技巧", "教程", "tutorial"]):
                module = "tools"
            elif any(kw in text for kw in ["论文", "paper", "研究", "research", "学术"]):
                module = "research"
            elif any(kw in text for kw in ["案例", "case", "实践", "实战", "应用"]):
                module = "cases"
            else:
                module = "news"
            return kb, module
        
        # 游戏关键词
        game_keywords = ["game", "游戏", "unity", "unreal", "godot", "indie", "gamedev", "引擎"]
        if any(kw in text for kw in game_keywords):
            kb = "game-development"
            if any(kw in text for kw in ["unity", "unreal", "godot", "引擎"]):
                module = "engine"
            elif any(kw in text for kw in ["设计", "design", "策划"]):
                module = "design"
            elif any(kw in text for kw in ["美术", "art", "模型", "动画", "渲染"]):
                module = "art"
            elif any(kw in text for kw in ["indie", "独立", "个人开发"]):
                module = "indie"
            else:
                module = "tech"
            return kb, module
        
        # 健康关键词
        health_keywords = ["健康", "health", "健身", "运动", "饮食", "心理", "营养"]
        if any(kw in text for kw in health_keywords):
            kb = "healthy-living"
            if any(kw in text for kw in ["运动", "健身", "fitness", "跑步", "训练"]):
                module = "fitness"
            elif any(kw in text for kw in ["饮食", "营养", "diet", "食谱", "吃"]):
                module = "nutrition"
            elif any(kw in text for kw in ["心理", "压力", "情绪", "mental", "psychology"]):
                module = "mental"
            else:
                module = "lifestyle"
            return kb, module
        
        # 默认
        return "ai-latest-news", "news"


class ArchiveManager:
    """归档管理器"""
    
    def __init__(self):
        self.state_file = COLLECTED_URLS_FILE
        STATE_DIR.mkdir(parents=True, exist_ok=True)
    
    def load_collected(self) -> set:
        """加载已收集的 URL"""
        if self.state_file.exists():
            data = json.loads(self.state_file.read_text())
            return set(data.get("urls", {}).keys())
        return set()
    
    def save_collected(self, articles: list):
        """保存已收集的文章"""
        data = {"urls": {}}
        
        if self.state_file.exists():
            data = json.loads(self.state_file.read_text())
        
        for article in articles:
            data["urls"][article["url"]] = {
                "first_collected": datetime.now().isoformat(),
                "kb": article.get("kb", "unknown"),
                "title": article["title"]
            }
        
        self.state_file.write_text(json.dumps(data, indent=2, ensure_ascii=False))
    
    def archive_to_kb(self, articles: list) -> dict:
        """归档到知识库"""
        date_str = datetime.now().strftime("%Y-%m-%d")
        year = date_str[:4]
        month = date_str[5:7]
        day = date_str[8:10]
        
        results = {}
        
        for article in articles:
            kb = article.get("kb", "link-collection")
            
            if kb in KB_CONFIG:
                kb_dir = MEMORY_DIR / "kb-archive" / kb / year / month
                kb_name = KB_CONFIG[kb]["name"]
            else:
                kb_dir = MEMORY_DIR / "link-collection" / year / month
                kb_name = "🔗 本地链接收藏"
            
            kb_dir.mkdir(parents=True, exist_ok=True)
            file_path = kb_dir / f"{day}.md"
            
            # 构建条目
            entry = f"""
### [{article['title']}]({article['url']})
> 来源: {article.get('source_name', 'RSS')} | 模块: {article.get('module', 'news')} | 收集时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}

{article.get('summary', '')[:200]}...

---
"""
            
            if file_path.exists():
                with open(file_path, "a", encoding="utf-8") as f:
                    f.write(entry)
            else:
                header = f"# {kb_name} - {date_str} 日报\n\n"
                file_path.write_text(header + entry, encoding="utf-8")
            
            results[article["url"]] = str(file_path)
        
        return results


def main():
    parser = argparse.ArgumentParser(description="RSS 采集脚本")
    parser.add_argument("--days", "-d", type=int, default=2, help="采集最近N天的内容")
    parser.add_argument("--kb", "-k", choices=["ai-latest-news", "game-development", "healthy-living"],
                       help="指定知识库")
    parser.add_argument("--archive", "-a", action="store_true", help="归档到知识库")
    parser.add_argument("--output", "-o", help="输出JSON文件路径")
    
    args = parser.parse_args()
    
    print("\n" + "="*60)
    print("📡 RSS 采集器 v1.0")
    print("="*60)
    
    # 采集
    collector = RSSCollector(days=args.days)
    raw_data = collector.collect_all(kb_key=args.kb)
    
    if not raw_data["articles"]:
        print("\n⚠️ 未采集到任何文章")
        return 1
    
    # 去重
    archive_manager = ArchiveManager()
    collected_urls = archive_manager.load_collected()
    new_articles = [a for a in raw_data["articles"] if a["url"] not in collected_urls]
    
    print(f"\n📝 新文章: {len(new_articles)} / {len(raw_data['articles'])}")
    
    if not new_articles:
        print("✅ 所有文章都已收集过")
        return 0
    
    # 分类
    print("\n📂 正在分类...")
    for article in new_articles:
        kb, module = ContentClassifier.classify(article["title"], article["summary"])
        article["kb"] = kb
        article["module"] = module
        print(f"  [{kb.split('-')[0]}] {article['title'][:50]}...")
    
    # 归档
    if args.archive:
        print("\n💾 正在归档...")
        results = archive_manager.archive_to_kb(new_articles)
        archive_manager.save_collected(new_articles)
        
        for url, path in results.items():
            print(f"  ✅ {path}")
    
    # 输出JSON
    if args.output:
        output_path = Path(args.output)
        output_path.write_text(json.dumps(new_articles, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"\n📄 已保存到: {args.output}")
    
    print("\n" + "="*60)
    print("✅ RSS 采集完成!")
    print("="*60 + "\n")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
