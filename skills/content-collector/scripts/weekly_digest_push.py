#!/usr/bin/env python3
"""
周刊精选推送脚本
每周六早上9点执行，汇总本周三个知识库的Top精选内容并推送
"""

import json
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List

# 知识库配置
KNOWLEDGE_BASES = {
    "ai-latest-news": {
        "name": "AI最新资讯",
        "space_id": "7616519632920251572",
        "icon": "🤖",
        "weekly_dir": "/workspace/projects/workspace/memory/ai-content/weekly",
        "top_count": 5,  # AI资讯取Top 5
        "modules": ["📰 行业资讯", "🛠️ 工具技巧", "📚 深度研究", "💡 案例分享"]
    },
    "game-dev": {
        "name": "游戏开发",
        "space_id": "7616735513310924004",
        "icon": "🎮",
        "weekly_dir": "/workspace/projects/workspace/memory/game-content/weekly",
        "top_count": 3,  # 游戏开发取Top 3
        "modules": ["🎮 游戏引擎", "🎯 游戏设计", "💻 开发技术", "🎨 美术资源", "🎵 音频音效", "🏆 独立游戏"]
    },
    "healthy-living": {
        "name": "健康生活",
        "space_id": "7616737910330510558",
        "icon": "🌱",
        "weekly_dir": "/workspace/projects/workspace/memory/health-content/weekly",
        "top_count": 3,  # 健康生活取Top 3
        "modules": ["🏃 运动健身", "🥗 饮食营养", "😊 心理健康", "💤 睡眠健康", "🏥 医疗资讯", "✨ 生活妙招"]
    }
}


def get_current_week_file(kb_config: Dict) -> Path:
    """获取本周的周刊文件路径"""
    now = datetime.now()
    year = now.year
    week = now.isocalendar()[1]
    
    weekly_file = Path(kb_config["weekly_dir"]) / f"weekly-{year}-W{week:02d}.md"
    
    # 如果没有weekly文件，尝试查找game-weekly或health-weekly格式
    if not weekly_file.exists() and kb_config["name"] == "游戏开发":
        weekly_file = Path(kb_config["weekly_dir"]) / f"game-weekly-{year}-W{week:02d}.md"
    elif not weekly_file.exists() and kb_config["name"] == "健康生活":
        weekly_file = Path(kb_config["weekly_dir"]) / f"health-weekly-{year}-W{week:02d}.md"
    
    return weekly_file


def parse_weekly_content(file_path: Path) -> List[Dict]:
    """解析周刊Markdown文件，提取文章列表"""
    if not file_path.exists():
        return []
    
    content = file_path.read_text(encoding='utf-8')
    articles = []
    
    # 解析 ### 标题行
    pattern = r'### \[(.+?)\]\((.+?)\)\n\n(.+?)(?=###|\Z)'
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
        
        # 评估质量分数
        quality_score = assess_quality(title, source, summary, tags)
        
        # 检测热点
        hot_keywords = ["openai", "gpt", "anthropic", "claude", "google", "发布", "突破", 
                       "unity", "unreal", "游戏引擎", "独立游戏",
                       "健康", "健身", "减肥", "养生"]
        is_hot = any(kw in title.lower() for kw in hot_keywords)
        
        articles.append({
            "title": title.strip(),
            "url": url.strip(),
            "summary": summary.strip()[:150] + "..." if len(summary) > 150 else summary.strip(),
            "source": source.strip(),
            "tags": tags,
            "quality_score": quality_score,
            "is_recommended": quality_score >= 75,
            "is_hot": is_hot
        })
    
    # 按质量分数排序
    articles.sort(key=lambda x: x["quality_score"], reverse=True)
    
    return articles


def assess_quality(title: str, source: str, summary: str, tags: List[str]) -> int:
    """评估内容质量分数(0-100)"""
    score = 50  # 基础分
    
    # 来源权重
    high_quality_sources = [
        "openai.com", "anthropic.com", "deepmind.google", "arxiv.org",
        "unity.com", "unrealengine.com", "godotengine.org",
        "dxy.com", "丁香医生", "who.int", "mayoclinic.org"
    ]
    for src in high_quality_sources:
        if src.lower() in source.lower():
            score += 20
            break
    
    # 标题质量
    if 10 <= len(title) <= 80:
        score += 10
    
    # 摘要长度
    if len(summary) >= 50:
        score += 10
    
    # 标签数量
    if len(tags) >= 2:
        score += 10
    
    return min(score, 100)


def generate_weekly_digest() -> Dict:
    """生成本周精选汇总"""
    now = datetime.now()
    year, week, _ = now.isocalendar()
    
    digest = {
        "date": now.strftime("%Y年%m月%d日"),
        "week_number": week,
        "year": year,
        "knowledge_bases": []
    }
    
    total_articles = 0
    total_top = 0
    
    for kb_key, kb_config in KNOWLEDGE_BASES.items():
        weekly_file = get_current_week_file(kb_config)
        
        # 获取所有文章
        articles = parse_weekly_content(weekly_file)
        
        # 取Top N
        top_count = kb_config["top_count"]
        top_articles = articles[:top_count] if articles else []
        
        kb_digest = {
            "key": kb_key,
            "name": kb_config["name"],
            "icon": kb_config["icon"],
            "space_id": kb_config["space_id"],
            "total_count": len(articles),
            "top_count": top_count,
            "top_articles": top_articles,
            "hot_count": sum(1 for a in articles if a["is_hot"]),
            "recommended_count": sum(1 for a in articles if a["is_recommended"])
        }
        
        digest["knowledge_bases"].append(kb_digest)
        total_articles += len(articles)
        total_top += len(top_articles)
    
    digest["total_articles"] = total_articles
    digest["total_top"] = total_top
    
    return digest


