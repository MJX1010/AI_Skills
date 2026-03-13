#!/usr/bin/env python3
"""
Classifier Processor - 内容分类器
"""

import argparse
import json
import sys
from pathlib import Path


def classify_ai(title, content=""):
    """AI内容分类"""
    text = (title + " " + content).lower()
    
    if any(kw in text for kw in ["发布", "融资", "openai", "anthropic", "google", "news", "员工", "起诉"]):
        return "news", 0.9
    elif any(kw in text for kw in ["工具", "教程", "技巧", "prompt", "how to"]):
        return "tools", 0.85
    elif any(kw in text for kw in ["论文", "原理", "分析", "研究", "paper", "research"]):
        return "research", 0.85
    elif any(kw in text for kw in ["案例", "实践", "经验", "案例", "case", "practice"]):
        return "cases", 0.8
    
    return "news", 0.6


def classify_game(title, content=""):
    """游戏内容分类"""
    text = (title + " " + content).lower()
    
    if any(kw in text for kw in ["unity", "unreal", "godot", "引擎", "engine"]):
        return "engine", 0.9
    elif any(kw in text for kw in ["设计", "机制", "玩法", "关卡", "design", "mechanic"]):
        return "design", 0.85
    elif any(kw in text for kw in ["代码", "技术", "算法", "tech", "code", "programming"]):
        return "tech", 0.85
    elif any(kw in text for kw in ["美术", "模型", "动画", "art", "model", "animation"]):
        return "art", 0.8
    elif any(kw in text for kw in ["音效", "音乐", "音频", "audio", "sound", "music"]):
        return "audio", 0.8
    elif any(kw in text for kw in ["独立", "indie", "独立游戏"]):
        return "indie", 0.85
    
    return "tech", 0.6


def classify_health(title, content=""):
    """健康内容分类"""
    text = (title + " " + content).lower()
    
    if any(kw in text for kw in ["运动", "健身", "跑步", "瑜伽", "exercise", "fitness"]):
        return "fitness", 0.9
    elif any(kw in text for kw in ["饮食", "营养", "食谱", "减肥", "diet", "nutrition"]):
        return "diet", 0.9
    elif any(kw in text for kw in ["心理", "压力", "情绪", "冥想", "mental", "psychology"]):
        return "mental", 0.85
    elif any(kw in text for kw in ["睡眠", "失眠", "作息", "sleep", "insomnia"]):
        return "sleep", 0.85
    elif any(kw in text for kw in ["疾病", "医疗", "预防", "medical", "disease"]):
        return "medical", 0.85
    elif any(kw in text for kw in ["生活", "窍门", "技巧", "妙招", "tips", "trick"]):
        return "tips", 0.8
    
    return "tips", 0.6


CLASSIFIERS = {
    "ai-latest-news": classify_ai,
    "game-development": classify_game,
    "healthy-living": classify_health,
}


def main():
    parser = argparse.ArgumentParser(description="Content Classifier Agent")
    parser.add_argument("--week", default="current")
    parser.add_argument("--kb")
    
    args = parser.parse_args()
    
    print("\n" + "=" * 60)
    print("📂 Classifier Agent: 内容分类")
    print("=" * 60)
    
    # 读取收集器输出
    base_path = Path("/workspace/projects/workspace/memory")
    
    for kb_key, classifier in CLASSIFIERS.items():
        if args.kb and args.kb != kb_key:
            continue
        
        json_file = base_path / f"{kb_key.replace('-', '_')}-content/weekly/{kb_key}-{args.week}.json"
        
        if not json_file.exists():
            print(f"⚠️ 文件不存在: {json_file}")
            continue
        
        with open(json_file, 'r', encoding='utf-8') as f:
            items = json.load(f)
        
        print(f"\n📚 {kb_key}: {len(items)} 条内容")
        
        # 分类
        for item in items:
            module, confidence = classifier(item.get("title", ""), item.get("summary", ""))
            item["module"] = module
            item["confidence"] = confidence
        
        # 保存
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(items, f, ensure_ascii=False, indent=2)
        
        # 统计
        counts = {}
        for item in items:
            m = item.get("module", "unknown")
            counts[m] = counts.get(m, 0) + 1
        
        print("  分类结果:")
        for m, c in counts.items():
            print(f"    - {m}: {c}条")
    
    print("\n✅ 分类完成")
    return 0


if __name__ == "__main__":
    sys.exit(main())
