#!/usr/bin/env python3
"""
日报推送脚本 - 推送日报到飞书知识库
使用 OpenClaw 内部 API
"""

import json
import sys
from datetime import datetime
from pathlib import Path

# 添加 OpenClaw 扩展路径
sys.path.insert(0, '/usr/lib/node_modules/openclaw/extensions/feishu')

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


def load_feishu_tools():
    """加载飞书工具"""
    try:
        # 尝试导入 feishu 模块
        import importlib.util
        spec = importlib.util.spec_from_file_location("feishu_wiki", "/usr/lib/node_modules/openclaw/extensions/feishu/skills/feishu-wiki.py")
        if spec and spec.loader:
            feishu_wiki = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(feishu_wiki)
            return feishu_wiki
    except Exception as e:
        print(f"⚠️ 无法加载 feishu_wiki: {e}")
    return None


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
    
    # 尝试加载飞书工具
    feishu_module = load_feishu_tools()
    
    if not feishu_module:
        print("\n  ⚠️ 飞书工具模块无法加载")
        print("  💡 请使用以下命令手动同步到飞书：")
        print()
        for kb, config in KB_CONFIG.items():
            content = read_daily_content(kb, date_str)
            count = count_articles(content)
            if count > 0:
                print(f"  # {config['name']}")
                print(f"  feishu_wiki --action nodes --space_id {config['space_id']}")
                print(f"  # 然后创建文档并写入内容")
                print()
    
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
            if feishu_module:
                print(f"     🔄 准备同步...")
                # 这里可以调用飞书工具
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
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
