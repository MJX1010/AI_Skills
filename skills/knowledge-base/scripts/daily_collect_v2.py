#!/usr/bin/env python3
"""
日报收集脚本 v2 - 增加时效性和质量检查
- 质量评分: 来源可信度 + 标题质量 + 时效性
- 数量限制: 每个知识库最多15条高质量内容
- 智能去重: URL + 标题相似度
"""

import argparse
import json
import re
import subprocess
import sys
import yaml
from datetime import datetime, timedelta
from pathlib import Path
from difflib import SequenceMatcher

WORKSPACE = Path("/workspace/projects/workspace")
MEMORY_DIR = WORKSPACE / "memory"
STATE_DIR = MEMORY_DIR / "state"
COLLECTED_URLS_FILE = STATE_DIR / "collected-urls.json"
CONFIG_FILE = WORKSPACE / "config" / "content_sources.yaml"

# 高质量来源白名单（可信度评分）
TRUSTED_SOURCES = {
    # AI 领域
    "openai.com": 10, "anthropic.com": 10, "claude.ai": 10,
    "arxiv.org": 9, "github.com": 8, "huggingface.co": 8,
    "techcrunch.com": 7, "theverge.com": 7, "wired.com": 7,
    
    # 中文科技媒体
    "36kr.com": 7, "pingwest.com": 7, "geekpark.net": 7,
    "solidot.org": 7, "jiqizhixin.com": 8, "ifanr.com": 6,
    
    # 游戏领域
    "unity.com": 9, "unrealengine.com": 9, "godotengine.org": 8,
    "gamedeveloper.com": 7, "indiegames.com": 6,
    
    # 健康领域
    "who.int": 10, "mayoclinic.org": 9, "harvard.edu": 8,
    "zhihu.com": 5,  # 知乎专栏
}

# 低质量来源黑名单
LOW_QUALITY_PATTERNS = [
    "clickbait", "ads", "promo", "sponsored",
    "震惊", "震惊！", "震惊!", "99%", "必看", "不看后悔",
    "绝了", "神了", "疯狂", "爆火", "全网", "都在看",
]

KB_BASE_CONFIG = {
    "ai-latest-news": {
        "name": "🤖 AI最新资讯",
        "space_id": "7616519632920251572",
        "max_items": 15,  # 最多收集15条
        "min_quality_score": 5.0  # 最低质量分
    },
    "game-development": {
        "name": "🎮 游戏开发",
        "space_id": "7616735513310924004",
        "max_items": 15,
        "min_quality_score": 5.0
    },
    "healthy-living": {
        "name": "🌱 健康生活",
        "space_id": "7616737910330510558",
        "max_items": 15,
        "min_quality_score": 5.0
    }
}


def load_search_config():
    """加载搜索配置"""
    kb_config = {}
    for kb_key, base_info in KB_BASE_CONFIG.items():
        kb_config[kb_key] = base_info.copy()
        kb_config[kb_key]["search_queries"] = []
    
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                config = yaml.safe_load(f)
            
            if config:
                for kb in ["AI", "game", "health"]:
                    kb_key = f"{kb}-latest-news" if kb == "AI" else f"{kb}-development" if kb == "game" else f"{kb}-living"
                    if kb_key in kb_config and "search_queries" in config.get(kb, {}):
                        kb_config[kb_key]["search_queries"] = config[kb]["search_queries"]
            
            print(f"✅ 已加载配置文件: {CONFIG_FILE}")
        except Exception as e:
            print(f"⚠️ 读取配置文件失败: {e}")
    
    # 默认搜索词
    defaults = {
        "ai-latest-news": [
            "OpenAI GPT Claude Anthropic AI latest news 2026",
            "Claude 3.7 Sonnet new features coding",
            "AI agent skill development best practices"
        ],
        "game-development": [
            "Unity 6 new features 2026",
            "Unreal Engine 5.5 game development",
            "Godot 4.4 indie game development"
        ],
        "healthy-living": [
            "健康生活 科学饮食 运动健身 2026",
            "mental health stress management wellness"
        ]
    }
    
    for kb_key in kb_config:
        if not kb_config[kb_key].get("search_queries"):
            kb_config[kb_key]["search_queries"] = defaults.get(kb_key, [])
    
    return kb_config


