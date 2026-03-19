#!/usr/bin/env python3
"""
微信文章归档助手
一键抓取微信文章并归档到层级结构
"""

import argparse
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

# 导入归档管理器
sys.path.insert(0, str(Path(__file__).parent))
from archive_manager import LinkArchiveManager

def fetch_wechat_article(url: str, method: str = "playwright") -> dict:
    """
    调用 fetch_wechat.py 抓取文章
    """
    fetch_script = Path(__file__).parent / "fetch_wechat.py"
    
    output_file = f"/tmp/wechat_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    try:
        result = subprocess.run(
            [
                "python3", str(fetch_script),
                url,
                "--method", method,
                "--format", "json",
                "--output", output_file
            ],
            capture_output=True,
            text=True,
            timeout=120
        )
        
        if result.returncode != 0:
            print(f"❌ 抓取失败: {result.stderr}")
            return None
        
        # 读取结果
        if Path(output_file).exists():
            data = json.loads(Path(output_file).read_text(encoding='utf-8'))
            return data
        
        return None
        
    except Exception as e:
        print(f"❌ 抓取异常: {e}")
        return None

def classify_article(article: dict) -> str:
    """
    根据文章内容自动分类
    """
    from classify_links import classify_link
    
    url = article.get('source_url', '')
    title = article.get('title', '')
    content = article.get('content', '')
    
    kb_key, confidence, reason = classify_link(url, title, content)
    
    print(f"📊 分类结果: {kb_key} (置信度: {confidence:.2f})")
    print(f"   原因: {reason}")
    
    return kb_key

def archive_article(article: dict, category: str = None, 
                   auto_classify: bool = False) -> Path:
    """
    归档微信文章
    
    Args:
        article: 文章数据
        category: 指定分类（如不提供则使用 auto_classify）
        auto_classify: 是否自动分类
    """
    manager = LinkArchiveManager()
    
    # 确定分类
    if auto_classify or category is None:
        kb_key = classify_article(article)
        # 映射到链接分类
        category_map = {
            "ai-latest-news": "wechat-articles",
            "game-dev": "wechat-articles",
            "healthy-living": "wechat-articles",
            "link-collection": "wechat-articles"
        }
        category = category_map.get(kb_key, "wechat-articles")
    
    # 提取信息
    url = article.get('source_url', '')
    title = article.get('title', '无标题')
    author = article.get('author', '')
    publish_time = article.get('publish_time', '')
    content = article.get('content', '')[:500]  # 摘要长度
    
    # 构建来源信息
    source = author if author else "微信公众号"
    if publish_time:
        source += f" · {publish_time}"
    
    # 添加到归档
    doc_path = manager.add_link(
        category=category,
        url=url,
        title=title,
        summary=content,
        source=source,
        tags=["微信文章", "公众号"]
    )
    
    return doc_path

def main():
    parser = argparse.ArgumentParser(description='微信文章归档助手')
    parser.add_argument('--url', '-u', help='微信文章URL')
    parser.add_argument('--file', '-f', help='已抓取的JSON文件路径')
    parser.add_argument('--method', '-m', default='playwright', 
                        choices=['requests', 'playwright', 'auto'],
                        help='抓取方法')
    parser.add_argument('--category', '-c', 
                        choices=['user-links', 'self-collected', 'wechat-articles'],
                        help='指定分类（不指定则自动分类）')
    parser.add_argument('--auto-classify', '-a', action='store_true',
                        help='自动根据内容分类')
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("微信文章归档助手")
    print("=" * 60)
    print()
    
    # 获取文章数据
    article = None
    
    if args.file:
        # 从文件读取
        print(f"📂 从文件读取: {args.file}")
        article = json.loads(Path(args.file).read_text(encoding='utf-8'))
    
    elif args.url:
        # 抓取文章
        print(f"🔗 抓取文章: {args.url}")
        article = fetch_wechat_article(args.url, args.method)
        
        if not article:
            print("❌ 抓取失败")
            sys.exit(1)
    
    else:
        print("❌ 请提供 --url 或 --file 参数")
        sys.exit(1)
    
    # 显示文章信息
    print(f"\n📄 文章信息:")
    print(f"   标题: {article.get('title', '无标题')}")
    print(f"   公众号: {article.get('author', '未知')}")
    print(f"   发布时间: {article.get('publish_time', '未知')}")
    print(f"   内容长度: {article.get('content_length', 0)} 字符")
    print()
    
    # 归档
    print("📦 开始归档...")
    doc_path = archive_article(
        article,
        category=args.category,
        auto_classify=args.auto_classify
    )
    
    print(f"\n✅ 归档完成!")
    print(f"   文档路径: {doc_path}")
    print(f"   知识库: 链接收藏 > 微信文章")

if __name__ == "__main__":
    main()
