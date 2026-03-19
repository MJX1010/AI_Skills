#!/usr/bin/env python3
"""
统一内容归档脚本 - 处理微信文章、B站视频等链接
自动分类到 AI/游戏/健康 知识库，和日报同一层级
"""

import argparse
import json
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

WORKSPACE = Path("/workspace/projects/workspace")
MEMORY_DIR = WORKSPACE / "memory"
STATE_DIR = MEMORY_DIR / "state"
COLLECTED_URLS_FILE = STATE_DIR / "collected-urls.json"

KB_CONFIG = {
    "ai-latest-news": {
        "name": "🤖 AI最新资讯",
        "space_id": "7616519632920251572",
        "keywords": ["ai", "人工智能", "gpt", "claude", "openai", "anthropic", "llm", "大模型", "机器学习", "深度学习", "神经网络", "nlp", "计算机视觉"]
    },
    "game-development": {
        "name": "🎮 游戏开发",
        "space_id": "7616735513310924004",
        "keywords": ["game", "游戏", "unity", "unreal", "godot", "indie", "gamedev", "游戏引擎", "游戏设计", "独立游戏", "游戏开发", "gameplay", "关卡设计"]
    },
    "healthy-living": {
        "name": "🌱 健康生活",
        "space_id": "7616737910330510558",
        "keywords": ["健康", "health", "健身", "运动", "饮食", "营养", "心理", "生活", "养生", "保健", "瑜伽", "跑步", "减肥", "睡眠", "医疗", "疾病"]
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


def detect_url_type(url: str) -> str:
    """检测URL类型"""
    if "mp.weixin.qq.com" in url or "weixin.qq.com" in url:
        return "wechat"
    elif "bilibili.com" in url or "b23.tv" in url:
        return "bilibili"
    else:
        return "generic"


def fetch_wechat_content(url: str) -> dict:
    """获取微信文章内容"""
    print(f"  📱 使用微信专用抓取...")
    
    try:
        # 调用 fetch_wechat.py
        cmd = [
            "python3",
            str(WORKSPACE / "skills/knowledge-base/scripts/fetch_wechat.py"),
            url,
            "--method", "playwright"
        ]
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=120,
            cwd=WORKSPACE
        )
        
        if result.returncode == 0:
            # 解析输出
            output = result.stdout
            # 提取标题和内容
            title = ""
            content = ""
            
            lines = output.split("\n")
            for i, line in enumerate(lines):
                if line.startswith("# ") and not title:
                    title = line[2:].strip()
                elif "作者:" in line or "公众号:" in line:
                    content += line + "\n"
                elif len(line) > 20:
                    content += line + "\n"
            
            if not title:
                title = "微信文章"
            
            return {
                "url": url,
                "title": title,
                "content": content[:2000],  # 限制长度
                "source": "微信公众号",
                "fetched_at": datetime.now().isoformat()
            }
        else:
            print(f"    ⚠️ 微信抓取失败，尝试通用方式")
            return fetch_generic_content(url)
    
    except Exception as e:
        print(f"    ⚠️ 微信抓取异常: {e}")
        return fetch_generic_content(url)


def fetch_bilibili_content(url: str) -> dict:
    """获取B站视频内容"""
    print(f"  📺 使用B站专用抓取...")
    
    try:
        # 调用 fetch_bilibili.py
        cmd = [
            "python3",
            str(WORKSPACE / "skills/knowledge-base/scripts/fetch_bilibili.py"),
            url
        ]
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=120,
            cwd=WORKSPACE
        )
        
        if result.returncode == 0:
            output = result.stdout
            
            # 提取标题
            title = ""
            desc = ""
            author = ""
            
            lines = output.split("\n")
            for line in lines:
                if line.startswith("标题:") or line.startswith("视频标题:"):
                    title = line.split(":", 1)[1].strip()
                elif line.startswith("描述:") or line.startswith("视频描述:"):
                    desc = line.split(":", 1)[1].strip()
                elif line.startswith("UP主:") or line.startswith("作者:"):
                    author = line.split(":", 1)[1].strip()
            
            if not title:
                title = "B站视频"
            
            content = f"UP主: {author}\n\n{desc}" if author else desc
            
            return {
                "url": url,
                "title": title,
                "content": content[:2000],
                "source": "Bilibili",
                "fetched_at": datetime.now().isoformat()
            }
        else:
            print(f"    ⚠️ B站抓取失败，尝试通用方式")
            return fetch_generic_content(url)
    
    except Exception as e:
        print(f"    ⚠️ B站抓取异常: {e}")
        return fetch_generic_content(url)


