#!/usr/bin/env python3
"""
游戏开发周刊收集脚本
参考阮一峰《科技爱好者周刊》格式
以周为单位收集、整理游戏开发相关内容
"""

import os
import sys
import json
import subprocess
import argparse
import re
from datetime import datetime, timedelta
from pathlib import Path
from urllib.parse import urlparse

# 配置
SKILL_DIR = Path("/workspace/projects/workspace/skills/game-content-collector")
OUTPUT_DIR = Path("/workspace/projects/workspace/memory/game-content")
WEEKLY_DIR = OUTPUT_DIR / "weekly"

# 默认搜索查询
DEFAULT_QUERIES = [
    "game development news Unity Unreal",
    "indie game releases this week",
    "gamedev tutorials tips",
    "game industry news",
]

CHINESE_QUERIES = [
    "游戏开发 Unity 最新动态",
    "独立游戏发布推荐",
    "游戏设计 开发技巧",
    "游戏引擎 Godot",
]

def get_week_info(date_obj=None):
    """获取周信息"""
    if date_obj is None:
        date_obj = datetime.now()
    
    # 获取当前是第几周（从年初开始）
    week_number = date_obj.isocalendar()[1]
    year = date_obj.year
    
    # 计算本周五的日期（周刊发布日）
    friday = date_obj + timedelta(days=(4 - date_obj.weekday()) % 7)
    
    return {
        'year': year,
        'week': week_number,
        'issue_number': week_number,  # 第X期
        'friday_date': friday.strftime("%Y-%m-%d"),
        'friday_display': friday.strftime("%Y年%m月%d日"),
        'week_range': f"{friday.strftime('%m.%d')}"
    }

def search_content(query, limit=5):
    """使用 coze-web-search 搜索内容"""
    try:
        script_path = "/workspace/projects/workspace/skills/coze-web-search/scripts/search.ts"
        result = subprocess.run(
            ["npx", "ts-node", script_path, "--query", query, "--limit", str(limit), "--time-range", "1w"],
            capture_output=True,
            text=True,
            timeout=60
        )
        return result.stdout
    except Exception as e:
        print(f"搜索失败 '{query}': {e}", file=sys.stderr)
        return ""

def fetch_url(url):
    """抓取 URL 内容"""
    try:
        script_path = "/workspace/projects/workspace/skills/coze-web-fetch/scripts/fetch.ts"
        result = subprocess.run(
            ["npx", "ts-node", script_path, "-u", url, "--format", "markdown"],
            capture_output=True,
            text=True,
            timeout=60
        )
        return result.stdout
    except Exception as e:
        print(f"抓取失败 '{url}': {e}", file=sys.stderr)
        return ""

def extract_title(content):
    """从内容中提取标题"""
    lines = content.split('\n')
    for line in lines:
        line = line.strip()
        if line.startswith('# '):
            return line[2:].strip()
        if line.startswith('## '):
            return line[3:].strip()
    return "无标题"

def extract_summary(content, max_length=200):
    """提取摘要"""
    lines = content.split('\n')
    paragraphs = []
    for line in lines:
        line = line.strip()
        if line and not line.startswith('#') and len(line) > 30:
            paragraphs.append(line)
            if len(' '.join(paragraphs)) > max_length:
                break
    
    summary = ' '.join(paragraphs)[:max_length]
    if len(summary) == max_length:
        summary += "..."
    return summary

def categorize_content(url, title):
    """分类游戏开发内容"""
    url_lower = url.lower()
    title_lower = title.lower()
    
    # 游戏引擎
    if any(x in url_lower for x in ['unity.com', 'unrealengine.com', 'godotengine.org']):
        return "游戏引擎"
    
    # 游戏设计
    if any(x in title_lower for x in ['design', 'gamedesign', '游戏设计', '机制']):
        return "游戏设计"
    
    # 开发技术
    if any(x in title_lower for x in ['programming', 'dev', 'code', '编程', '技术']):
        return "开发技术"
    
    # 美术资源
    if any(x in title_lower for x in ['art', 'graphics', '美术', '画面', 'shader']):
        return "美术资源"
    
    # 音频音效
    if any(x in title_lower for x in ['audio', 'sound', 'music', '音效', '音乐']):
        return "音频音效"
    
    # 独立游戏
    if any(x in url_lower for x in ['indie', 'itch.io', 'indienova']):
        return "独立游戏"
    
    # 行业资讯
    return "行业资讯"

