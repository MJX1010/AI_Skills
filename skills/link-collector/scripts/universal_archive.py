#!/usr/bin/env python3
"""
通用知识库自动归档系统
支持所有知识库的时间层级归档（年/月/周/日）和模块分类
"""

import os
import json
import argparse
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import sys

# 添加分类器路径
sys.path.insert(0, str(Path(__file__).parent))
from classify_kb import classify_content, KNOWLEDGE_BASES

# 配置
BASE_DIR = Path("/workspace/projects/workspace/memory/kb-archive")
ARCHIVE_YEARS = 1

# 知识库配置（包含space_id和本地路径）
KB_CONFIG = {
    "ai-latest-news": {
        "name": "🤖 AI最新资讯",
        "space_id": "7616519632920251572",
        "local_dir": BASE_DIR / "ai-latest-news",
        "has_time_structure": True,  # 是否需要时间层级
    },
    "game-dev": {
        "name": "🎮 游戏开发",
        "space_id": "7616735513310924004",
        "local_dir": BASE_DIR / "game-dev",
        "has_time_structure": True,
    },
    "healthy-living": {
        "name": "🌱 健康生活",
        "space_id": "7616737910330510558",
        "local_dir": BASE_DIR / "healthy-living",
        "has_time_structure": True,
    },
    "link-collection": {
        "name": "🔗 链接收藏",
        "space_id": None,
        "local_dir": Path("/workspace/projects/workspace/memory/link-collection"),
        "has_time_structure": True,
    }
}


class UniversalArchiveManager:
    """通用知识库归档管理器"""
    
    def __init__(self, kb_key: str):
        self.kb_key = kb_key
        self.kb_config = KB_CONFIG.get(kb_key)
        if not self.kb_config:
            raise ValueError(f"未知知识库: {kb_key}")
        
        self.base_dir = self.kb_config["local_dir"]
        self._ensure_structure()
    
    def _ensure_structure(self):
        """确保目录结构存在"""
        self.base_dir.mkdir(parents=True, exist_ok=True)
    
    def get_date_info(self, date: datetime = None) -> Dict:
        """获取日期层级信息"""
        if date is None:
            date = datetime.now()
        
        return {
            "year": date.year,
            "month": date.month,
            "day": date.day,
            "week": date.isocalendar()[1],
            "year_str": f"{date.year}",
            "month_str": f"{date.month:02d}",
            "day_str": f"{date.day:02d}",
            "week_str": f"week-{date.isocalendar()[1]:02d}",
            "date_str": date.strftime("%Y-%m-%d"),
            "display_date": date.strftime("%Y年%m月%d日"),
            "weekday": ["周一", "周二", "周三", "周四", "周五", "周六", "周日"][date.weekday()]
        }
    
    def get_archive_path(self, date: datetime = None, module: str = None) -> Path:
        """
        获取归档路径
        结构: kb/year/month/week/day.md
        """
        info = self.get_date_info(date)
        
        # 检查是否需要历史归档
        current_year = datetime.now().year
        if current_year - info["year"] > ARCHIVE_YEARS:
            base = self.base_dir / "archive" / info["year_str"]
        else:
            base = self.base_dir / info["year_str"] / info["month_str"] / info["week_str"]
        
        # 如果有模块，添加到路径
        if module:
            base = base / module
        
        base.mkdir(parents=True, exist_ok=True)
        return base
    
    def get_daily_doc_path(self, date: datetime = None, module: str = None) -> Path:
        """获取每日文档路径"""
        base = self.get_archive_path(date, module)
        info = self.get_date_info(date)
        return base / f"{info['date_str']}.md"
    
    def create_daily_doc(self, date: datetime = None, module: str = None) -> Path:
        """创建每日文档（如果不存在）"""
        doc_path = self.get_daily_doc_path(date, module)
        info = self.get_date_info(date)
        
        if not doc_path.exists():
            kb_name = self.kb_config["name"]
            module_name = f" - {module}" if module else ""
            
            header = f"""# {kb_name}{module_name} - {info['display_date']}

> **知识库**: {kb_name}  
> **日期**: {info['display_date']} {info['weekday']}  
> **周次**: 第{info['week']}周  
> **文档类型**: 每日归档

---

## 📋 今日内容

"""
            doc_path.write_text(header, encoding='utf-8')
            print(f"✅ 创建文档: {doc_path}")
        
        return doc_path
    
    def add_content(self, title: str, url: str, summary: str = "", 
                   source: str = "", date: datetime = None, 
                   module: str = None, tags: List[str] = None) -> Path:
        """
        添加内容到归档
        """
        if date is None:
            date = datetime.now()
        
        # 创建/获取每日文档
        doc_path = self.create_daily_doc(date, module)
        
        # 构建内容条目
        info = self.get_date_info(date)
        tags_str = ", ".join(tags) if tags else "未分类"
        module_info = f"**模块**: {module}\n\n" if module else ""
        
        entry = f"""
### [{title}]({url})

{module_info}**摘要**: {summary or '暂无摘要'}

**来源**: {source or '未知'}

**标签**: {tags_str}

**收集时间**: {datetime.now().strftime('%H:%M')}

---

"""
        
        # 追加到文档
        with open(doc_path, 'a', encoding='utf-8') as f:
            f.write(entry)
        
        print(f"✅ 已添加内容到: {doc_path}")
        return doc_path
    
    def auto_archive(self, url: str, title: str = "", content: str = "", 
                    date: datetime = None) -> Tuple[str, str, Path]:
        """
        自动分类并归档
        返回: (kb_key, module_key, doc_path)
        """
        # 1. 自动分类
        kb_key, module_key, confidence, reason = classify_content(url, title, content)
        
        if not kb_key:
            print(f"⚠️ 无法分类: {url}")
            return None, None, None
        
        # 2. 如果分类到当前知识库，直接归档
        if kb_key == self.kb_key:
            doc_path = self.add_content(
                title=title or "未命名",
                url=url,
                summary=content[:200] if content else "",
                source=source_from_url(url),
                date=date,
                module=module_key,
                tags=["自动分类", f"置信度:{confidence:.0%}"]
            )
            print(f"📦 已归档到 {self.kb_config['name']} > {module_key or '通用'}")
            return kb_key, module_key, doc_path
        else:
            # 3. 如果分类到其他知识库，创建对应管理器并归档
            other_manager = UniversalArchiveManager(kb_key)
            doc_path = other_manager.add_content(
                title=title or "未命名",
                url=url,
                summary=content[:200] if content else "",
                source=source_from_url(url),
                date=date,
                module=module_key,
                tags=["自动分类", f"置信度:{confidence:.0%}"]
            )
            print(f"📦 已归档到 {KB_CONFIG[kb_key]['name']} > {module_key or '通用'}")
            return kb_key, module_key, doc_path


