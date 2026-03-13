#!/usr/bin/env python3
"""
从文本中提取所有 URL
"""

import re
import sys
import argparse

def extract_urls(text):
    """从文本中提取所有 URL"""
    # 匹配 http/https URL
    url_pattern = r'https?://[^\s<>"\')\]]+[^\s<>"\')\].,;!?]'
    urls = re.findall(url_pattern, text)
    
    # 去重并保持顺序
    seen = set()
    unique_urls = []
    for url in urls:
        url = url.rstrip('.,;!?')
        if url not in seen:
            seen.add(url)
            unique_urls.append(url)
    
    return unique_urls

def main():
    parser = argparse.ArgumentParser(description='Extract URLs from text')
    parser.add_argument('text', help='Text containing URLs')
    parser.add_argument('--json', action='store_true', help='Output as JSON')
    
    args = parser.parse_args()
    
    urls = extract_urls(args.text)
    
    if args.json:
        import json
        print(json.dumps(urls, indent=2, ensure_ascii=False))
    else:
        for url in urls:
            print(url)

if __name__ == "__main__":
    main()