def get_domain_name(url):
    """获取域名"""
    parsed = urlparse(url)
    domain = parsed.netloc
    if domain.startswith('www.'):
        domain = domain[4:]
    return domain

def collect_weekly_content(week_info):
    """收集本周内容"""
    print(f"正在收集 第{week_info['issue_number']}期（{week_info['friday_display']}）的游戏开发内容...")
    
    all_results = []
    queries = DEFAULT_QUERIES + CHINESE_QUERIES
    
    for query in queries:
        print(f"  搜索: {query}")
        results = search_content(query, limit=5)
        
        # 提取 URL
        urls = re.findall(r'https?://[^\s<>"\')\]]+[^\s<>"\')\].,;!?]', results)
        for url in urls[:3]:
            url = url.rstrip('.,;!?')
            # 去重
            if url not in [r['url'] for r in all_results]:
                all_results.append({'url': url, 'query': query})
    
    print(f"  发现 {len(all_results)} 个链接")
    
    # 抓取内容
    contents = {
        '游戏引擎': [],
        '游戏设计': [],
        '开发技术': [],
        '美术资源': [],
        '音频音效': [],
        '独立游戏': [],
        '行业资讯': []
    }
    
    for item in all_results[:15]:  # 限制处理数量
        url = item['url']
        print(f"  抓取: {url[:50]}...")
        
        content = fetch_url(url)
        if content:
            title = extract_title(content)
            summary = extract_summary(content)
            category = categorize_content(url, title)
            domain = get_domain_name(url)
            
            contents[category].append({
                'url': url,
                'title': title,
                'summary': summary,
                'domain': domain,
                'date': week_info['friday_date']
            })
    
    total = sum(len(v) for v in contents.values())
    print(f"  成功抓取 {total} 个内容")
    return contents, week_info

def generate_weekly_markdown(contents, week_info):
    """生成周刊 Markdown（参考阮一峰格式）"""
    issue = week_info['issue_number']
    date = week_info['friday_display']
    week_range = week_info['week_range']
    
    md = f"# 游戏开发周刊：第{issue}期（{date}）\n\n"
    
    # 封面图占位
    md += f"![第{issue}期封面](封面图URL)\n\n"
    
    # 刊头
    md += "---\n\n"
    md += f"**本期编辑** | OpenClaw AI  \n"
    md += f"**出版日期** | {date}  \n"
    md += f"**总第{issue}期**\n\n"
    md += "---\n\n"
    
    # 本周话题
    md += "## 📌 本周话题\n\n"
    md += "本周最值得关注的游戏开发动态或行业趋势...\n\n"
    md += "（人工编辑补充）\n\n"
    md += "---\n\n"
    
    # 游戏引擎
    if contents['游戏引擎']:
        md += "## 🎮 游戏引擎\n\n"
        for i, item in enumerate(contents['游戏引擎'][:5], 1):
            md += f"### {i}. [{item['title']}]({item['url']})\n\n"
            md += f"{item['summary']}\n\n"
            md += f"> 来源：[{item['domain']}]({item['url']})\n\n"
        md += "---\n\n"
    
    # 游戏设计
    if contents['游戏设计']:
        md += "## 🎯 游戏设计\n\n"
        for i, item in enumerate(contents['游戏设计'][:4], 1):
            md += f"### {i}. [{item['title']}]({item['url']})\n\n"
            md += f"{item['summary']}\n\n"
            md += f"> 来源：[{item['domain']}]({item['url']})\n\n"
        md += "---\n\n"
    
    # 开发技术
    if contents['开发技术']:
        md += "## 💻 开发技术\n\n"
        for i, item in enumerate(contents['开发技术'][:4], 1):
            md += f"### {i}. [{item['title']}]({item['url']})\n\n"
            md += f"{item['summary']}\n\n"
            md += f"> 来源：[{item['domain']}]({item['url']})\n\n"
        md += "---\n\n"
    
    # 美术资源
    if contents['美术资源']:
        md += "## 🎨 美术资源\n\n"
        for i, item in enumerate(contents['美术资源'][:3], 1):
            md += f"### {i}. [{item['title']}]({item['url']})\n\n"
            md += f"{item['summary']}\n\n"
            md += f"> 来源：[{item['domain']}]({item['url']})\n\n"
        md += "---\n\n"
    
    # 独立游戏
    if contents['独立游戏']:
        md += "## 🏆 独立游戏\n\n"
        for i, item in enumerate(contents['独立游戏'][:5], 1):
            md += f"### {i}. [{item['title']}]({item['url']})\n\n"
            md += f"{item['summary']}\n\n"
            md += f"> 来源：[{item['domain']}]({item['url']})\n\n"
        md += "---\n\n"
    
    # 行业资讯
    if contents['行业资讯']:
        md += "## 📊 行业资讯\n\n"
        for i, item in enumerate(contents['行业资讯'][:3], 1):
            md += f"### {i}. [{item['title']}]({item['url']})\n\n"
            md += f"{item['summary']}\n\n"
            md += f"> 来源：[{item['domain']}]({item['url']})\n\n"
        md += "---\n\n"
    
    # 本周金句
    md += "## 💬 本周金句\n\n"
    md += "> （人工编辑补充最有价值的一句话）\n\n"
    md += "---\n\n"
    
    # 链接引用汇总
    md += "## 🔗 链接引用\n\n"
    md += "本期周刊涉及的所有链接：\n\n"
    md += "| 序号 | 标题 | 来源 |\n"
    md += "|------|------|------|\n"
    
    idx = 1
    for category in ['游戏引擎', '游戏设计', '开发技术', '美术资源', '音频音效', '独立游戏', '行业资讯']:
        for item in contents[category]:
            title_short = item['title'][:30] + "..." if len(item['title']) > 30 else item['title']
            md += f"| {idx} | [{title_short}]({item['url']}) | {item['domain']} |\n"
            idx += 1
    
    md += "\n---\n\n"
    md += "## 📮 订阅\n\n"
    md += "- 飞书知识库：[游戏开发](https://xxx.feishu.cn/wiki/xxx)\n"
    md += "- GitHub：[MJX1010/AI_Skills](https://github.com/MJX1010/AI_Skills)\n\n"
    
    md += "---\n\n"
    md += "*本期周刊由 OpenClaw AI 自动生成，部分内容由人工编辑审核*\n"
    
    return md

