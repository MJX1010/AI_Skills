#!/usr/bin/env python3
"""
微信文章归档助手
一键抓取微信文章并归档到知识库
"""

import argparse
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

# 配置
WORKSPACE = Path("/workspace/projects/workspace")
MEMORY_DIR = WORKSPACE / "memory"
STATE_DIR = MEMORY_DIR / "state"
COLLECTED_URLS_FILE = STATE_DIR / "collected-urls.json"

# 知识库配置
KB_CONFIG = {
    "ai-latest-news": {
        "name": "🤖 AI最新资讯",
        "space_id": "7616519632920251572",
        "keywords": ["ai", "人工智能", "gpt", "claude", "openai", "anthropic", "llm", "大模型", "机器学习"]
    },
    "game-development": {
        "name": "🎮 游戏开发",
        "space_id": "7616735513310924004",
        "keywords": ["game", "游戏", "unity", "unreal", "godot", "indie", "gamedev"]
    },
    "healthy-living": {
        "name": "🌱 健康生活",
        "space_id": "7616737910330510558",
        "keywords": ["健康", "health", "健身", "运动", "饮食", "心理", "生活"]
    }
}


def ensure_dirs():
    """确保目录存在"""
    STATE_DIR.mkdir(parents=True, exist_ok=True)


def load_collected_urls():
    """加载已收集的URL"""
    if COLLECTED_URLS_FILE.exists():
        return json.loads(COLLECTED_URLS_FILE.read_text())
    return {"urls": {}}


def save_collected_urls(data):
    """保存已收集的URL"""
    COLLECTED_URLS_FILE.write_text(json.dumps(data, indent=2))


def is_url_collected(url: str) -> bool:
    """检查URL是否已收集"""
    data = load_collected_urls()
    return url in data.get("urls", {})


def mark_url_collected(url: str, kb: str, title: str):
    """标记URL为已收集"""
    data = load_collected_urls()
    data["urls"][url] = {
        "first_collected": datetime.now().isoformat(),
        "kb": kb,
        "title": title
    }
    save_collected_urls(data)


def fetch_wechat_article(url: str, method: str = "playwright") -> dict:
    """调用 fetch_wechat.py 抓取文章"""
    fetch_script = Path(__file__).parent / "fetch_wechat.py"
    
    try:
        result = subprocess.run(
            [
                "python3", str(fetch_script),
                url,
                "--method", method,
                "--format", "markdown"
            ],
            capture_output=True,
            text=True,
            timeout=120
        )
        
        if result.returncode != 0:
            print(f"❌ 抓取失败: {result.stderr}")
            return None
        
        # 解析输出
        output = result.stdout
        lines = output.split("\n")
        
        title = ""
        content = ""
        author = ""
        
        # 优先从 markdown 格式解析标题 (# 开头的标题)
        for i, line in enumerate(lines):
            # Markdown 格式标题: # 标题
            if line.startswith("# ") and not title:
                title = line[2:].strip()
            # 旧格式兼容: 标题: xxx
            elif line.startswith("标题:") and not title:
                title = line.replace("标题:", "").strip()
            elif line.startswith("**公众号**:") or line.startswith("公众号:"):
                author = line.split(":", 1)[1].strip().strip('*')
        
        # 如果没找到标题，使用默认
        if not title:
            title = "微信文章"
        
        return {
            "title": title,
            "content": output,
            "author": author,
            "url": url
        }
        
    except Exception as e:
        print(f"❌ 抓取异常: {e}")
        return None


def classify_content(title: str, content: str) -> tuple:
    """分类内容到知识库"""
    text = (title + " " + content).lower()
    
    scores = {}
    for kb_key, config in KB_CONFIG.items():
        score = sum(1 for kw in config["keywords"] if kw in text)
        scores[kb_key] = score
    
    best_kb = max(scores, key=scores.get)
    best_score = scores[best_kb]
    
    if best_score > 0:
        return best_kb, best_score
    
    return "link-collection", 0.3


