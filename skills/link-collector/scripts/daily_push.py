#!/usr/bin/env python3
"""
知识库每日推送脚本
每天早上8点推送三个知识库的更新内容和链接卡片
"""

import json
from datetime import datetime, timedelta
from pathlib import Path

# 知识库配置
KNOWLEDGE_BASES = {
    "ai-latest-news": {
        "name": "AI最新资讯",
        "space_id": "7616519632920251572",
        "icon": "🤖",
        "description": "AI行业动态、技术突破、产品发布",
        "update_time": "每周五下午6点",
        "weekly_format": True
    },
    "game-dev": {
        "name": "游戏开发", 
        "space_id": "7616735513310924004",
        "icon": "🎮",
        "description": "游戏引擎、开发技术、独立游戏",
        "update_time": "每周五下午6点",
        "weekly_format": True
    },
    "healthy-living": {
        "name": "健康生活",
        "space_id": "7616737910330510558",
        "icon": "🌱",
        "description": "生活妙招、健康知识、运动健身、饮食营养",
        "update_time": "每周更新",
        "weekly_format": True
    },
    "link-collection": {
        "name": "链接收藏",
        "space_id": None,  # 飞书文档
        "icon": "🔗",
        "description": "技术文章、工具资源、教程收藏",
        "update_time": "实时更新",
        "weekly_format": False
    }
}

def get_today_updates():
    """获取今日更新内容"""
    today = datetime.now()
    today_str = today.strftime("%Y-%m-%d")
    
    updates = {
        "date": today_str,
        "kbs": []
    }
    
    # 检查 AI 内容收集目录
    ai_weekly_dir = Path("/workspace/projects/workspace/memory/ai-content/weekly")
    if ai_weekly_dir.exists():
        # 查找最新的周刊
        files = sorted(ai_weekly_dir.glob("weekly-*.md"), reverse=True)
        if files:
            latest = files[0]
            latest_date = latest.stat().st_mtime
            latest_datetime = datetime.fromtimestamp(latest_date)
            
            # 如果是最近7天内更新
            if (today - latest_datetime).days <= 7:
                updates["kbs"].append({
                    "key": "ai-latest-news",
                    "name": "AI最新资讯",
                    "icon": "🤖",
                    "latest_update": latest_datetime.strftime("%Y-%m-%d"),
                    "content": f"第{latest_datetime.isocalendar()[1]}期周刊已发布",
                    "url": f"https://xxx.feishu.cn/wiki/ai-weekly-{latest_datetime.strftime('%Y-W%U')}"
                })
    
    # 检查游戏开发目录
    game_weekly_dir = Path("/workspace/projects/workspace/memory/game-content/weekly")
    if game_weekly_dir.exists():
        files = sorted(game_weekly_dir.glob("game-weekly-*.md"), reverse=True)
        if files:
            latest = files[0]
            latest_date = latest.stat().st_mtime
            latest_datetime = datetime.fromtimestamp(latest_date)
            
            if (today - latest_datetime).days <= 7:
                updates["kbs"].append({
                    "key": "game-dev",
                    "name": "游戏开发",
                    "icon": "🎮",
                    "latest_update": latest_datetime.strftime("%Y-%m-%d"),
                    "content": f"第{latest_datetime.isocalendar()[1]}期游戏周刊已发布",
                    "url": f"https://xxx.feishu.cn/wiki/game-weekly-{latest_datetime.strftime('%Y-W%U')}"
                })
    
    # 检查健康生活目录
    health_weekly_dir = Path("/workspace/projects/workspace/memory/health-content/weekly")
    if health_weekly_dir.exists():
        files = sorted(health_weekly_dir.glob("health-weekly-*.md"), reverse=True)
        if files:
            latest = files[0]
            latest_date = latest.stat().st_mtime
            latest_datetime = datetime.fromtimestamp(latest_date)
            
            if (today - latest_datetime).days <= 7:
                updates["kbs"].append({
                    "key": "healthy-living",
                    "name": "健康生活",
                    "icon": "🌱",
                    "latest_update": latest_datetime.strftime("%Y-%m-%d"),
                    "content": f"第{latest_datetime.isocalendar()[1]}期健康生活周刊已发布",
                    "url": f"https://xxx.feishu.cn/wiki/health-weekly-{latest_datetime.strftime('%Y-W%U')}"
                })
    
    # 链接收藏（检查最近添加的链接）
    link_dir = Path("/workspace/projects/workspace/memory/link-collection")
    if link_dir.exists():
        files = sorted(link_dir.glob("*.md"), reverse=True)
        if files:
            latest = files[0]
            latest_date = latest.stat().st_mtime
            latest_datetime = datetime.fromtimestamp(latest_date)
            
            if (today - latest_datetime).days <= 1:  # 最近1天
                updates["kbs"].append({
                    "key": "link-collection",
                    "name": "链接收藏",
                    "icon": "🔗",
                    "latest_update": latest_datetime.strftime("%Y-%m-%d"),
                    "content": f"新增 {len(files)} 个链接收藏",
                    "url": f"https://xxx.feishu.cn/wiki/link-collection"
                })
    
    return updates

