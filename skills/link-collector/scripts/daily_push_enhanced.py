#!/usr/bin/env python3
"""
知识库日报推送脚本 - 增强版
每天早上8点推送知识库更新，包含质量筛选和推荐
"""

import json
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Tuple

# 知识库配置
KNOWLEDGE_BASES = {
    "ai-latest-news": {
        "name": "AI最新资讯",
        "space_id": "7616519632920251572",
        "icon": "🤖",
        "weekly_dir": "/workspace/projects/workspace/memory/ai-content/weekly",
        "modules": ["📰 行业资讯", "🛠️ 工具技巧", "📚 深度研究", "💡 案例分享"]
    },
    "game-dev": {
        "name": "游戏开发",
        "space_id": "7616735513310924004",
        "icon": "🎮",
        "weekly_dir": "/workspace/projects/workspace/memory/game-content/weekly",
        "modules": ["🎮 游戏引擎", "🎯 游戏设计", "💻 开发技术", "🎨 美术资源", "🎵 音频音效", "🏆 独立游戏"]
    },
    "healthy-living": {
        "name": "健康生活",
        "space_id": "7616737910330510558",
        "icon": "🌱",
        "weekly_dir": "/workspace/projects/workspace/memory/health-content/weekly",
        "modules": ["🏃 运动健身", "🥗 饮食营养", "😊 心理健康", "💤 睡眠健康", "🏥 医疗资讯", "✨ 生活妙招"]
    }
}


def parse_weekly_content(file_path: Path) -> List[Dict]:
    """
    解析周刊Markdown文件，提取文章列表
    """
    content = file_path.read_text(encoding='utf-8')
    articles = []
    
    # 简单解析：提取 ### 标题行（支持带序号格式如 ### 1. [标题](URL)）
    pattern = r'###\s*(?:\d+\.\s*)?\[(.+?)\]\((.+?)\)\n\n(.+?)(?=###|\Z)'
    matches = re.findall(pattern, content, re.DOTALL)
    
    for match in matches:
        title, url, body = match
        
        # 提取摘要
        summary_match = re.search(r'\*\*摘要\*\*: (.+?)(?:\n|$)', body)
        summary = summary_match.group(1) if summary_match else ""
        
        # 提取来源
        source_match = re.search(r'> 来源：\[(.+?)\]', body)
        source = source_match.group(1) if source_match else ""
        
        # 提取标签
        tags_match = re.search(r'\*\*标签\*\*: (.+?)(?:\n|$)', body)
        tags = tags_match.group(1).split(", ") if tags_match else []
        
        # 质量评估
        quality_score = assess_quality(title, source, summary, tags)
        
        articles.append({
            "title": title.strip(),
            "url": url.strip(),
            "summary": summary.strip()[:100] + "..." if len(summary) > 100 else summary.strip(),
            "source": source.strip(),
            "tags": tags,
            "quality_score": quality_score,
            "is_recommended": quality_score >= 80,
            "is_hot": any(kw in title.lower() for kw in ["openai", "gpt", "google", "发布", "突破"])
        })
    
    return articles


def assess_quality(title: str, source: str, summary: str, tags: List[str]) -> int:
    """
    评估内容质量分数(0-100)
    """
    score = 50  # 基础分
    
    # 来源权重
    high_quality_sources = ["openai.com", "anthropic.com", "deepmind.google", 
                            "arxiv.org", "techcrunch.com", "theverge.com",
                            "unity.com", "unrealengine.com",
                            "dxy.com", "丁香医生"]
    for src in high_quality_sources:
        if src.lower() in source.lower():
            score += 20
            break
    
    # 标题质量
    if len(title) >= 10 and len(title) <= 100:
        score += 10
    
    # 摘要完整性
    if len(summary) >= 50:
        score += 10
    
    # 标签丰富度
    if len(tags) >= 2:
        score += 10
    
    return min(score, 100)


def get_kb_updates(kb_key: str, kb_config: Dict) -> Dict:
    """
    获取知识库更新内容
    """
    weekly_dir = Path(kb_config["weekly_dir"])
    if not weekly_dir.exists():
        return None
    
    # 查找最新的周刊
    files = sorted(weekly_dir.glob("*.md"), reverse=True)
    if not files:
        return None
    
    latest_file = files[0]
    latest_date = datetime.fromtimestamp(latest_file.stat().st_mtime)
    today = datetime.now()
    
    # 检查是否是最近3天内更新
    if (today - latest_date).days > 3:
        return None
    
    # 解析内容
    articles = parse_weekly_content(latest_file)
    
    # 筛选推荐内容
    recommended = [a for a in articles if a["is_recommended"]]
    hot = [a for a in articles if a["is_hot"]]
    
    # 取Top 5
    top_articles = sorted(articles, key=lambda x: x["quality_score"], reverse=True)[:5]
    
    return {
        "kb_key": kb_key,
        "name": kb_config["name"],
        "icon": kb_config["icon"],
        "space_id": kb_config["space_id"],
        "update_date": latest_date.strftime("%Y-%m-%d"),
        "total_count": len(articles),
        "recommended_count": len(recommended),
        "hot_count": len(hot),
        "top_articles": top_articles,
        "week_number": latest_date.isocalendar()[1]
    }


