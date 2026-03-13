#!/usr/bin/env python3
"""
批量抓取链接并生成 Markdown 整理文档
"""

import sys
import json
import subprocess
import argparse
from pathlib import Path
from datetime import datetime
from urllib.parse import urlparse

def fetch_url(url):
    """使用 coze-web-fetch 抓取单个 URL"""
    try:
        script_path = "/workspace/projects/workspace/skills/coze-web-fetch/scripts/fetch.ts"
        result = subprocess.run(
            ["npx", "ts-node", script_path, "-u", url, "--format", "json"],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        # 解析 JSON 输出
        output = result.stdout
        # 找到 JSON 部分（可能在多行输出中）
        lines = output.strip().split('\n')
        for line in lines:
            line = line.strip()
            if line and line.startswith('{'):
                try:
                    data = json.loads(line)
                    return data
                except:
                    continue
        
        return None
    except Exception as e:
        print(f"Error fetching {url}: {e}", file=sys.stderr)
        return None

def extract_title(data):
    """从抓取数据中提取标题"""
    if not data:
        return "无标题"
    
    # 尝试不同字段
    title = data.get('title', '')
    if not title and 'content' in data:
        # 从内容第一行提取
        content = data['content']
        lines = content.split('\n')
        for line in lines:
            line = line.strip()
            if line and not line.startswith('http'):
                return line[:100]
    
    return title or "无标题"

def extract_summary(data, max_length=200):
    """从抓取数据中提取摘要"""
    if not data:
        return "无法获取内容"
    
    content = data.get('content', '')
    if not content:
        return "无内容"
    
    # 清理内容
    lines = content.split('\n')
    paragraphs = []
    for line in lines:
        line = line.strip()
        if line and not line.startswith('#') and len(line) > 20:
            paragraphs.append(line)
    
    if paragraphs:
        summary = paragraphs[0]
        if len(summary) > max_length:
            summary = summary[:max_length] + "..."
        return summary
    
    return "无可用摘要"

def get_domain(url):
    """获取域名"""
    try:
        parsed = urlparse(url)
        return parsed.netloc
    except:
        return "未知来源"

def categorize_url(url, title, content):
    """简单分类链接"""
    url_lower = url.lower()
    title_lower = title.lower()
    
    # 视频网站
    if any(x in url_lower for x in ['youtube', 'bilibili', 'youtu.be', 'vimeo']):
        return "视频"
    
    # 文档/API
    if any(x in url_lower for x in ['docs.', 'api.', 'documentation']):
        return "文档"
    
    # GitHub
    if 'github.com' in url_lower:
        return "代码仓库"
    
    # 工具/产品
    if any(x in title_lower for x in ['tool', 'app', '软件', '工具']):
        return "工具"
    
    # 默认文章
    return "文章"

def generate_markdown(urls_data, title="链接收藏"):
    """生成 Markdown 文档"""
    date_str = datetime.now().strftime("%Y-%m-%d")
    
    md = f"# {title} - {date_str}\n\n"
    md += f"共收集 {len(urls_data)} 个链接\n\n"
    
    # 按分类分组
    categories = {}
    for item in urls_data:
        cat = item.get('category', '其他')
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(item)
    
    # 目录
    md += "## 📑 目录\n\n"
    for cat in categories:
        md += f"- [{cat}](#{cat.lower()})\n"
    md += "\n---\n\n"
    
    # 各分类内容
    for cat, items in categories.items():
        md += f"## {cat}\n\n"
        for i, item in enumerate(items, 1):
            md += f"### {i}. {item['title']}\n\n"
            md += f"- **链接**: {item['url']}\n"
            md += f"- **来源**: {item['domain']}\n"
            md += f"- **摘要**: {item['summary']}\n\n"
        md += "---\n\n"
    
    return md

def main():
    parser = argparse.ArgumentParser(description='Collect links into markdown document')
    parser.add_argument('--urls', required=True, help='Comma-separated URLs')
    parser.add_argument('--output', '-o', default='links-collection.md', help='Output file')
    parser.add_argument('--title', '-t', default='链接收藏', help='Document title')
    
    args = parser.parse_args()
    
    urls = [u.strip() for u in args.urls.split(',') if u.strip()]
    
    print(f"正在处理 {len(urls)} 个链接...")
    
    urls_data = []
    for url in urls:
        print(f"  抓取: {url}")
        data = fetch_url(url)
        
        item = {
            'url': url,
            'title': extract_title(data),
            'summary': extract_summary(data),
            'domain': get_domain(url),
            'category': categorize_url(url, extract_title(data), data.get('content', '') if data else '')
        }
        urls_data.append(item)
    
    # 生成文档
    markdown = generate_markdown(urls_data, args.title)
    
    # 保存
    output_path = Path(args.output)
    output_path.write_text(markdown, encoding='utf-8')
    
    print(f"\n✅ 已保存到: {output_path}")
    print(f"   共整理 {len(urls_data)} 个链接")
    
    # 显示分类统计
    categories = {}
    for item in urls_data:
        cat = item['category']
        categories[cat] = categories.get(cat, 0) + 1
    print(f"   分类: {', '.join([f'{k}({v})' for k, v in categories.items()])}")

if __name__ == "__main__":
    main()
