#!/usr/bin/env python3
"""
Quality Filter Processor - 质量筛选器
支持从配置文件读取权威来源
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.config import get_config


def calculate_quality(item, config, kb_key):
    """计算内容质量分"""
    score = 0.5  # 基础分
    
    # 从配置获取权威来源加分
    source = item.get("source", "").lower()
    if config.is_authoritative_source(kb_key, source):
        score += config.get_quality_threshold("authoritative_bonus", 0.2)
    
    # 有摘要
    if item.get("summary") and len(item.get("summary", "")) > 20:
        score += 0.15
    
    # 有日期
    if item.get("date"):
        score += 0.1
    
    # 标题长度适中
    title_len = len(item.get("title", ""))
    if 10 < title_len < 100:
        score += 0.05
    
    return min(score, 1.0)


def main():
    parser = argparse.ArgumentParser(description="Quality Filter Agent")
    parser.add_argument("--week", default="current")
    
    args = parser.parse_args()
    
    print("\n" + "=" * 60)
    print("🔍 Quality Filter Agent: 质量筛选")
    print("=" * 60)
    
    config = get_config()
    base_path = Path("/workspace/projects/workspace/memory")
    kb_list = ["ai-latest-news", "game-development", "healthy-living"]
    
    for kb_key in kb_list:
        json_file = base_path / f"{kb_key.replace('-', '_')}-content/weekly/{kb_key}-{args.week}.json"
        
        if not json_file.exists():
            continue
        
        with open(json_file, 'r', encoding='utf-8') as f:
            items = json.load(f)
        
        print(f"\n📚 {kb_key}: {len(items)} 条内容")
        
        # 计算质量分（使用配置）
        for item in items:
            item["quality_score"] = calculate_quality(item, config, kb_key)
        
        # 过滤低质量
        min_confidence = config.get_quality_threshold("min_confidence", 0.4)
        filtered = [item for item in items if item.get("quality_score", 0) > min_confidence]
        
        # 按质量排序
        filtered.sort(key=lambda x: x.get("quality_score", 0), reverse=True)
        
        # 保存
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(filtered, f, ensure_ascii=False, indent=2)
        
        print(f"  ✅ 筛选后: {len(filtered)} 条 (过滤 {len(items) - len(filtered)} 条)")
        
        # 高质量标记
        high_quality_threshold = config.get_quality_threshold("high_quality", 0.8)
        high_quality = [item for item in filtered if item.get("quality_score", 0) > high_quality_threshold]
        print(f"  ⭐ 高质量: {len(high_quality)} 条")
    
    print("\n✅ 质量筛选完成")
    return 0


if __name__ == "__main__":
    sys.exit(main())