def generate_daily_report() -> Dict:
    """
    生成日报
    """
    today = datetime.now()
    today_str = today.strftime("%Y年%m月%d日")
    weekday = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"][today.weekday()]
    
    # 收集所有知识库更新
    updates = []
    for kb_key, kb_config in KNOWLEDGE_BASES.items():
        update = get_kb_updates(kb_key, kb_config)
        if update:
            updates.append(update)
    
    report = {
        "date": today_str,
        "weekday": weekday,
        "total_kbs": len(updates),
        "total_articles": sum(u["total_count"] for u in updates),
        "total_recommended": sum(u["recommended_count"] for u in updates),
        "updates": updates
    }
    
    return report


def generate_text_report(report: Dict) -> str:
    """
    生成文本格式报告
    """
    lines = []
    lines.append("📚 知识库日报")
    lines.append(f"📅 {report['date']} {report['weekday']}")
    lines.append("=" * 50)
    lines.append("")
    
    if report['total_kbs'] == 0:
        lines.append("📝 今日暂无新内容更新")
        lines.append("")
        lines.append("💡 提示：每周五下午6点自动更新周刊")
    else:
        lines.append(f"🆕 今日更新 {report['total_kbs']} 个知识库")
        lines.append(f"📊 共 {report['total_articles']} 篇文章")
        lines.append(f"⭐ 精选推荐 {report['total_recommended']} 篇")
        lines.append("")
        
        for update in report['updates']:
            lines.append(f"{update['icon']} **{update['name']}**")
            lines.append(f"   周刊: 第{update['week_number']}期 ({update['update_date']})")
            lines.append(f"   文章: {update['total_count']}篇 | 推荐: {update['recommended_count']}篇")
            
            if update['hot_count'] > 0:
                lines.append(f"   🔥 热点: {update['hot_count']}篇")
            
            lines.append("   ⭐ 精选内容:")
            for i, article in enumerate(update['top_articles'][:3], 1):
                prefix = "🔥" if article['is_hot'] else "⭐" if article['is_recommended'] else "•"
                lines.append(f"      {prefix} {article['title'][:40]}...")
            
            lines.append("")
    
    lines.append("=" * 50)
    lines.append("💡 每日8点自动推送 | 周五更新周刊")
    
    return "\n".join(lines)


def generate_feishu_card(report: Dict) -> Dict:
    """
    生成飞书卡片
    """
    card = {
        "config": {"wide_screen_mode": True},
        "header": {
            "title": {
                "tag": "plain_text",
                "content": f"📚 知识库日报 | {report['date']}"
            },
            "template": "blue"
        },
        "elements": []
    }
    
    # 统计信息
    if report['total_kbs'] > 0:
        card["elements"].append({
            "tag": "div",
            "text": {
                "tag": "lark_md",
                "content": f"**📊 今日统计**\n知识库: {report['total_kbs']}个 | 文章: {report['total_articles']}篇 | 推荐: {report['total_recommended']}篇"
            }
        })
        card["elements"].append({"tag": "hr"})
        
        # 各知识库详情
        for update in report['updates']:
            content = f"{update['icon']} **{update['name']}**\n"
            content += f"第{update['week_number']}期 · {update['total_count']}篇文章"
            
            if update['hot_count'] > 0:
                content += f" · 🔥{update['hot_count']}篇热点"
            
            card["elements"].append({
                "tag": "div",
                "text": {"tag": "lark_md", "content": content}
            })
            
            # 精选文章
            for article in update['top_articles'][:2]:
                emoji = "🔥" if article['is_hot'] else "⭐" if article['is_recommended'] else "•"
                card["elements"].append({
                    "tag": "div",
                    "text": {
                        "tag": "lark_md",
                        "content": f"{emoji} [{article['title'][:30]}...]({article['url']})"
                    }
                })
            
            # 查看全部按钮
            card["elements"].append({
                "tag": "action",
                "actions": [{
                    "tag": "button",
                    "text": {"tag": "plain_text", "content": "查看全部"},
                    "type": "default",
                    "url": f"https://xxx.feishu.cn/wiki/{update['space_id']}"
                }]
            })
            card["elements"].append({"tag": "hr"})
    else:
        card["elements"].append({
            "tag": "div",
            "text": {"tag": "lark_md", "content": "📝 今日暂无新内容更新\n\n💡 每周五下午6点自动更新周刊"}
        })
    
    return card


def main():
    """主函数"""
    print("=" * 60)
    print("📚 知识库日报推送 - 增强版")
    print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 60)
    print()
    
    # 生成报告
    report = generate_daily_report()
    
    # 生成文本报告
    text_report = generate_text_report(report)
    print(text_report)
    print()
    
    # 生成飞书卡片
    card = generate_feishu_card(report)
    print("✅ 飞书卡片已生成")
    
    # 保存到文件
    output_dir = Path("/workspace/projects/workspace/memory/daily-push")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    today_str = datetime.now().strftime("%Y%m%d")
    
    # 保存文本
    text_file = output_dir / f"report-{today_str}.txt"
    text_file.write_text(text_report, encoding='utf-8')
    
    # 保存JSON
    json_file = output_dir / f"report-{today_str}.json"
    json_file.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    
    # 保存飞书卡片
    card_file = output_dir / f"card-{today_str}.json"
    card_file.write_text(json.dumps(card, ensure_ascii=False, indent=2), encoding='utf-8')
    
    print(f"\n✅ 报告已保存:")
    print(f"   文本: {text_file}")
    print(f"   JSON: {json_file}")
    print(f"   卡片: {card_file}")
    
    return report, card


if __name__ == "__main__":
    main()