def save_weekly_content(contents, week_info):
    """保存周刊内容"""
    WEEKLY_DIR.mkdir(parents=True, exist_ok=True)
    
    # Markdown 格式
    md_content = generate_weekly_markdown(contents, week_info)
    output_file = WEEKLY_DIR / f"game-weekly-{week_info['year']}-W{week_info['week']:02d}.md"
    output_file.write_text(md_content, encoding='utf-8')
    print(f"✅ 周刊已保存: {output_file}")
    
    # JSON 格式（便于后续处理）
    json_file = WEEKLY_DIR / f"game-weekly-{week_info['year']}-W{week_info['week']:02d}.json"
    json_file.write_text(
        json.dumps({
            'week_info': week_info,
            'contents': contents
        }, ensure_ascii=False, indent=2),
        encoding='utf-8'
    )
    
    return output_file, json_file

def main():
    parser = argparse.ArgumentParser(description='Collect weekly game dev content (周刊模式)')
    parser.add_argument('--week', default='current', help='Week to collect (current/YYYY-Wxx)')
    parser.add_argument('--year', type=int, default=None, help='Year')
    
    args = parser.parse_args()
    
    # 计算周信息
    if args.week == 'current':
        week_info = get_week_info()
    else:
        # 解析 YYYY-Wxx 格式
        try:
            year, week = args.week.split('-W')
            date_obj = datetime.strptime(f"{year}-{week}-1", "%Y-%W-%w")
            week_info = get_week_info(date_obj)
        except:
            print("周格式错误，使用当前周")
            week_info = get_week_info()
    
    print(f"=" * 60)
    print(f"游戏开发周刊 - 第{week_info['issue_number']}期")
    print(f"出版日期: {week_info['friday_display']}")
    print(f"=" * 60)
    print()
    
    # 收集内容
    contents, week_info = collect_weekly_content(week_info)
    
    # 保存
    md_file, json_file = save_weekly_content(contents, week_info)
    
    # 统计
    print(f"\n📊 本期统计:")
    print(f"   期数: 第{week_info['issue_number']}期")
    print(f"   日期: {week_info['friday_display']}")
    for cat, items in contents.items():
        if items:
            print(f"   {cat}: {len(items)} 条")
    
    print(f"\n✨ 周刊已生成！")
    print(f"   Markdown: {md_file}")
    print(f"   JSON: {json_file}")
    
    return md_file

if __name__ == "__main__":
    main()
