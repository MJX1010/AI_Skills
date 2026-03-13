#!/usr/bin/env python3
"""
Publisher Agent - 周刊推送器
负责生成周刊并推送到飞书
"""

import argparse
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path


def generate_weekly_md(kb_key, kb_name, kb_icon, modules, module_names, items, year, week_num):
    """生成周刊 Markdown"""
    
    # 计算日期
    jan_1 = datetime(year, 1, 1)
    week_start = jan_1 + timedelta(weeks=week_num-1, days=-jan_1.weekday())
    date_str = week_start.strftime("%Y年%m月%d日")
    
    # 按模块分组
    module_items = {m: [] for m in modules}
    for item in items:
        m = item.get("module", modules[0])
        if m in module_items:
            module_items[m].append(item)
    
    # 生成 Markdown
    md_lines = [
        f"# {kb_name}周刊：第{week_num}期（{date_str}）",
        "",
        "---",
        "",
        f"**本期编辑** | OpenClaw AI  ",
        f"**出版日期** | {date_str}  ",
        f"**总第{week_num}期**",
        "",
        "---",
        "",
        "## 📌 本周话题",
        f"{kb_name}本周热点内容精选...",
        "",
        "---",
        ""
    ]
    
    # 按模块输出
    for module in modules:
        items_list = module_items[module]
        if not items_list:
            continue
        
        module_name = module_names.get(module, module)
        md_lines.extend([
            f"## {module_name}",
            ""
        ])
        
        for i, item in enumerate(items_list[:5], 1):  # 每模块最多5条
            md_lines.extend([
                f"### {i}. [{item['title']}]({item['url']})",
                "",
                item.get("summary", "暂无摘要"),
                "",
                f"> 来源：[{item.get('source', '未知')}]({item['url']}) · {item.get('date', '')}",
                ""
            ])
        
        md_lines.extend(["---", ""])
    
    # 链接引用表
    md_lines.extend([
        "## 🔗 链接引用",
        "",
        "| 序号 | 标题 | 来源 | 日期 |",
        "|------|------|------|------|"
    ])
    
    idx = 1
    for module in modules:
        for item in module_items[module]:
            source = item.get('source', '未知')[:15]
            date = item.get('date', '')
            md_lines.append(f"| {idx} | [{item['title'][:30]}...]({item['url']}) | {source} | {date} |")
            idx += 1
    
    md_lines.extend([
        "",
        "---",
        "",
        "*本期周刊由 OpenClaw AI 自动生成*",
        ""
    ])
    
    return "\n".join(md_lines)


def main():
    parser = argparse.ArgumentParser(description="Publisher Agent")
    parser.add_argument("--week", default="current")
    
    args = parser.parse_args()
    
    print("\n" + "=" * 60)
    print("📰 Publisher Agent: 生成周刊")
    print("=" * 60)
    
    # 知识库配置
    kb_configs = {
        "ai-latest-news": {
            "name": "AI每周精选",
            "icon": "🤖",
            "modules": ["news", "tools", "research", "cases"],
            "module_names": {
                "news": "📰 行业资讯",
                "tools": "🛠️ 工具技巧",
                "research": "📚 深度研究",
                "cases": "💡 案例分享"
            }
        },
        "game-development": {
            "name": "游戏开发周刊",
            "icon": "🎮",
            "modules": ["engine", "design", "tech", "art", "audio", "indie"],
            "module_names": {
                "engine": "🎮 游戏引擎",
                "design": "🎯 游戏设计",
                "tech": "💻 开发技术",
                "art": "🎨 美术资源",
                "audio": "🎵 音频音效",
                "indie": "🏆 独立游戏"
            }
        },
        "healthy-living": {
            "name": "健康生活周刊",
            "icon": "🌱",
            "modules": ["fitness", "diet", "mental", "sleep", "medical", "tips"],
            "module_names": {
                "fitness": "🏃 运动健身",
                "diet": "🥗 饮食营养",
                "mental": "😊 心理健康",
                "sleep": "💤 睡眠健康",
                "medical": "🏥 医疗资讯",
                "tips": "✨ 生活妙招"
            }
        }
    }
    
    base_path = Path("/workspace/projects/workspace/memory")
    
    # 获取周信息
    if args.week == "current":
        today = datetime.now()
        year = today.year
        week_num = int(today.strftime("%W")) + 1
        week_str = f"{year}-W{week_num:02d}"
    else:
        week_str = args.week
        year = int(week_str.split("-W")[0])
        week_num = int(week_str.split("-W")[1])
    
    for kb_key, config in kb_configs.items():
        json_file = base_path / f"{kb_key.replace('-', '_')}-content/weekly/{kb_key}-{week_str}.json"
        
        if not json_file.exists():
            print(f"⚠️ 跳过 {kb_key}: 文件不存在")
            continue
        
        with open(json_file, 'r', encoding='utf-8') as f:
            items = json.load(f)
        
        print(f"\n📚 {config['icon']} {config['name']}: {len(items)} 条内容")
        
        # 生成 Markdown
        md_content = generate_weekly_md(
            kb_key, config['name'], config['icon'],
            config['modules'], config['module_names'],
            items, year, week_num
        )
        
        # 保存 Markdown
        output_dir = base_path / f"{kb_key.replace('-', '_')}-content/weekly"
        if kb_key == "ai-latest-news":
            md_file = output_dir / f"weekly-{week_str}.md"
        elif kb_key == "game-development":
            md_file = output_dir / f"game-weekly-{week_str}.md"
        else:
            md_file = output_dir / f"health-weekly-{week_str}.md"
        
        with open(md_file, 'w', encoding='utf-8') as f:
            f.write(md_content)
        
        print(f"  ✅ 周刊已生成: {md_file}")
    
    print("\n⚠️ 注意: 飞书同步需要手动执行或使用 sync_feishu.py")
    print("\n✅ 周刊生成完成")
    return 0


if __name__ == "__main__":
    sys.exit(main())