def fetch_generic_content(url: str) -> dict:
    """通用内容获取"""
    print(f"  🌐 使用通用方式获取...")
    
    try:
        cmd = [
            "npx", "ts-node",
            str(WORKSPACE / "skills/coze-web-fetch/scripts/fetch.ts"),
            "-u", url,
            "--format", "markdown",
            "--text-only"
        ]
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=60,
            cwd=WORKSPACE
        )
        
        if result.returncode == 0:
            output = result.stdout
            lines = output.split("\n")
            
            # 提取标题
            title = ""
            for line in lines[:10]:
                if line.startswith("# "):
                    title = line[2:].strip()
                    break
            
            if not title:
                title = url.split("/")[-1] or "未命名"
            
            return {
                "url": url,
                "title": title,
                "content": output[:2000],
                "source": "网页",
                "fetched_at": datetime.now().isoformat()
            }
        else:
            return {
                "url": url,
                "title": url.split("/")[-1] or "未命名",
                "content": "",
                "source": "未知",
                "error": "获取失败"
            }
    
    except Exception as e:
        return {
            "url": url,
            "title": url.split("/")[-1] or "未命名",
            "content": "",
            "source": "未知",
            "error": str(e)
        }


def classify_content(url: str, title: str, content: str) -> tuple:
    """分类内容到知识库"""
    text = (url + " " + title + " " + content).lower()
    
    scores = {}
    for kb_key, config in KB_CONFIG.items():
        score = sum(1 for kw in config["keywords"] if kw in text)
        scores[kb_key] = score
    
    best_kb = max(scores, key=scores.get)
    best_score = scores[best_kb]
    
    if best_score > 0:
        module = classify_module(best_kb, text)
        confidence = min(best_score / 3, 1.0)
        return best_kb, module, confidence
    
    return "link-collection", "general", 0.3


def classify_module(kb: str, text: str) -> str:
    """分类到具体模块"""
    text = text.lower()
    
    if kb == "ai-latest-news":
        if any(kw in text for kw in ["工具", "tool", "技巧", "tutorial", "教程"]):
            return "tools"
        elif any(kw in text for kw in ["论文", "paper", "研究", "research", "原理"]):
            return "research"
        elif any(kw in text for kw in ["案例", "case", "实践", "实战", "经验"]):
            return "cases"
        else:
            return "news"
    
    elif kb == "game-development":
        if any(kw in text for kw in ["unity", "unreal", "godot", "引擎", "渲染"]):
            return "engine"
        elif any(kw in text for kw in ["设计", "design", "机制", "玩法", "关卡"]):
            return "design"
        elif any(kw in text for kw in ["美术", "art", "模型", "动画", "特效"]):
            return "art"
        elif any(kw in text for kw in ["音频", "audio", "音效", "音乐", "声音"]):
            return "audio"
        elif any(kw in text for kw in ["indie", "独立", "独立游戏"]):
            return "indie"
        else:
            return "tech"
    
    elif kb == "healthy-living":
        if any(kw in text for kw in ["运动", "健身", "fitness", "跑步", "瑜伽", "锻炼"]):
            return "fitness"
        elif any(kw in text for kw in ["饮食", "营养", "diet", "食谱", "减肥", "健康餐"]):
            return "diet"
        elif any(kw in text for kw in ["心理", "mental", "压力", "情绪", "冥想", "焦虑"]):
            return "mental"
        elif any(kw in text for kw in ["睡眠", "sleep", "失眠", "作息", "熬夜"]):
            return "sleep"
        elif any(kw in text for kw in ["医疗", "medical", "疾病", "医院", "预防", "健康检查"]):
            return "medical"
        else:
            return "tips"
    
    return "general"


