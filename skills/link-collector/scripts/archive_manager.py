#!/usr/bin/env python3
"""
链接归档管理器
按层级结构管理链接：年/月/周/日
支持用户链接、自动收集链接、微信文章分类存储
"""

import os
import json
import argparse
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# 基础配置
BASE_DIR = Path("/workspace/projects/workspace/memory/link-collection")
ARCHIVE_YEARS = 1  # 超过1年归档到历史库

class LinkArchiveManager:
    """链接归档管理器"""
    
    def __init__(self):
        self.base_dir = BASE_DIR
        self.categories = {
            "user-links": "用户发送的链接",
            "self-collected": "自动收集的链接", 
            "wechat-articles": "微信文章"
        }
        self._ensure_structure()
    
    def _ensure_structure(self):
        """确保目录结构存在"""
        for category in self.categories.keys():
            (self.base_dir / category).mkdir(parents=True, exist_ok=True)
    
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
            "display_date": date.strftime("%Y年%m月%d日")
        }
    
    def get_archive_path(self, category: str, date: datetime = None) -> Path:
        """
        获取归档路径
        结构: category/year/month/week/day.md
        """
        info = self.get_date_info(date)
        
        # 检查是否需要历史归档（超过1年）
        current_year = datetime.now().year
        if current_year - info["year"] > ARCHIVE_YEARS:
            base = self.base_dir / category / "archive" / info["year_str"]
        else:
            base = self.base_dir / category / info["year_str"] / info["month_str"] / info["week_str"]
        
        base.mkdir(parents=True, exist_ok=True)
        return base
    
    def get_daily_doc_path(self, category: str, date: datetime = None) -> Path:
        """获取每日文档路径"""
        base = self.get_archive_path(category, date)
        info = self.get_date_info(date)
        return base / f"{info['date_str']}.md"
    
    def create_daily_doc(self, category: str, date: datetime = None) -> Path:
        """创建每日文档（如果不存在）"""
        doc_path = self.get_daily_doc_path(category, date)
        info = self.get_date_info(date)
        
        if not doc_path.exists():
            # 创建文档头部
            category_name = self.categories.get(category, category)
            header = f"""# {category_name} - {info['display_date']}

> **分类**: {category_name}  
> **日期**: {info['display_date']}  
> **周次**: 第{info['week']}周  
> **文档类型**: 每日归档

---

## 📋 今日收集

"""
            doc_path.write_text(header, encoding='utf-8')
            print(f"✅ 创建文档: {doc_path}")
        
        return doc_path
    
    def add_link(self, category: str, url: str, title: str = "", 
                 summary: str = "", source: str = "", date: datetime = None,
                 tags: List[str] = None) -> Path:
        """
        添加链接到归档
        
        Args:
            category: 分类 (user-links/self-collected/wechat-articles)
            url: 链接URL
            title: 标题
            summary: 摘要
            source: 来源
            date: 日期（默认今天）
            tags: 标签列表
        """
        if date is None:
            date = datetime.now()
        
        # 确保分类有效
        if category not in self.categories:
            category = "self-collected"
        
        # 创建/获取每日文档
        doc_path = self.create_daily_doc(category, date)
        
        # 构建链接条目
        info = self.get_date_info(date)
        tags_str = ", ".join(tags) if tags else "未分类"
        
        entry = f"""
### [{title or '无标题'}]({url})

**摘要**: {summary or '暂无摘要'}

**来源**: {source or '未知'}

**标签**: {tags_str}

**收集时间**: {datetime.now().strftime('%H:%M')}

---

"""
        
        # 追加到文档
        with open(doc_path, 'a', encoding='utf-8') as f:
            f.write(entry)
        
        print(f"✅ 已添加链接到: {doc_path}")
        return doc_path
    
    def get_week_summary(self, category: str, week_date: datetime = None) -> Path:
        """生成周汇总文档"""
        if week_date is None:
            week_date = datetime.now()
        
        info = self.get_date_info(week_date)
        
        # 周汇总路径
        base = self.base_dir / category / info["year_str"] / info["month_str"] / info["week_str"]
        summary_path = base / f"week-summary-{info['week_str']}.md"
        
        # 收集本周所有日期的链接
        week_links = []
        for day_file in sorted(base.glob("2026-*.md")):
            if "week-summary" not in day_file.name:
                content = day_file.read_text(encoding='utf-8')
                week_links.append({
                    "date": day_file.stem,
                    "content": content
                })
        
        # 生成周汇总
        category_name = self.categories.get(category, category)
        summary = f"""# {category_name} - 第{info['week']}周汇总

> **分类**: {category_name}  
> **周次**: 第{info['week']}周  
> **时间范围**: {info['year_str']}年{info['month_str']}月  
> **文档类型**: 周汇总

---

## 📊 本周统计

- **总链接数**: {len(week_links)} 天有更新
- **分类**: {category_name}

---

## 📅 每日详情

"""
        
        for link in week_links:
            summary += f"### {link['date']}\n\n"
            # 提取链接部分（简化处理）
            summary += f"[查看当日详情](./{link['date']}.md)\n\n"
        
        summary_path.write_text(summary, encoding='utf-8')
        print(f"✅ 生成周汇总: {summary_path}")
        return summary_path
    
    def get_month_index(self, category: str, month_date: datetime = None) -> Path:
        """生成月索引文档"""
        if month_date is None:
            month_date = datetime.now()
        
        info = self.get_date_info(month_date)
        
        # 月索引路径
        base = self.base_dir / category / info["year_str"] / info["month_str"]
        index_path = base / f"month-index-{info['month_str']}.md"
        
        # 收集本月所有周
        weeks = sorted([d for d in base.iterdir() if d.is_dir() and d.name.startswith("week-")])
        
        category_name = self.categories.get(category, category)
        index = f"""# {category_name} - {info['year_str']}年{info['month_str']}月索引

> **分类**: {category_name}  
> **年份**: {info['year_str']}年  
> **月份**: {info['month_str']}月  
> **文档类型**: 月索引

---

## 📅 本月周次

"""
        
        for week_dir in weeks:
            week_num = week_dir.name.replace("week-", "")
            index += f"- [第{week_num}周](./{week_dir.name}/week-summary-week-{week_num}.md)\n"
        
        index += """
---

## 📈 月度统计

- **总周数**: {} 周
- **分类**: {}

""".format(len(weeks), category_name)
        
        index_path.write_text(index, encoding='utf-8')
        print(f"✅ 生成月索引: {index_path}")
        return index_path
    
    def archive_old_content(self):
        """归档超过1年的内容"""
        current_year = datetime.now().year
        
        for category in self.categories.keys():
            category_dir = self.base_dir / category
            if not category_dir.exists():
                continue
            
            for year_dir in category_dir.iterdir():
                if not year_dir.is_dir():
                    continue
                
                try:
                    year = int(year_dir.name)
                    if current_year - year > ARCHIVE_YEARS:
                        # 移动到归档目录
                        archive_dir = category_dir / "archive" / year_dir.name
                        archive_dir.parent.mkdir(parents=True, exist_ok=True)
                        year_dir.rename(archive_dir)
                        print(f"📦 归档: {year_dir} -> {archive_dir}")
                except ValueError:
                    continue
    
    def get_full_structure(self) -> Dict:
        """获取完整目录结构"""
        structure = {}
        
        for category in self.categories.keys():
            structure[category] = {}
            category_dir = self.base_dir / category
            
            if not category_dir.exists():
                continue
            
            for year_dir in category_dir.iterdir():
                if not year_dir.is_dir() or year_dir.name == "archive":
                    continue
                
                year = year_dir.name
                structure[category][year] = {}
                
                for month_dir in year_dir.iterdir():
                    if not month_dir.is_dir():
                        continue
                    
                    month = month_dir.name
                    weeks = [d.name for d in month_dir.iterdir() if d.is_dir() and d.name.startswith("week-")]
                    structure[category][year][month] = weeks
        
        return structure

