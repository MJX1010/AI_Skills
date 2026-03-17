#!/usr/bin/env python3
"""
每日资讯收集脚本
收集前一天发布的资讯，保存到daily目录
Usage: python daily_collect.py [--date YYYY-MM-DD]
"""

import argparse
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path

# 知识库列表
KNOWLEDGE_BASES = [
    ("ai-latest-news", "🤖 AI最新资讯", "ai-content"),
    ("game-development", "🎮 游戏开发", "game-content"),
    ("healthy-living", "🌱 健康生活", "health-content")
]


def get_target_date(date_arg):
    """获取目标日期"""
    if date_arg == "yesterday":
        date = datetime.now() - timedelta(days=1)
    else:
        date = datetime.strptime(date_arg, "%Y-%m-%d")
    return date


def run_collector(kb_key, date_str):
    """运行收集器"""
    print(f"\n{'=' * 60}")
    print(f"📚 收集: {kb_key}")
    print(f"{'=' * 60}")
    
    cmd = [
        sys.executable,
        "skills/content-collector/scripts/collect.py",
        "--kb", kb_key,
        "--week", "current"
    ]
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300,
            cwd="/workspace/projects/workspace"
        )
        
        if result.returncode == 0:
            print(result.stdout)
            return True
        else:
            print(f"❌ 收集失败: {result.stderr}")
            return False
    
    except Exception as e:
        print(f"❌ 异常: {e}")
        return False


def generate_daily_summary(date_str, results):
    """生成每日汇总报告"""
    date_obj = datetime.strptime(date_str, "%Y-%m-%d")
    weekday = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"][date_obj.weekday()]
    
    lines = []
    lines.append(f"📅 {date_str} {weekday} 资讯汇总")
    lines.append("=" * 50)
    lines.append("")
    
    total = 0
    for kb_key, kb_name, folder in KNOWLEDGE_BASES:
        # 读取收集到的内容
        daily_file = Path(f"/workspace/projects/workspace/memory/{folder}/daily/{date_str}.md")
        count = 0
        if daily_file.exists():
            content = daily_file.read_text(encoding='utf-8')
            # 统计文章数
            count = content.count("### ")
        
        status = "✅" if results.get(kb_key) else "❌"
        lines.append(f"{status} {kb_name}: {count}篇")
        total += count
    
    lines.append("")
    lines.append(f"📊 总计: {total}篇")
    lines.append("=" * 50)
    
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="每日资讯收集")
    parser.add_argument("--date", default="yesterday",
                       help="目标日期 (yesterday 或 YYYY-MM-DD)")
    
    args = parser.parse_args()
    
    # 获取目标日期
    target_date = get_target_date(args.date)
    date_str = target_date.strftime("%Y-%m-%d")
    
    print("=" * 60)
    print("🔄 每日资讯收集")
    print("=" * 60)
    print(f"📅 目标日期: {date_str}")
    print(f"⏰ 收集范围: 前一天发布的资讯")
    print()
    
    results = {}
    
    # 收集所有知识库
    for kb_key, kb_name, folder in KNOWLEDGE_BASES:
        success = run_collector(kb_key, date_str)
        results[kb_key] = success
    
    # 生成汇总报告
    print("\n" + "=" * 60)
    print("📊 收集完成汇总")
    print("=" * 60)
    
    for kb_key, kb_name, folder in KNOWLEDGE_BASES:
        status_icon = "✅" if results[kb_key] else "❌"
        print(f"{status_icon} {kb_name}")
    
    # 保存汇总报告
    summary = generate_daily_summary(date_str, results)
    summary_dir = Path("/workspace/projects/workspace/memory/daily-summary")
    summary_dir.mkdir(parents=True, exist_ok=True)
    summary_file = summary_dir / f"{date_str}.txt"
    summary_file.write_text(summary, encoding='utf-8')
    
    print(f"\n✅ 汇总报告已保存: {summary_file}")
    
    return 0 if all(results.values()) else 1


if __name__ == "__main__":
    sys.exit(main())
