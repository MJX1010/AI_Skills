#!/usr/bin/env python3
"""
推送通知脚本 - 发送任务执行结果到飞书
使用 OpenClaw 的消息推送功能
"""

import json
from datetime import datetime
from pathlib import Path

WORKSPACE = Path("/workspace/projects/workspace")
MEMORY_DIR = WORKSPACE / "memory"

KB_CONFIG = {
    "ai-latest-news": {"name": "🤖 AI最新资讯"},
    "game-development": {"name": "🎮 游戏开发"},
    "healthy-living": {"name": "🌱 健康生活"}
}


def read_push_record(date_str: str) -> dict:
    """读取推送记录"""
    push_file = MEMORY_DIR / "daily-push" / f"{date_str}.json"
    if push_file.exists():
        return json.loads(push_file.read_text(encoding="utf-8"))
    return None


def generate_daily_report(date_str: str) -> str:
    """生成日报报告"""
    record = read_push_record(date_str)
    
    if not record:
        return f"📚 **知识库日报** | {date_str}\n\n今日暂无收集记录"
    
    total = sum(s["count"] for s in record["stats"].values())
    
    if total == 0:
        return f"📚 **知识库日报** | {date_str}\n\n今日暂无新增内容"
    
    message = f"📚 **知识库日报** | {date_str}\n\n"
    message += f"✅ 今日共收集 **{total}** 条内容\n\n"
    
    for kb, info in record["stats"].items():
        if info["count"] > 0:
            message += f"{info['name']}: {info['count']} 条\n"
    
    message += "\n📁 已同步到飞书知识库\n"
    message += "💾 本地备份已保存"
    
    return message


def generate_weekly_report(date_str: str) -> str:
    """生成周报报告"""
    # 查找本周的推送记录
    date_obj = datetime.strptime(date_str, "%Y-%m-%d")
    weekday = date_obj.weekday()
    
    # 计算本周一
    monday = date_obj - __import__('datetime').timedelta(days=weekday)
    
    message = f"📰 **知识库周报** | 第{date_obj.isocalendar()[1]}期\n"
    message += f"📅 {monday.strftime('%m月%d日')} - {date_str}\n\n"
    
    # 统计本周内容
    total = 0
    for i in range(7):
        day = monday + __import__('datetime').timedelta(days=i)
        day_str = day.strftime("%Y-%m-%d")
        record = read_push_record(day_str)
        if record:
            total += sum(s["count"] for s in record["stats"].values())
    
    if total == 0:
        message += "本周暂无新增内容\n"
    else:
        message += f"✅ 本周共收集 **{total}** 条内容\n\n"
        message += "📁 已同步到飞书知识库"
    
    return message


def main():
    """主函数 - 输出发送给用户的消息"""
    date_str = datetime.now().strftime("%Y-%m-%d")
    
    # 判断是日报还是周报
    weekday = datetime.now().weekday()
    hour = datetime.now().hour
    
    if weekday == 4 and hour >= 18:  # 周五 18:00 后，推送周报
        message = generate_weekly_report(date_str)
        print("WEEKLY")
    else:  # 其他时间，推送日报
        message = generate_daily_report(date_str)
        print("DAILY")
    
    print(message)
    
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
