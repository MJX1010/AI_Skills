#!/usr/bin/env python3
"""
B站视频归档助手
一键抓取B站视频并归档到知识库
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
        "keywords": ["ai", "人工智能", "gpt", "claude", "openai", "anthropic", "llm", "大模型"]
    },
    "game-development": {
        "name": "🎮 游戏开发",
        "space_id": "7616735513310924004",
        "keywords": ["game", "游戏", "unity", "unreal", "godot", "indie"]
    },
    "healthy-living": {
        "name": "🌱 健康生活",
        "space_id": "7616737910330510558",
        "keywords": ["健康", "运动", "健身", "饮食"]
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


def fetch_bilibili_video(url: str, method: str = "auto") -> dict:
    """调用 fetch_bilibili.py 抓取视频"""
    fetch_script = Path(__file__).parent / "fetch_bilibili.py"
    
    try:
        result = subprocess.run(
            [
                "python3", str(fetch_script),
                url
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
        author = ""
        
        for line in lines:
            if line.startswith("标题:") or line.startswith("视频标题:"):
                title = line.split(":", 1)[1].strip()
            elif line.startswith("UP主:") or line.startswith("作者:"):
                author = line.split(":", 1)[1].strip()
        
        if not title:
            title = "B站视频"
        
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
### 📺 [{title}]({url})
> 来源: Bilibili | UP主: {content.get('author', '未知')} | 收集时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}

---
"""
    
    if file_path.exists():
        with open(file_path, "a", encoding="utf-8") as f:
            f.write(entry)
    else:
        header = f"# {kb_name} - {date_str} 日报\n\n"
        file_path.write_text(header + entry, encoding="utf-8")
    
    return file_path


def main():
    parser = argparse.ArgumentParser(description="归档B站视频")
    parser.add_argument("--url", "-u", required=True, help="B站视频URL")
    parser.add_argument("--auto-classify", "-a", action="store_true", help="自动分类")
    
    args = parser.parse_args()
    
    print("\n" + "="*60)
    print("📺 B站视频归档")
    print("="*60)
    
    # 检查是否已收集
    if is_url_collected(args.url):
        print(f"\n⏭️  已收集，跳过: {args.url}")
        return 0
    
    # 抓取视频
    print(f"\n🔍 抓取视频: {args.url}")
    video = fetch_bilibili_video(args.url)
    
    if not video:
        print("❌ 抓取失败")
        return 1
    
    print(f"📄 标题: {video['title']}")
    print(f"🎬 UP主: {video.get('author', '未知')}")
    
    # 分类
    if args.auto_classify:
        kb, confidence = classify_content(video['title'], video['content'])
        print(f"\n📂 分类: {KB_CONFIG.get(kb, {}).get('name', kb)} (置信度: {confidence:.2f})")
    else:
        kb = "link-collection"
        print(f"\n📂 分类: 链接收藏 (未启用自动分类)")
    
    # 保存
    file_path = save_to_kb(kb, video['title'], video, args.url)
    print(f"\n✅ 已保存: {file_path}")
    
    # 标记已收集
    mark_url_collected(args.url, kb, video['title'])
    
    print("="*60 + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