def save_to_kb(kb: str, module: str, content: dict, date_str: str) -> Path:
    """保存到知识库（和日报同一层级）"""
    year = date_str[:4]
    month = date_str[5:7]
    day = date_str[8:10]
    
    kb_dir = MEMORY_DIR / "kb-archive" / kb / year / month
    kb_dir.mkdir(parents=True, exist_ok=True)
    
    file_path = kb_dir / f"{day}.md"
    
    # 构建条目
    source_emoji = "📱" if content.get('source') == '微信公众号' else "📺" if content.get('source') == 'Bilibili' else "🔗"
    
    entry = f"""
### {source_emoji} [{content['title']}]({content['url']})
> 模块: {module} | 来源: {content.get('source', '未知')} | 收集时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}

{content.get('content', '')[:800]}...

---
"""
    
    if file_path.exists():
        with open(file_path, "a", encoding="utf-8") as f:
            f.write(entry)
    else:
        header = f"# {KB_CONFIG.get(kb, {}).get('name', kb)} - {date_str} 日报\n\n"
        file_path.write_text(header + entry, encoding="utf-8")
    
    return file_path


def archive_content(url: str, title: str = "") -> dict:
    """归档内容（统一入口）"""
    print(f"\n{'='*60}")
    print(f"📥 归档内容: {url[:60]}...")
    print(f"{'='*60}")
    
    # 1. 检查是否已收集
    if is_url_collected(url):
        print(f"  ⏭️  已收集，跳过")
        return {"status": "skipped", "reason": "already_collected"}
    
    # 2. 检测类型并获取内容
    url_type = detect_url_type(url)
    print(f"  🔍 检测到类型: {url_type}")
    
    if url_type == "wechat":
        content = fetch_wechat_content(url)
    elif url_type == "bilibili":
        content = fetch_bilibili_content(url)
    else:
        content = fetch_generic_content(url)
    
    if title:
        content['title'] = title
    
    print(f"  📄 标题: {content['title'][:50]}...")
    
    # 3. 分类
    kb, module, confidence = classify_content(url, content['title'], content.get('content', ''))
    print(f"  📂 分类: {KB_CONFIG.get(kb, {}).get('name', kb)} / {module}")
    print(f"  📊 置信度: {confidence:.2f}")
    
    # 4. 保存（和日报同一层级）
    date_str = datetime.now().strftime("%Y-%m-%d")
    file_path = save_to_kb(kb, module, content, date_str)
    print(f"  ✅ 已保存: {file_path}")
    
    # 5. 标记已收集
    mark_url_collected(url, kb, content['title'])
    
    return {
        "status": "success",
        "url_type": url_type,
        "kb": kb,
        "module": module,
        "confidence": confidence,
        "file": str(file_path)
    }


def main():
    parser = argparse.ArgumentParser(description="统一内容归档（微信/B站/通用链接）")
    parser.add_argument("--url", "-u", required=True, help="内容URL")
    parser.add_argument("--title", "-t", default="", help="标题（可选）")
    
    args = parser.parse_args()
    
    print("\n" + "="*60)
    print("📦 统一内容归档")
    print("="*60)
    
    ensure_dirs()
    
    result = archive_content(args.url, args.title)
    
    print("\n" + "="*60)
    print("📊 结果")
    print("="*60)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    print("="*60 + "\n")
    
    return 0 if result["status"] == "success" else 1


if __name__ == "__main__":
    sys.exit(main())