def generate_push_message(updates):
    """生成推送消息"""
    today_str = datetime.now().strftime("%Y年%m月%d日")
    weekday = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"][datetime.now().weekday()]
    
    message = f"📚 知识库日报 | {today_str} {weekday}\n"
    message += "=" * 40 + "\n\n"
    
    if not updates["kbs"]:
        message += "📝 今日暂无新内容更新\n\n"
        message += "📌 知识库入口：\n"
        for key, kb in KNOWLEDGE_BASES.items():
            message += f"{kb['icon']} {kb['name']}\n"
    else:
        message += f"🆕 今日更新 {len(updates['kbs'])} 个知识库\n\n"
        
        for kb in updates["kbs"]:
            message += f"{kb['icon']} **{kb['name']}**\n"
            message += f"   {kb['content']}\n"
            message += f"   📅 更新于：{kb['latest_update']}\n"
            message += f"   🔗 [查看详情]({kb['url']})\n\n"
    
    message += "=" * 40 + "\n"
    message += "💡 提示：每天8点自动推送知识库更新\n"
    
    return message

def generate_feishu_card(updates):
    """生成飞书卡片消息"""
    today_str = datetime.now().strftime("%Y年%m月%d日")
    
    card = {
        "config": {
            "wide_screen_mode": True
        },
        "header": {
            "title": {
                "tag": "plain_text",
                "content": f"📚 知识库日报 | {today_str}"
            },
            "template": "blue"
        },
        "elements": []
    }
    
    # 更新内容
    if updates["kbs"]:
        card["elements"].append({
            "tag": "div",
            "text": {
                "tag": "lark_md",
                "content": f"**🆕 今日更新 {len(updates['kbs'])} 个知识库**"
            }
        })
        card["elements"].append({"tag": "hr"})
        
        for kb in updates["kbs"]:
            card["elements"].append({
                "tag": "div",
                "text": {
                    "tag": "lark_md",
                    "content": f"{kb['icon']} **{kb['name']}**\n{kb['content']}\n📅 {kb['latest_update']}"
                }
            })
            # 添加跳转按钮
            card["elements"].append({
                "tag": "action",
                "actions": [
                    {
                        "tag": "button",
                        "text": {
                            "tag": "plain_text",
                            "content": "查看详情"
                        },
                        "type": "primary",
                        "url": kb['url']
                    }
                ]
            })
            card["elements"].append({"tag": "hr"})
    else:
        card["elements"].append({
            "tag": "div",
            "text": {
                "tag": "lark_md",
                "content": "📝 今日暂无新内容更新"
            }
        })
    
    # 知识库入口
    card["elements"].append({
        "tag": "div",
        "text": {
            "tag": "lark_md",
            "content": "**📌 知识库入口**"
        }
    })
    
    # 添加各个知识库的链接
    for key, kb in KNOWLEDGE_BASES.items():
        card["elements"].append({
            "tag": "action",
            "actions": [
                {
                    "tag": "button",
                    "text": {
                        "tag": "plain_text",
                        "content": f"{kb['icon']} {kb['name']}"
                    },
                    "type": "default",
                    "url": f"https://xxx.feishu.cn/wiki/{kb['space_id']}" if kb['space_id'] else "#"
                }
            ]
        })
    
    return card

def main():
    """主函数"""
    print("=" * 60)
    print("知识库日报推送")
    print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 60)
    print()
    
    # 获取更新
    updates = get_today_updates()
    
    # 生成消息
    message = generate_push_message(updates)
    card = generate_feishu_card(updates)
    
    print(message)
    print()
    print("飞书卡片已生成")
    
    # 保存到文件（供后续发送使用）
    output_dir = Path("/workspace/projects/workspace/memory/daily-push")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    today_str = datetime.now().strftime("%Y%m%d")
    
    # 保存文本消息
    text_file = output_dir / f"push-{today_str}.txt"
    text_file.write_text(message, encoding='utf-8')
    
    # 保存卡片JSON
    card_file = output_dir / f"push-{today_str}.json"
    card_file.write_text(json.dumps(card, ensure_ascii=False, indent=2), encoding='utf-8')
    
    print(f"✅ 推送内容已保存:")
    print(f"   文本: {text_file}")
    print(f"   卡片: {card_file}")
    
    return message, card

if __name__ == "__main__":
    main()