def main():
    parser = argparse.ArgumentParser(description='链接归档管理器')
    parser.add_argument('--action', '-a', choices=['add', 'week-summary', 'month-index', 'archive', 'structure'], 
                        default='structure', help='操作类型')
    parser.add_argument('--category', '-c', choices=['user-links', 'self-collected', 'wechat-articles'],
                        default='user-links', help='链接分类')
    parser.add_argument('--url', '-u', help='链接URL')
    parser.add_argument('--title', '-t', help='链接标题')
    parser.add_argument('--summary', '-s', help='链接摘要')
    parser.add_argument('--source', '-src', help='链接来源')
    
    args = parser.parse_args()
    
    manager = LinkArchiveManager()
    
    if args.action == 'add':
        if not args.url:
            print("❌ 请提供 --url 参数")
            return
        manager.add_link(
            category=args.category,
            url=args.url,
            title=args.title or "",
            summary=args.summary or "",
            source=args.source or ""
        )
    
    elif args.action == 'week-summary':
        manager.get_week_summary(args.category)
    
    elif args.action == 'month-index':
        manager.get_month_index(args.category)
    
    elif args.action == 'archive':
        manager.archive_old_content()
    
    elif args.action == 'structure':
        structure = manager.get_full_structure()
        print(json.dumps(structure, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