def generate_text_digest(digest: Dict) -> str:
    """生成文本格式的周刊精选"""
    lines = []
    
    lines.append("=" * 60)
    lines.append(f"📚 周刊精选 | 第{digest['week_number']}期 ({digest['date']})")
    lines.append("=" * 60)
    lines.append("")
    lines.append(f"📊 本周汇总: 共 {digest['total_articles']} 篇文章，精选 {digest['total_top']} 篇")
    lines.append("")
    
    for kb in digest["knowledge_bases"]:
        lines.append(f"{kb['icon']} **{kb['name']}** (本周{kb['total_count']}篇)")
        lines.append("-" * 50)
        
        if kb["top_articles"]:
            for i, article in enumerate(kb["top_articles"], 1):
                emoji = "🔥" if article["is_hot"] else "⭐"
                lines.append(f"{emoji} {i}. {article['title']}")
                lines.append(f"   📎 {article['url']}")
                if article["summary"]:
                    lines.append(f"   📝 {article['summary'][:80]}...")
                lines.append("")
        else:
            lines.append("   📝 本周暂无内容")
            lines.append("")
        
        # 添加知识库链接
        lines.append(f"   🔗 查看全部: https://xxx.feishu.cn/wiki/{kb['space_id']}")
        lines.append("")
    
    lines.append("=" * 60)
    lines.append("💡 每周六早上9点自动推送 | 每日18点自动收集")
    
    return "\n".join(lines)


def generate_feishu_card(digest: Dict) -> Dict:
    """生成飞书卡片"""
    card = {
        "config": {"wide_screen_mode": True},
        "header": {
            "title": {
                "tag": "plain_text",
                "content": f"📚 周刊精选 | 第{digest['week_number']}期"
            },
            "sub_title": {
                "tag": "plain_text",
                "content": f"{digest['date']} | 共{digest['total_articles']}篇文章"
            },
            "template": "blue"
        },
        "elements": []
    }
    
    # 各知识库精选
    for kb in digest["knowledge_bases"]:
        # 知识库标题
        card["elements"].append({
            "tag": "div",
            "text": {
                "tag": "lark_md",
                "content": f"{kb['icon']} **{kb['name']}** · Top {kb['top_count']}"
            }
        })
        
        if kb["top_articles"]:
            for i, article in enumerate(kb["top_articles"], 1):
                emoji = "🔥" if article["is_hot"] else f"{i}."
                content = f"{emoji} [{article['title'][:35]}...]({article['url']})"
                
                card["elements"].append({
                    "tag": "div",
                    "text": {
                        "tag": "lark_md",
                        "content": content
                    }
                })
        else:
            card["elements"].append({
                "tag": "div",
                "text": {
                    "tag": "lark_md",
                    "content": "📝 本周暂无内容"
                }
            })
        
        # 查看全部按钮
        card["elements"].append({
            "tag": "action",
            "actions": [{
                "tag": "button",
                "text": {"tag": "plain_text", "content": f"查看{kb['name']}"},
                "type": "primary",
                "url": f"https://xxx.feishu.cn/wiki/{kb['space_id']}"
            }]
        })
        
        card["elements"].append({"tag": "hr"})
    
    # 底部提示
    card["elements"].append({
        "tag": "note",
        "elements": [{
            "tag": "plain_text",
            "content": "💡 每周六早上9点自动推送 | 每日18点自动收集更新"
        }]
    })
    
    return card


def save_digest(digest: Dict, text_content: str, card: Dict):
    """保存周刊精选到文件"""
    output_dir = Path("/workspace/projects/workspace/memory/weekly-digest")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    today_str = datetime.now().strftime("%Y%m%d")
    
    # 保存JSON数据
    json_file = output_dir / f"digest-{today_str}.json"
    json_file.write_text(
        json.dumps(digest, ensure_ascii=False, indent=2),
        encoding='utf-8'
    )
    
    # 保存文本报告
    text_file = output_dir / f"digest-{today_str}.txt"
    text_file.write_text(text_content, encoding='utf-8')
    
    # 保存飞书卡片
    card_file = output_dir / f"card-{today_str}.json"
    card_file.write_text(
        json.dumps(card, ensure_ascii=False, indent=2),
        encoding='utf-8'
    )
    
    return json_file, text_file, card_file


def main():
    """主函数"""
    print("=" * 60)
    print("📚 周刊精选推送")
    print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 60)
    print()
    
    # 生成精选汇总
    digest = generate_weekly_digest()
    
    # 生成文本报告
    text_digest = generate_text_digest(digest)
    print(text_digest)
    print()
    
    # 生成飞书卡片
    card = generate_feishu_card(digest)
    print("✅ 飞书卡片已生成")
    
    # 保存到文件
    json_file, text_file, card_file = save_digest(digest, text_digest, card)
    
    print(f"\n✅ 周刊精选已保存:")
    print(f"   数据: {json_file}")
    print(f"   文本: {text_file}")
    print(f"   卡片: {card_file}")
    
    # 统计信息
    print(f"\n📊 本周统计:")
    print(f"   总文章数: {digest['total_articles']}")
    print(f"   精选数量: {digest['total_top']}")
    for kb in digest["knowledge_bases"]:
        print(f"   {kb['icon']} {kb['name']}: {kb['total_count']}篇 (精选{kb['top_count']}篇)")
    
    return digest, card


if __name__ == "__main__":
    main()