def save_to_kb(kb: str, title: str, content: str, url: str) -> Path:
    """保存到知识库"""
    date_str = datetime.now().strftime("%Y-%m-%d")
    year = date_str[:4]
    month = date_str[5:7]
    day = date_str[8:10]
    
    if kb in KB_CONFIG:
        kb_dir = MEMORY_DIR / "kb-archive" / kb / year / month
        kb_name = KB_CONFIG[kb]["name"]
    else:
        kb_dir = MEMORY_DIR / "link-collection" / year / month
        kb_name = "链接收藏"
    
    kb_dir.mkdir(parents=True, exist_ok=True)
    file_path = kb_dir / f"{day}.md"
    
    # 构建条目
    entry = f"""
### 📱 [{title}]({url})
> 来源: 微信公众号 | 收集时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}

---
"""
    
    if file_path.exists():
        with open(file_path, "a", encoding="utf-8") as f:
            f.write(entry)
    else:
        header = f"# {kb_name} - {date_str} 日报\n\n"
        file_path.write_text(header + entry, encoding="utf-8")
    
    return file_path


def manual_input_mode(url: str) -> dict:
    """手动输入模式 - 当自动抓取失败时使用"""
    print("\n" + "-"*60)
    print("📝 手动粘贴模式")
    print("-"*60)
    print("\n💡 请按以下步骤操作:")
    print("   1. 在微信中打开该文章")
    print("   2. 复制文章标题")
    print("   3. 复制全文内容 (Ctrl+A, Ctrl+C)")
    print("\n请粘贴文章标题 (回车确认):")
    
    try:
        title = input().strip()
        if not title:
            title = "微信文章"
        
        print("\n请粘贴文章内容 (输入 END 单独一行结束):")
        lines = []
        while True:
            line = input()
            if line.strip() == "END":
                break
            lines.append(line)
        
        content = "\n".join(lines)
        
        print("\n请输入公众号名称 (可选，直接回车跳过):")
        author = input().strip()
        
        return {
            "title": title,
            "content": content,
            "author": author or "未知",
            "url": url
        }
    except EOFError:
        print("\n❌ 输入中断")
        return None
    except KeyboardInterrupt:
        print("\n❌ 用户取消")
        return None


def main():
    parser = argparse.ArgumentParser(description="归档微信文章")
    parser.add_argument("--url", "-u", required=True, help="微信文章URL")
    parser.add_argument("--method", "-m", default="playwright", help="抓取方法")
    parser.add_argument("--auto-classify", "-a", action="store_true", help="自动分类")
    parser.add_argument("--manual", action="store_true", help="强制使用手动模式")
    
    args = parser.parse_args()
    
    print("\n" + "="*60)
    print("📱 微信文章归档")
    print("="*60)
    
    # 检查是否已收集
    if is_url_collected(args.url):
        print(f"\n⏭️  已收集，跳过: {args.url}")
        return 0
    
    article = None
    
    # 如果不是强制手动模式，先尝试自动抓取
    if not args.manual:
        print(f"\n🔍 尝试自动抓取: {args.url}")
        article = fetch_wechat_article(args.url, args.method)
    
    # 如果自动抓取失败或未尝试，进入手动模式
    if not article:
        if not args.manual:
            print("\n⚠️  自动抓取被微信拦截，切换到手动模式...")
        article = manual_input_mode(args.url)
    
    if not article:
        print("❌ 归档失败")
        return 1
    
    print(f"\n📄 标题: {article['title']}")
    print(f"✍️  作者: {article.get('author', '未知')}")
    print(f"📝 内容长度: {len(article.get('content', ''))} 字符")
    
    # 分类
    if args.auto_classify:
        kb, confidence = classify_content(article['title'], article['content'])
        print(f"\n📂 分类: {KB_CONFIG.get(kb, {}).get('name', kb)} (置信度: {confidence:.2f})")
    else:
        kb = "link-collection"
        print(f"\n📂 分类: 链接收藏")
    
    # 保存
    file_path = save_to_kb(kb, article['title'], article['content'], args.url)
    print(f"\n✅ 已保存: {file_path}")
    
    # 标记已收集
    mark_url_collected(args.url, kb, article['title'])
    
    print("="*60 + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