KB_CONFIG = load_search_config()
COLLECT_DAYS = 2


def calculate_quality_score(url: str, title: str) -> float:
    """
    计算内容质量评分 (0-10)
    - 来源可信度: 0-10
    - 标题质量: 0-5
    - 时效性奖励: 0-2
    """
    score = 0.0
    
    # 1. 来源可信度评分
    source_score = 3.0  # 默认3分
    for domain, weight in TRUSTED_SOURCES.items():
        if domain in url.lower():
            source_score = weight
            break
    score += source_score
    
    # 2. 标题质量评分
    title_score = 2.5  # 默认2.5分
    
    # 检查低质量关键词
    for pattern in LOW_QUALITY_PATTERNS:
        if pattern in title.lower():
            title_score -= 1.5
            break
    
    # 标题长度检查（太短或太长都不好）
    title_len = len(title)
    if 20 <= title_len <= 60:
        title_score += 1.0
    elif title_len < 10:
        title_score -= 1.0
    
    # 标题信息密度（数字、年份、专业术语加分）
    if re.search(r'20\d{2}', title):  # 包含年份
        title_score += 0.5
    if re.search(r'\d+\.\d+|v\d+', title):  # 包含版本号
        title_score += 0.5
    
    score += max(0, title_score)
    
    return min(10.0, score)


def is_similar_title(title1: str, title2: str, threshold: float = 0.7) -> bool:
    """检查两个标题是否相似（用于去重）"""
    return SequenceMatcher(None, title1.lower(), title2.lower()).ratio() > threshold


def search_content(query: str, days: int = 2, max_results: int = 10) -> list:
    """搜索内容并返回高质量结果"""
    print(f"  🔍 搜索: {query[:50]}...")
    
    try:
        cmd = [
            "npx", "ts-node",
            str(WORKSPACE / "skills/coze-web-search/scripts/search.ts"),
            "-q", query,
            "--time-range", f"{days}d",
            "--count", str(max_results)
        ]
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=120,
            cwd=WORKSPACE
        )
        
        if result.returncode == 0:
            return parse_search_results(result.stdout)
        else:
            return []
    
    except Exception as e:
        print(f"  ⚠️ 搜索失败: {e}")
        return []


def parse_search_results(output: str) -> list:
    """解析搜索结果"""
    results = []
    lines = output.split("\n")
    
    for line in lines:
        line = line.strip()
        if line.startswith("http") and " - " in line:
            parts = line.split(" - ", 1)
            if len(parts) >= 2:
                results.append({
                    "url": parts[0].strip(),
                    "title": parts[1].strip()
                })
    
    return results


def load_collected_urls():
    """加载已收集的URL"""
    if COLLECTED_URLS_FILE.exists():
        return json.loads(COLLECTED_URLS_FILE.read_text())
    return {"urls": {}, "titles": []}


def save_collected_urls(data):
    """保存已收集的URL"""
    COLLECTED_URLS_FILE.write_text(json.dumps(data, indent=2))


def is_content_duplicate(url: str, title: str, collected_data: dict) -> bool:
    """检查内容是否重复（URL或标题相似）"""
    # URL检查
    if url in collected_data.get("urls", {}):
        return True
    
    # 标题相似度检查
    for existing_title in collected_data.get("titles", []):
        if is_similar_title(title, existing_title):
            return True
    
    return False


def mark_content_collected(url: str, title: str, kb: str, collected_data: dict):
    """标记内容为已收集"""
    if "urls" not in collected_data:
        collected_data["urls"] = {}
    if "titles" not in collected_data:
        collected_data["titles"] = []
    
    collected_data["urls"][url] = {
        "first_collected": datetime.now().isoformat(),
        "kb": kb,
        "title": title
    }
    collected_data["titles"].append(title)
    
    # 限制标题历史记录数量（保留最近100条）
    if len(collected_data["titles"]) > 100:
        collected_data["titles"] = collected_data["titles"][-100:]
    
    save_collected_urls(collected_data)