def source_from_url(url: str) -> str:
    """从URL提取来源"""
    from urllib.parse import urlparse
    parsed = urlparse(url)
    domain = parsed.netloc
    if domain.startswith('www.'):
        domain = domain[4:]
    return domain


def process_url(url: str, title: str = "", content: str = ""):
    """
    处理单个URL：自动分类并归档
    """
    print(f"\n{'='*60}")
    print(f"🔗 处理链接: {url[:60]}...")
    print(f"{'='*60}")
    
    # 自动分类
    kb_key, module_key, confidence, reason = classify_content(url, title, content)
    
    if not kb_key:
        print(f"⚠️ 无法自动分类，请手动指定知识库")
        return None, None, None
    
    print(f"\n📊 分类结果:")
    print(f"   知识库: {KB_CONFIG[kb_key]['name']}")
    print(f"   模块: {module_key or '通用'}")
    print(f"   置信度: {confidence:.0%}")
    print(f"   原因: {reason}")
    
    # 创建管理器并归档
    manager = UniversalArchiveManager(kb_key)
    doc_path = manager.add_content(
        title=title or "未命名",
        url=url,
        summary=content[:300] if content else "",
        source=source_from_url(url),
        module=module_key,
        tags=["自动归档"]
    )
    
    return kb_key, module_key, doc_path


def batch_process(urls_file: str):
    """
    批量处理URL文件
    """
    with open(urls_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    results = {}
    for line in lines:
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        
        # 简单解析：URL 或 URL|标题|内容
        parts = line.split('|')
        url = parts[0]
        title = parts[1] if len(parts) > 1 else ""
        content = parts[2] if len(parts) > 2 else ""
        
        kb, module, path = process_url(url, title, content)
        
        if kb:
            if kb not in results:
                results[kb] = []
            results[kb].append({"url": url, "module": module, "path": str(path)})
    
    # 打印汇总
    print(f"\n{'='*60}")
    print("📊 批量处理完成")
    print(f"{'='*60}")
    for kb, items in results.items():
        print(f"\n{KB_CONFIG[kb]['name']}: {len(items)}篇")


def main():
    parser = argparse.ArgumentParser(description='通用知识库自动归档系统')
    parser.add_argument('--url', '-u', help='要归档的URL')
    parser.add_argument('--title', '-t', help='内容标题')
    parser.add_argument('--content', '-c', help='内容摘要')
    parser.add_argument('--kb', '-k', choices=list(KB_CONFIG.keys()),
                        help='指定知识库（不指定则自动分类）')
    parser.add_argument('--module', '-m', help='指定模块')
    parser.add_argument('--batch', '-b', help='批量处理URL文件')
    parser.add_argument('--list-kb', action='store_true', help='列出所有知识库')
    
    args = parser.parse_args()
    
    if args.list_kb:
        print("📚 支持的知识库:")
        for key, config in KB_CONFIG.items():
            print(f"  {config['icon']} {config['name']} ({key})")
        return
    
    if args.batch:
        batch_process(args.batch)
        return
    
    if args.url:
        if args.kb:
            # 指定知识库
            manager = UniversalArchiveManager(args.kb)
            doc_path = manager.add_content(
                title=args.title or "未命名",
                url=args.url,
                summary=args.content or "",
                source=source_from_url(args.url),
                module=args.module
            )
            print(f"\n✅ 已归档到: {doc_path}")
        else:
            # 自动分类
            process_url(args.url, args.title, args.content)
    else:
        print("❌ 请提供 --url 或 --batch 参数")
        parser.print_help()


if __name__ == "__main__":
    main()
