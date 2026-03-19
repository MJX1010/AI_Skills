#!/usr/bin/env python3
"""
链接收集脚本 - 统一处理用户发送的链接
整合原 link-collector 功能到 knowledge-base
"""

import argparse
import json
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


def classify_link(url: str, title: str = "") -> tuple:
    """分类链接到知识库"""
    # 合并URL和标题进行判断
    text = (url + " " + title).lower()
    
    scores = {}
    for kb_key, config in KB_CONFIG.items():
        score = sum(1 for kw in config["keywords"] if kw in text)
        scores[kb_key] = score
    
    # 找出最高分
    best_kb = max(scores, key=scores.get)
    best_score = scores[best_kb]
    
    # 判断模块
    if best_score > 0:
        module = classify_module(best_kb, text)
        confidence = min(best_score / 3, 1.0)  # 简单置信度计算
        return best_kb, module, confidence
    
    # 无法分类，归入本地链接收藏
    return "link-collection", "general", 0.5


def classify_module(kb: str, text: str) -> str:
    """分类到具体模块"""
    text = text.lower()
    
    if kb == "ai-latest-news":
        if any(kw in text for kw in ["工具", "tool", "技巧", "tutorial"]):
            return "tools"
        elif any(kw in text for kw in ["论文", "paper", "研究", "research"]):
            return "research"
        elif any(kw in text for kw in ["案例", "case", "实践", "实战"]):
            return "cases"
        else:
            return "news"
    
    elif kb == "game-development":
        if any(kw in text for kw in ["unity", "unreal", "godot", "引擎"]):
            return "engine"
        elif any(kw in text for kw in ["设计", "design"]):
            return "design"
        elif any(kw in text for kw in ["美术", "art", "模型", "动画"]):
            return "art"
        elif any(kw in text for kw in ["音频", "audio", "音效", "音乐"]):
            return "audio"
        elif any(kw in text for kw in ["indie", "独立"]):
            return "indie"
        else:
            return "tech"
    
    elif kb == "healthy-living":
        if any(kw in text for kw in ["运动", "健身", "fitness", "跑步"]):
            return "fitness"
        elif any(kw in text for kw in ["饮食", "营养", "diet", "食谱"]):
            return "diet"
        elif any(kw in text for kw in ["心理", "mental", "压力", "情绪"]):
            return "mental"
        elif any(kw in text for kw in ["睡眠", "sleep", "失眠"]):
            return "sleep"
        elif any(kw in text for kw in ["医疗", "medical", "疾病", "医院"]):
            return "medical"
        else:
            return "tips"
    
    return "general"


def fetch_content(url: str) -> dict:
    """获取链接内容"""
    print(f"  🔍 获取内容: {url[:60]}...")
    
    try:
        # 使用 coze-web-fetch
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
            # 解析结果
            output = result.stdout
            # 提取标题（第一行通常有标题）
            lines = output.split("\n")
            title = ""
            for line in lines[:5]:
                if line.startswith("# "):
                    title = line[2:].strip()
                    break
            
            if not title:
                title = url.split("/")[-1] or "无标题"
            
            # 提取正文
            content = output
            
            return {
                "url": url,
                "title": title,
                "content": content,
                "fetched_at": datetime.now().isoformat()
            }
        else:
            print(f"  ⚠️ 获取失败: {result.stderr[:100]}")
            return {
                "url": url,
                "title": url.split("/")[-1] or "无标题",
                "content": "",
                "error": result.stderr
            }
    
    except Exception as e:
        print(f"  ⚠️ 获取异常: {e}")
        return {
            "url": url,
            "title": url.split("/")[-1] or "无标题",
            "content": "",
            "error": str(e)
        }


def save_to_kb(kb: str, module: str, content: dict, date_str: str) -> Path:
    """保存到知识库"""
    year = date_str[:4]
    month = date_str[5:7]
    day = date_str[8:10]
    
    # 文件路径
    kb_dir = MEMORY_DIR / "kb-archive" / kb / year / month
    kb_dir.mkdir(parents=True, exist_ok=True)
    
    file_path = kb_dir / f"{day}.md"
    
    # 构建条目
    entry = f"""
### [{content['title']}]({content['url']})
> 模块: {module} | 收集时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}

{content.get('content', '')[:500]}...

---
"""
    
    # 追加或创建
    if file_path.exists():
        with open(file_path, "a", encoding="utf-8") as f:
            f.write(entry)
    else:
        header = f"# {KB_CONFIG.get(kb, {}).get('name', kb)} - {date_str} 日报\n\n"
        file_path.write_text(header + entry, encoding="utf-8")
    
    return file_path


def save_to_local_links(content: dict, date_str: str) -> Path:
    """保存到本地链接收藏"""
    year = date_str[:4]
    month = date_str[5:7]
    
    links_dir = MEMORY_DIR / "link-collection" / year / month
    links_dir.mkdir(parents=True, exist_ok=True)
    
    file_path = links_dir / f"{date_str}.md"
    
    entry = f"""
### [{content['title']}]({content['url']})
> 收集时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}

{content.get('content', '')[:300]}...

---
"""
    
    if file_path.exists():
        with open(file_path, "a", encoding="utf-8") as f:
            f.write(entry)
    else:
        header = f"# 链接收藏 - {date_str}\n\n"
        file_path.write_text(header + entry, encoding="utf-8")
    
    return file_path


def collect_link(url: str, title: str = "") -> dict:
    """收集单个链接"""
    print(f"\n{'='*60}")
    print(f"🔗 处理链接: {url[:60]}...")
    print(f"{'='*60}")
    
    # 1. 检查是否已收集
    if is_url_collected(url):
        print(f"  ⏭️  已收集，跳过")
        return {"status": "skipped", "reason": "already_collected"}
    
    # 2. 分类
    kb, module, confidence = classify_link(url, title)
    print(f"  📂 分类: {KB_CONFIG.get(kb, {}).get('name', kb)} / {module}")
    print(f"  📊 置信度: {confidence:.2f}")
    
    # 3. 获取内容
    content = fetch_content(url)
    if title:
        content['title'] = title
    
    # 4. 保存
    date_str = datetime.now().strftime("%Y-%m-%d")
    
    if kb in KB_CONFIG:
        # 保存到知识库
        file_path = save_to_kb(kb, module, content, date_str)
        print(f"  ✅ 已保存到知识库: {file_path}")
        
        # 标记已收集
        mark_url_collected(url, kb, content['title'])
        
        return {
            "status": "success",
            "kb": kb,
            "module": module,
            "confidence": confidence,
            "file": str(file_path)
        }
    else:
        # 保存到本地链接
        file_path = save_to_local_links(content, date_str)
        print(f"  ✅ 已保存到本地链接: {file_path}")
        
        mark_url_collected(url, "link-collection", content['title'])
        
        return {
            "status": "success",
            "kb": "link-collection",
            "module": "general",
            "file": str(file_path)
        }


def main():
    parser = argparse.ArgumentParser(description="收集链接到知识库")
    parser.add_argument("--url", "-u", required=True, help="链接URL")
    parser.add_argument("--title", "-t", default="", help="链接标题（可选）")
    
    args = parser.parse_args()
    
    print("\n" + "="*60)
    print("🔗 链接收集")
    print("="*60)
    
    ensure_dirs()
    
    result = collect_link(args.url, args.title)
    
    print("\n" + "="*60)
    print("📊 结果")
    print("="*60)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    print("="*60 + "\n")
    
    return 0 if result["status"] == "success" else 1


if __name__ == "__main__":
    sys.exit(main())
