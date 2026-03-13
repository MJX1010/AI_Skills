#!/usr/bin/env python3
"""
AI 内容每日收集脚本
自动搜索、抓取、整理 AI 相关内容
"""

import os
import sys
import json
import subprocess
import argparse
from datetime import datetime, timedelta
from pathlib import Path
from urllib.parse import urlparse

# 配置
SKILL_DIR = Path("/workspace/projects/workspace/skills/ai-content-collector")
OUTPUT_DIR = Path("/workspace/projects/workspace/memory/ai-content")
SOURCES_FILE = SKILL_DIR / "references" / "sources.md"

# 默认搜索查询
DEFAULT_QUERIES = [
    "AI artificial intelligence latest news",
    "LLM large language model new research",
    "machine learning latest papers",
    "OpenAI Google DeepMind announcement",
    "AI tools open source github",
]

CHINESE_QUERIES = [
    "人工智能最新进展",
    "大语言模型 LLM 新论文",
    "机器学习最新研究",
    "AI产品发布",
]

def ensure_dirs():
    """确保目录存在"""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUTPUT_DIR / "daily").mkdir(exist_ok=True)
    (OUTPUT_DIR / "archive").mkdir(exist_ok=True)

def search_content(query, limit=5):
    """使用 coze-web-search 搜索内容"""
    try:
        script_path = "/workspace/projects/workspace/skills/coze-web-search/scripts/search.ts"
        result = subprocess.run(
            ["npx", "ts-node", script_path, "--query", query, "--limit", str(limit)],
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
        if line and not line.startswith('http') and len(line) < 200:
            return line
    return "无标题"

def extract_summary(content, max_length=300):
    """提取摘要"""
    lines = content.split('\n')
    paragraphs = []
    for line in lines:
        line = line.strip()
        if line and not line.startswith('#') and len(line) > 50:
            paragraphs.append(line)
            if len(' '.join(paragraphs)) > max_length:
                break
    
    summary = ' '.join(paragraphs)[:max_length]
    if len(summary) == max_length:
        summary += "..."
    return summary

def categorize_content(url, title):
    """自动分类内容"""
    url_lower = url.lower()
    title_lower = title.lower()
    
    # 研究论文
    if any(x in url_lower for x in ['arxiv', 'paperswithcode', 'huggingface.co/papers']):
        return "研究论文"
    
    # 技术博客
    if any(x in url_lower for x in ['blog', 'openai', 'google', 'deepmind', 'research']):
        return "技术博客"
    
    # GitHub/开源
    if 'github.com' in url_lower:
        return "工具与开源"
    
    # 视频
    if any(x in url_lower for x in ['youtube', 'bilibili', 'youtu.be']):
        return "视频播客"
    
    # 新闻
    return "行业动态"

def collect_daily_content(date_str=None):
    """收集每日内容"""
    if date_str is None or date_str == "today":
        date_str = datetime.now().strftime("%Y-%m-%d")
    elif date_str == "yesterday":
        date_str = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    
    print(f"正在收集 {date_str} 的 AI 内容...")
    
    # 搜索内容
    all_results = []
    queries = DEFAULT_QUERIES + CHINESE_QUERIES
    
    for query in queries[:3]:  # 限制搜索次数
        print(f"  搜索: {query}")
        results = search_content(query, limit=3)
        # 这里需要解析搜索结果中的 URL
        # 简化处理：假设结果是文本，我们提取其中的 URL
        import re
        urls = re.findall(r'https?://[^\s<>"\')\]]+[^\s<>"\')\].,;!?]', results)
        for url in urls[:2]:  # 每个查询取前 2 个
            url = url.rstrip('.,;!?')
            if url not in [r['url'] for r in all_results]:
                all_results.append({'url': url, 'query': query})
    
    print(f"  发现 {len(all_results)} 个链接")
    
    # 抓取内容
    contents = []
    for item in all_results[:10]:  # 限制处理数量
        url = item['url']
        print(f"  抓取: {url[:60]}...")
        content = fetch_url(url)
        if content:
            title = extract_title(content)
            summary = extract_summary(content)
            category = categorize_content(url, title)
            
            contents.append({
                'url': url,
                'title': title,
                'summary': summary,
                'category': category,
                'date': date_str
            })
    
    print(f"  成功抓取 {len(contents)} 个内容")
    return contents, date_str

def generate_markdown(contents, date_str):
    """生成 Markdown 文档"""
    md = f"# AI 内容归档 - {date_str}\n\n"
    md += f"收集时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"
    md += f"共收集 {len(contents)} 条内容\n\n"
    
    # 按分类分组
    categories = {}
    for item in contents:
        cat = item.get('category', '其他')
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(item)
    
    # 目录
    md += "## 📑 目录\n\n"
    for cat in categories:
        md += f"- [{cat}](#{cat.lower().replace(' ', '-')})\n"
    md += "\n---\n\n"
    
    # 各分类内容
    for cat, items in categories.items():
        md += f"## {cat}\n\n"
        for i, item in enumerate(items, 1):
            md += f"### {i}. [{item['title']}]({item['url']})\n\n"
            md += f"- **摘要**: {item['summary']}\n"
            md += f"- **来源**: {urlparse(item['url']).netloc}\n\n"
        md += "---\n\n"
    
    return md

def save_content(contents, date_str, output_format="markdown"):
    """保存内容"""
    if output_format == "markdown":
        md_content = generate_markdown(contents, date_str)
        output_file = OUTPUT_DIR / "daily" / f"ai-content-{date_str}.md"
        output_file.write_text(md_content, encoding='utf-8')
        print(f"✅ 已保存到: {output_file}")
        return output_file
    
    # 也可以保存为 JSON
    json_file = OUTPUT_DIR / "archive" / f"{date_str}.json"
    json_file.write_text(json.dumps(contents, ensure_ascii=False, indent=2), encoding='utf-8')
    return json_file

def main():
    parser = argparse.ArgumentParser(description='Collect daily AI content')
    parser.add_argument('--date', default='today', help='Date to collect (today/yesterday/YYYY-MM-DD)')
    parser.add_argument('--output', default='markdown', choices=['markdown', 'json'], help='Output format')
    parser.add_argument('--limit', type=int, default=10, help='Max items to collect')
    
    args = parser.parse_args()
    
    ensure_dirs()
    
    # 收集内容
    contents, date_str = collect_daily_content(args.date)
    
    # 限制数量
    contents = contents[:args.limit]
    
    # 保存
    if contents:
        output_file = save_content(contents, date_str, args.output)
        print(f"\n📊 统计:")
        print(f"   日期: {date_str}")
        print(f"   内容数: {len(contents)}")
        
        # 分类统计
        categories = {}
        for item in contents:
            cat = item.get('category', '其他')
            categories[cat] = categories.get(cat, 0) + 1
        print(f"   分类: {', '.join([f'{k}({v})' for k, v in categories.items()])}")
    else:
        print("❌ 未收集到内容")

if __name__ == "__main__":
    main()
