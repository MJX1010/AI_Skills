#!/usr/bin/env python3
"""
统一内容收集器 - 收集指定知识库的周刊内容
Usage: python collect.py --kb <knowledge_base> --week <current|YYYY-WXX>
"""

import argparse
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

# 知识库配置
KB_CONFIG = {
    "ai-latest-news": {
        "name": "AI最新资讯",
        "icon": "🤖",
        "search_queries": [
            "OpenAI Anthropic Google AI latest news",
            "AI人工智能 最新动态 GPT Claude"
        ],
        "modules": ["news", "tools", "research", "cases"],
        "module_names": {
            "news": "📰 行业资讯",
            "tools": "🛠️ 工具技巧",
            "research": "📚 深度研究",
            "cases": "💡 案例分享"
        },
        "output_dir": "memory/ai-content",
        "keywords": ["AI", "人工智能", "GPT", "Claude", "LLM", "机器学习", "OpenAI", "Anthropic"]
    },
    "game-development": {
        "name": "游戏开发",
        "icon": "🎮",
        "search_queries": [
            "Unity Unreal game development news",
            "游戏开发 Unity 独立游戏 最新动态"
        ],
        "modules": ["engine", "design", "tech", "art", "audio", "indie"],
        "module_names": {
            "engine": "🎮 游戏引擎",
            "design": "🎯 游戏设计",
            "tech": "💻 开发技术",
            "art": "🎨 美术资源",
            "audio": "🎵 音频音效",
            "indie": "🏆 独立游戏"
        },
        "output_dir": "memory/game-content",
        "keywords": ["Unity", "Unreal", "Godot", "游戏", "game", "独立游戏", "indie", "引擎"]
    },
    "healthy-living": {
        "name": "健康生活",
        "icon": "🌱",
        "search_queries": [
            "健康 运动 饮食 生活妙招",
            "fitness nutrition mental health tips"
        ],
        "modules": ["fitness", "diet", "mental", "sleep", "medical", "tips"],
        "module_names": {
            "fitness": "🏃 运动健身",
            "diet": "🥗 饮食营养",
            "mental": "😊 心理健康",
            "sleep": "💤 睡眠健康",
            "medical": "🏥 医疗资讯",
            "tips": "✨ 生活妙招"
        },
        "output_dir": "memory/health-content",
        "keywords": ["健康", "运动", "饮食", "心理", "生活", "健身", "营养", "睡眠"]
    }
}


def get_week_info(week_arg):
    """获取周信息"""
    if week_arg == "current":
        today = datetime.now()
        year = today.year
        week_num = int(today.strftime("%W")) + 1  # 转换为1-based
        return f"{year}-W{week_num:02d}", year, week_num
    else:
        # 格式: YYYY-WXX
        parts = week_arg.split("-W")
        year = int(parts[0])
        week_num = int(parts[1])
        return week_arg, year, week_num


def classify_content(title, content, kb_config):
    """分类内容到模块"""
    text = (title + " " + content).lower()
    module_scores = {}
    
    # 根据知识库使用不同的分类逻辑
    if kb_config["name"] == "AI最新资讯":
        if any(kw in text for kw in ["发布", "融资", "openai", "anthropic", "google", "news", "新闻"]):
            return "news"
        elif any(kw in text for kw in ["工具", "教程", "技巧", "prompt", "how to", "tool"]):
            return "tools"
        elif any(kw in text for kw in ["论文", "原理", "分析", "研究", "paper", "research"]):
            return "research"
        elif any(kw in text for kw in ["案例", "实践", "经验", "案例", "case", "practice"]):
            return "cases"
    
    elif kb_config["name"] == "游戏开发":
        if any(kw in text for kw in ["unity", "unreal", "godot", "引擎", "engine"]):
            return "engine"
        elif any(kw in text for kw in ["设计", "机制", "玩法", "关卡", "design", "mechanic"]):
            return "design"
        elif any(kw in text for kw in ["代码", "技术", "算法", "tech", "code", "programming"]):
            return "tech"
        elif any(kw in text for kw in ["美术", "模型", "动画", "art", "model", "animation"]):
            return "art"
        elif any(kw in text for kw in ["音效", "音乐", "音频", "audio", "sound", "music"]):
            return "audio"
        elif any(kw in text for kw in ["独立", "indie", "独立游戏"]):
            return "indie"
    
    elif kb_config["name"] == "健康生活":
        if any(kw in text for kw in ["运动", "健身", "跑步", "瑜伽", "exercise", "fitness"]):
            return "fitness"
        elif any(kw in text for kw in ["饮食", "营养", "食谱", "减肥", "diet", "nutrition"]):
            return "diet"
        elif any(kw in text for kw in ["心理", "压力", "情绪", "冥想", "mental", "psychology"]):
            return "mental"
        elif any(kw in text for kw in ["睡眠", "失眠", "作息", "sleep", "insomnia"]):
            return "sleep"
        elif any(kw in text for kw in ["疾病", "医疗", "预防", "medical", "disease", "health"]):
            return "medical"
        elif any(kw in text for kw in ["生活", "窍门", "技巧", "妙招", "tips", "trick"]):
            return "tips"
    
    # 默认返回第一个模块
    return kb_config["modules"][0]


