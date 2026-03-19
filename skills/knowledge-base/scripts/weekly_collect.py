#!/usr/bin/env python3
"""
周报收集脚本 - 汇总本周所有日报内容
"""

import argparse
from datetime import datetime, timedelta
from pathlib import Path

WORKSPACE = Path("/workspace/projects/workspace")
MEMORY_DIR = WORKSPACE / "memory"

KB_CONFIG = {
    "ai-latest-news": {"name": "🤖 AI最新资讯"},
    "game-development": {"name": "🎮 游戏开发"},
    "healthy-living": {"name": "🌱 健康生活"}
}


def get_week_range(date=None):
    """获取本周日期范围（周一到周日）"""
    if date is None:
        date = datetime.now()
    
    monday = date - timedelta(days=date.weekday())
    sunday = monday + timedelta(days=6)
    
    return monday, sunday


def collect_weekly_content(kb: str, monday: datetime, sunday: datetime) -> str:
    """收集本周所有日报内容"""
    year = monday.strftime("%Y")
    month = monday.strftime("%m")
    
    contents = []
    current = monday
    
    while current <= sunday:
        day = current.strftime("%d")
        daily_file = MEMORY_DIR / "kb-archive" / kb / year / month / f"{day}.md"
        
        if daily_file.exists():
            content = daily_file.read_text(encoding="utf-8")
            contents.append((current.strftime("%m-%d"), content))
        
        current += timedelta(days=1)
    
    return contents


def generate_weekly_md(kb: str, contents: list, monday: datetime, sunday: datetime) -> str:
    """生成周报 Markdown"""
    config = KB_CONFIG[kb]
    week_num = monday.isocalendar()[1]
    date_range = f"{monday.strftime('%m.%d')}-{sunday.strftime('%m.%d')}"
    
    lines = []
    lines.append(f"# {config['name']}周刊：第{week_num}期（{date_range}）")
    lines.append("")
    lines.append(f"**本期编辑** | OpenClaw AI")
    lines.append(f"**出版日期** | {datetime.now().strftime('%Y年%m月%d日')}")
    lines.append(f"**总第{week_num}期**")
    lines.append("")
    lines.append("---")
    lines.append("")
    
    # 统计
    total_articles = sum(c[1].count("### [") for c in contents)
    lines.append(f"## 📌 本周话题")
    lines.append("")
    lines.append(f"本周共收录 **{total_articles}** 条优质内容。")
    lines.append("")
    lines.append("---")
    lines.append("")
    
    # 每日内容
    for date_str, content in contents:
        # 提取文章列表
        articles = []
        for line in content.split("\n"):
            if line.startswith("### ["):
                articles.append(line)
        
        if articles:
            lines.append(f"## {date_str}")
            lines.append("")
            for article in articles:
                lines.append(article)
            lines.append("")
    
    lines.append("---")
    lines.append("")
    lines.append("*本期周报由 OpenClaw AI 自动生成*")
    
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="周报收集")
    parser.add_argument("--date", help="日期 (YYYY-MM-DD，默认今天)")
    args = parser.parse_args()
    
    if args.date:
        date = datetime.strptime(args.date, "%Y-%m-%d")
    else:
        date = datetime.now()
    
    monday, sunday = get_week_range(date)
    week_num = monday.isocalendar()[1]
    
    print("\n" + "="*60)
    print("🔄 周报收集")
    print("="*60)
    print(f"📅 本周: {monday.strftime('%Y-%m-%d')} ~ {sunday.strftime('%Y-%m-%d')}")
    print(f"📊 第 {week_num} 周")
    print("="*60 + "\n")
    
    for kb in KB_CONFIG.keys():
        print(f"📚 收集: {KB_CONFIG[kb]['name']}")
        
        contents = collect_weekly_content(kb, monday, sunday)
        
        if not contents:
            print(f"  ⚠️ 本周无内容\n")
            continue
        
        # 生成周报
        weekly_md = generate_weekly_md(kb, contents, monday, sunday)
        
        # 保存周报
        year = monday.strftime("%Y")
        month = monday.strftime("%m")
        weekly_file = MEMORY_DIR / "kb-archive" / kb / year / month / f"week-{week_num}.md"
        weekly_file.parent.mkdir(parents=True, exist_ok=True)
        weekly_file.write_text(weekly_md, encoding="utf-8")
        
        total = sum(c[1].count("### [") for c in contents)
        print(f"  ✅ 已生成: {weekly_file}")
        print(f"  📊 共 {total} 条内容\n")
    
    print("="*60)
    print("✅ 周报收集完成!")
    print("="*60 + "\n")
    
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
