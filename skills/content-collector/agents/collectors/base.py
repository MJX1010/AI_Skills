#!/usr/bin/env python3
"""
Base Collector - 收集器基类
"""

import sys
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from pathlib import Path
import json

# 导入配置管理器
sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.config import get_config


class BaseCollector(ABC):
    """收集器基类"""
    
    # 子类必须定义
    kb_key = None
    kb_name = None
    kb_icon = None
    modules = []
    
    def __init__(self):
        self.base_path = Path("/workspace/projects/workspace")
        self.results = []
        self.config = get_config()
        
        # 从配置加载搜索关键词和时间范围
        self.search_queries = self.config.get_search_queries(self.kb_key)
        self.time_range = self.config.get_setting("search.time_range", "1d")
    
    def get_week_info(self, week_arg):
        """获取周信息"""
        if week_arg == "current":
            today = datetime.now()
            year = today.year
            week_num = int(today.strftime("%W")) + 1
            return f"{year}-W{week_num:02d}", year, week_num
        else:
            parts = week_arg.split("-W")
            year = int(parts[0])
            week_num = int(parts[1])
            return week_arg, year, week_num
    
    @abstractmethod
    def search_content(self, week_str, year, week_num):
        """
        搜索内容 - 子类实现
        
        返回: 内容列表 [{title, url, source, date, summary}]
        """
        pass
    
    def classify_content(self, item):
        """分类内容到模块 - 可被子类覆盖"""
        title = item.get("title", "").lower()
        
        # 默认实现，子类可覆盖
        return self.modules[0] if self.modules else "default"
    
    def save_results(self, week_str, content_items):
        """保存收集结果"""
        output_dir = self.base_path / f"memory/{self.kb_key.replace('-', '_')}-content/weekly"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # 保存为 JSON (原始数据)
        json_file = output_dir / f"{self.kb_key}-{week_str}.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(content_items, f, ensure_ascii=False, indent=2)
        
        return json_file
    
    def collect(self, week="current"):
        """主收集流程"""
        print(f"\n{'=' * 60}")
        print(f"📚 Collector: {self.kb_icon} {self.kb_name}")
        print(f"{'=' * 60}")
        
        # 获取周信息
        week_str, year, week_num = self.get_week_info(week)
        print(f"📅 Week: {week_str} (第{week_num}周)")
        print(f"🔍 Search Queries: {', '.join(self.search_queries[:2])}...")
        
        # 搜索内容
        print("\n🔎 搜索内容...")
        content_items = self.search_content(week_str, year, week_num)
        
        if not content_items:
            print("⚠️ 未找到内容")
            return []
        
        print(f"✅ 找到 {len(content_items)} 条内容")
        
        # 分类内容
        print("\n📂 分类内容...")
        for item in content_items:
            item["module"] = self.classify_content(item)
        
        # 保存结果
        json_file = self.save_results(week_str, content_items)
        print(f"✅ 结果已保存: {json_file}")
        
        # 统计
        module_counts = {}
        for item in content_items:
            m = item.get("module", "unknown")
            module_counts[m] = module_counts.get(m, 0) + 1
        
        print(f"\n📊 分类统计:")
        for module, count in module_counts.items():
            print(f"  - {module}: {count}条")
        
        return content_items
