#!/usr/bin/env python3
"""
统一内容归档脚本 - 处理微信文章、B站视频等链接
自动分类到 AI/游戏/健康 知识库，和日报同一层级
输出同步信息供 Agent 调用飞书工具完成同步
"""

import argparse
import json
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
        "parent_token": "PhL6wlstzissQ1kKPwMc18xbngg",
        "keywords": ["ai", "人工智能", "gpt", "claude", "openai", "anthropic", "llm", "大模型", "机器学习", "深度学习", "神经网络", "nlp", "计算机视觉"]
    },
    "game-development": {
        "name": "🎮 游戏开发",
        "space_id": "7616735513310924004",
        "parent_token": "U9EWwwL8ui16IEkrN8vcIRISnFg",
        "keywords": ["game", "游戏", "unity", "unreal", "godot", "indie", "gamedev", "游戏引擎", "游戏设计", "独立游戏", "游戏开发", "gameplay", "关卡设计"]
    },
    "healthy-living": {
        "name": "🌱 健康生活",
        "space_id": "7616737910330510558",
        "parent_token": "XD2PwwJukiD8a8koNAAc4Fedn5t",
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


def fetch_content(url: str, url_type: str) -> dict:
    """获取内容（简化版，实际由外部调用）"""
    # 这里简化处理，实际标题等信息由调用方提供
    return {
        "url": url,
        "title": url.split("/")[-1] or "未命名",
        "content": "",
        "source": "Bilibili" if url_type == "bilibili" else "微信公众号" if url_type == "wechat" else "网页"
    }


def classify_content(url: str, title: str) -> tuple:
    """分类内容到知识库"""
    text = (url + " " + title).lower()
    
    scores = {}
    for kb_key, config in KB_CONFIG.items():
        score = sum(1 for kw in config["keywords"] if kw in text)
        scores[kb_key] = score
    
    best_kb = max(scores, key=scores.get)
    best_score = scores[best_kb]
    
    if best_score > 0:
        confidence = min(best_score / 2, 1.0)
        return best_kb, confidence
    
    return "link-collection", 0.0


def save_to_kb(kb: str, content: dict, date_str: str) -> Path:
    """保存到知识库"""
    year = date_str[:4]
    month = date_str[5:7]
    day = date_str[8:10]
    
    kb_dir = MEMORY_DIR / "kb-archive" / kb / year / month
    kb_dir.mkdir(parents=True, exist_ok=True)
    
    file_path = kb_dir / f"{day}.md"
    
    source_emoji = "📱" if content.get('source') == '微信公众号' else "📺" if content.get('source') == 'Bilibili' else "🔗"
    
    entry = f"""### {source_emoji} [{content['title']}]({content['url']})
> 来源: {content.get('source', '未知')} | 收集时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}

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
    """归档内容"""
    result = {
        "url": url,
        "status": "skipped",
        "local_saved": False,
        "feishu_sync": None
    }
    
    # 1. 检查是否已收集
    if is_url_collected(url):
        result["reason"] = "already_collected"
        return result
    
    # 2. 检测类型
    url_type = detect_url_type(url)
    result["url_type"] = url_type
    
    # 3. 基础内容
    content = fetch_content(url, url_type)
    if title:
        content['title'] = title
    
    # 4. 分类
    kb, confidence = classify_content(url, content['title'])
    result["kb"] = kb
    result["confidence"] = confidence
    
    # 5. 保存到本地
    date_str = datetime.now().strftime("%Y-%m-%d")
    file_path = save_to_kb(kb, content, date_str)
    result["local_saved"] = True
    result["file"] = str(file_path)
    
    # 6. 标记已收集
    mark_url_collected(url, kb, content['title'])
    
    # 7. 生成飞书同步信息（供 Agent 使用）
    if kb in KB_CONFIG:
        kb_config = KB_CONFIG[kb]
        result["feishu_sync"] = {
            "space_id": kb_config["space_id"],
            "parent_token": kb_config["parent_token"],
            "kb_name": kb_config["name"],
            "year": date_str[:4],
            "month": str(int(date_str[5:7])),
            "day": str(int(date_str[8:10])),
            "doc_title": f"{int(date_str[5:7])}月{int(date_str[8:10])}日 日报",
            "content_entry": f"""### {'📱' if content.get('source') == '微信公众号' else '📺' if content.get('source') == 'Bilibili' else '🔗'} [{content['title']}]({content['url']})
> 来源: {content.get('source', '未知')} | 收集时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}

---
"""
        }
    
    result["status"] = "success"
    return result


def main():
    parser = argparse.ArgumentParser(description="统一内容归档")
    parser.add_argument("--url", "-u", required=True, help="内容URL")
    parser.add_argument("--title", "-t", default="", help="标题（可选）")
    
    args = parser.parse_args()
    
    ensure_dirs()
    
    result = archive_content(args.url, args.title)
    
    # 输出 JSON 结果
    print(json.dumps(result, indent=2, ensure_ascii=False))
    
    return 0 if result["status"] == "success" else 1


if __name__ == "__main__":
    sys.exit(main())