def generate_weekly_md(kb_key, week_str, year, week_num, content_items):
    """生成周刊 Markdown 文件"""
    config = KB_CONFIG[kb_key]
    
    # 计算周日期范围
    jan_1 = datetime(year, 1, 1)
    week_start = jan_1 + timedelta(weeks=week_num-1, days=-jan_1.weekday())
    week_end = week_start + timedelta(days=6)
    date_str = week_start.strftime("%Y年%m月%d日")
    
    # 按模块分组
    modules_content = {m: [] for m in config["modules"]}
    for item in content_items:
        module = item.get("module", config["modules"][0])
        if module in modules_content:
            modules_content[module].append(item)
    
    # 生成 Markdown
    md_lines = [
        f"# {config['name']}周刊：第{week_num}期（{date_str}）",
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
        "（本期热点综述）",
        "",
        "---",
        ""
    ]
    
    # 按模块输出
    for module in config["modules"]:
        items = modules_content[module]
        if not items:
            continue
        
        module_name = config["module_names"][module]
        md_lines.extend([
            f"## {module_name}",
            ""
        ])
        
        for i, item in enumerate(items, 1):
            md_lines.extend([
                f"### {i}. [{item['title']}]({item['url']})",
                "",
                item.get("summary", "暂无摘要"),
                "",
                f"> 来源：[{item.get('source', '未知')}]({item['url']}) · {item.get('date', '')}",
                ""
            ])
        
        md_lines.append("---")
        md_lines.append("")
    
    # 链接引用表
    md_lines.extend([
        "## 🔗 链接引用",
        "",
        "| 序号 | 标题 | 来源 | 日期 |",
        "|------|------|------|------|"
    ])
    
    idx = 1
    for module in config["modules"]:
        for item in modules_content[module]:
            source = item.get('source', '未知')
            date = item.get('date', '')
            md_lines.append(f"| {idx} | [{item['title']}]({item['url']}) | {source} | {date} |")
            idx += 1
    
    md_lines.extend([
        "",
        "---",
        "",
        "*本期周刊由 OpenClaw AI 自动生成*",
        ""
    ])
    
    return "\n".join(md_lines)


def save_weekly(kb_key, week_str, year, week_num, content_items):
    """保存周刊到本地文件"""
    config = KB_CONFIG[kb_key]
    
    # 确保目录存在
    weekly_dir = Path(f"/workspace/projects/workspace/{config['output_dir']}/weekly")
    weekly_dir.mkdir(parents=True, exist_ok=True)
    
    # 生成文件名
    if kb_key == "ai-latest-news":
        filename = f"weekly-{week_str}.md"
    elif kb_key == "game-development":
        filename = f"game-weekly-{week_str}.md"
    else:
        filename = f"health-weekly-{week_str}.md"
    
    filepath = weekly_dir / filename
    
    # 生成内容
    md_content = generate_weekly_md(kb_key, week_str, year, week_num, content_items)
    
    # 写入文件
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(md_content)
    
    return filepath


def collect_content(kb_key, week_str, year, week_num):
    """收集内容 - 调用实际的收集器 Agent"""
    config = KB_CONFIG[kb_key]
    
    print(f"正在收集 {config['name']} 第{week_num}期内容...")
    print(f"搜索关键词: {', '.join(config['search_queries'])}")
    
    # 导入并调用实际的收集器
    import sys
    sys.path.insert(0, "/workspace/projects/workspace/skills/content-collector/agents/collectors")
    
    try:
        if kb_key == "ai-latest-news":
            from ai_collector import AICollector
            collector = AICollector()
        elif kb_key == "game-development":
            from game_collector import GameCollector
            collector = GameCollector()
        elif kb_key == "healthy-living":
            from health_collector import HealthCollector
            collector = HealthCollector()
        else:
            print(f"⚠️ 未知的知识库: {kb_key}")
            return []
        
        # 调用收集器
        content_items = collector.search_content(week_str, year, week_num)
        
        # 分类内容
        for item in content_items:
            item["module"] = collector.classify_content(item)
        
        print(f"✅ 收集到 {len(content_items)} 条内容")
        return content_items
        
    except Exception as e:
        print(f"⚠️ 收集器调用失败: {e}")
        import traceback
        traceback.print_exc()
        return []


def main():
    parser = argparse.ArgumentParser(description="统一内容收集器")
    parser.add_argument("--kb", required=True, 
                       choices=["ai-latest-news", "game-development", "healthy-living"],
                       help="目标知识库")
    parser.add_argument("--week", default="current",
                       help="周次 (current 或 YYYY-WXX)")
    
    args = parser.parse_args()
    
    # 获取周信息
    week_str, year, week_num = get_week_info(args.week)
    print(f"📅 目标周次: {week_str} (第{week_num}周)")
    
    # 获取知识库配置
    config = KB_CONFIG[args.kb]
    print(f"📚 知识库: {config['icon']} {config['name']}")
    
    # 收集内容
    content_items = collect_content(args.kb, week_str, year, week_num)
    
    if not content_items:
        print("⚠️ 未收集到内容，请检查搜索配置或手动添加内容")
        # 创建空模板
        content_items = []
    
    # 分类内容
    for item in content_items:
        item["module"] = classify_content(item.get("title", ""), item.get("summary", ""), config)
    
    # 保存周刊
    filepath = save_weekly(args.kb, week_str, year, week_num, content_items)
    print(f"✅ 周刊已保存: {filepath}")
    
    # 输出统计
    module_counts = {}
    for item in content_items:
        m = item.get("module", "unknown")
        module_counts[m] = module_counts.get(m, 0) + 1
    
    print(f"\n📊 内容统计:")
    for module, count in module_counts.items():
        module_name = config["module_names"].get(module, module)
        print(f"  - {module_name}: {count}条")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