def classify_content(url: str, title: str) -> tuple:
    """分类内容到知识库"""
    title_lower = title.lower()
    
    # AI 关键词
    ai_keywords = ["ai", "人工智能", "gpt", "claude", "openai", "anthropic", "llm", "大模型"]
    if any(kw in title_lower for kw in ai_keywords):
        return "ai-latest-news", "news"
    
    # 游戏关键词
    game_keywords = ["game", "游戏", "unity", "unreal", "godot", "indie"]
    if any(kw in title_lower for kw in game_keywords):
        return "game-development", "tech"
    
    # 健康关键词
    health_keywords = ["健康", "health", "健身", "运动", "饮食", "心理"]
    if any(kw in title_lower for kw in health_keywords):
        return "healthy-living", "tips"
    
    return "ai-latest-news", "news"


def collect_kb(kb_key: str, date_str: str) -> dict:
    """收集单个知识库的高质量内容"""
    config = KB_CONFIG[kb_key]
    print(f"\n{'='*60}")
    print(f"📚 收集: {config['name']} (最多{config['max_items']}条，最低质量{config['min_quality_score']}分)")
    print(f"{'='*60}")
    
    all_candidates = []
    collected_data = load_collected_urls()
    
    # 收集候选内容
    for query in config['search_queries']:
        results = search_content(query, days=COLLECT_DAYS, max_results=10)
        
        for result in results:
            url = result['url']
            title = result['title']
            
            # 去重检查
            if is_content_duplicate(url, title, collected_data):
                continue
            
            # 分类
            kb, module = classify_content(url, title)
            if kb != kb_key:
                continue
            
            # 计算质量分
            quality_score = calculate_quality_score(url, title)
            
            # 低于质量阈值跳过
            if quality_score < config['min_quality_score']:
                print(f"  ⏭️  质量分{quality_score:.1f}过低: {title[:40]}...")
                continue
            
            all_candidates.append({
                "url": url,
                "title": title,
                "kb": kb,
                "module": module,
                "quality": quality_score
            })
    
    # 按质量分排序，取前N条
    all_candidates.sort(key=lambda x: x['quality'], reverse=True)
    selected = all_candidates[:config['max_items']]
    
    # 保存选中的内容
    for item in selected:
        print(f"  ✅ [{item['quality']:.1f}分] {item['title'][:50]}...")
        save_to_file(item['kb'], item['module'], item, date_str)
        mark_content_collected(item['url'], item['title'], item['kb'], collected_data)
    
    print(f"\n  📊 候选: {len(all_candidates)}条 → 选中: {len(selected)}条")
    
    return {
        "kb": kb_key,
        "name": config['name'],
        "selected": len(selected),
        "candidates": len(all_candidates)
    }


def save_to_file(kb: str, module: str, content: dict, date_str: str):
    """保存内容到本地文件"""
    year = date_str[:4]
    month = date_str[5:7]
    day = date_str[8:10]
    
    file_path = MEMORY_DIR / "kb-archive" / kb / year / month / f"{day}.md"
    file_path.parent.mkdir(parents=True, exist_ok=True)
    
    entry = f"""### [{content['title']}]({content['url']})
> 质量分: {content['quality']:.1f} | 模块: {module} | 收集时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}

---
"""
    
    if file_path.exists():
        with open(file_path, "a", encoding="utf-8") as f:
            f.write(entry)
    else:
        header = f"# {KB_CONFIG[kb]['name']} - {date_str} 日报\n\n"
        file_path.write_text(header + entry, encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description="日报收集 v2（带质量检查）")
    parser.add_argument("--date", default=datetime.now().strftime("%Y-%m-%d"), help="日期")
    args = parser.parse_args()
    
    print("\n" + "="*60)
    print("🔄 日报收集 v2（带质量检查）")
    print("="*60)
    print(f"📅 日期: {args.date}")
    print(f"⏰ 收集范围: 最近{COLLECT_DAYS}天")
    print(f"📊 每个知识库最多: 15条高质量内容")
    print("="*60)
    
    results = []
    for kb_key in KB_CONFIG.keys():
        result = collect_kb(kb_key, args.date)
        results.append(result)
    
    # 输出汇总
    print(f"\n{'='*60}")
    print("📊 日报收集汇总")
    print(f"{'='*60}")
    total = 0
    for r in results:
        print(f"{r['name']}: {r['selected']}条 (从{r['candidates']}条候选)")
        total += r['selected']
    print(f"\n总计: {total}条高质量内容")
    print("="*60 + "\n")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
