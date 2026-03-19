#!/usr/bin/env python3
"""
日报推送脚本 - 推送日报到飞书知识库
正确使用方式：先检查节点是否存在，不存在才创建
"""

import json
import sys
from datetime import datetime
from pathlib import Path

WORKSPACE = Path("/workspace/projects/workspace")
MEMORY_DIR = WORKSPACE / "memory"

KB_CONFIG = {
    "ai-latest-news": {
        "name": "🤖 AI最新资讯",
        "space_id": "7616519632920251572"
    },
    "game-development": {
        "name": "🎮 游戏开发",
        "space_id": "7616735513310924004"
    },
    "healthy-living": {
        "name": "🌱 健康生活",
        "space_id": "7616737910330510558"
    }
}


def read_daily_content(kb: str, date_str: str) -> str:
    """读取日报内容"""
    year = date_str[:4]
    month = date_str[5:7]
    day = date_str[8:10]
    
    file_path = MEMORY_DIR / "kb-archive" / kb / year / month / f"{day}.md"
    
    if file_path.exists():
        return file_path.read_text(encoding="utf-8")
    return ""


def count_articles(content: str) -> int:
    """统计文章数量"""
    return content.count("### [")


def generate_push_message(date_str: str, stats: dict) -> str:
    """生成推送消息"""
    date_obj = datetime.strptime(date_str, "%Y-%m-%d")
    weekday = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"][date_obj.weekday()]
    
    message = f"📚 **知识库日报** | {date_str} {weekday}\n\n"
    
    total = sum(s["count"] for s in stats.values())
    if total == 0:
        message += "今日暂无新增内容\n"
        return message
    
    message += f"今日共新增 **{total}** 条内容\n\n---\n\n"
    
    for kb, info in stats.items():
        if info["count"] > 0:
            message += f"{info['name']}: {info['count']} 条\n"
    
    message += "\n---\n📖 点击查看完整知识库"
    
    return message


def main():
    date_str = datetime.now().strftime("%Y-%m-%d")
    
    print("\n" + "="*60)
    print("📤 日报推送")
    print("="*60)
    print(f"📅 日期: {date_str}")
    print("="*60)
    
    stats = {}
    
    # 统计每个知识库的内容
    for kb in KB_CONFIG.keys():
        content = read_daily_content(kb, date_str)
        count = count_articles(content)
        stats[kb] = {
            "name": KB_CONFIG[kb]["name"],
            "count": count
        }
        
        if count > 0:
            print(f"\n  📊 {KB_CONFIG[kb]['name']}: {count} 条")
            print(f"     💡 同步步骤：")
            print(f"     1. feishu_wiki --action nodes --space_id {KB_CONFIG[kb]['space_id']}")
            print(f"     2. 查找或创建: 2026年 → 3月 → 3月19日 日报")
            print(f"     3. feishu_doc --action write --doc_token <token> --content <content>")
        else:
            print(f"\n  ⏭️  {KB_CONFIG[kb]['name']}: 无内容，跳过")
    
    # 生成推送消息
    message = generate_push_message(date_str, stats)
    
    print("\n" + "="*60)
    print("📱 推送消息内容:")
    print("="*60)
    print(message)
    print("="*60)
    
    # 保存推送记录
    push_dir = MEMORY_DIR / "daily-push"
    push_dir.mkdir(parents=True, exist_ok=True)
    push_file = push_dir / f"{date_str}.json"
    push_file.write_text(json.dumps({
        "date": date_str,
        "stats": stats,
        "message": message,
        "pushed_at": datetime.now().isoformat()
    }, indent=2, ensure_ascii=False), encoding="utf-8")
    
    print(f"\n✅ 推送记录已保存: {push_file}")
    print("\n📋 本地文件位置:")
    for kb in KB_CONFIG.keys():
        file_path = MEMORY_DIR / "kb-archive" / kb / date_str[:4] / date_str[5:7] / f"{date_str[8:10]}.md"
        if file_path.exists():
            print(f"  - {file_path}")
    
    print("\n" + "="*60)
    print("⚠️  重要提示：关于节点复用")
    print("="*60)
    print("正确的节点获取流程应该是：")
    print("  1. 列出已有节点: feishu_wiki --action nodes --space_id <id>")
    print("  2. 检查是否存在 '2026年' 节点")
    print("  3. 如果存在 → 复用该节点的 node_token")
    print("  4. 如果不存在 → 创建新节点")
    print("  5. 对 '3月' 节点重复上述流程")
    print("="*60)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
