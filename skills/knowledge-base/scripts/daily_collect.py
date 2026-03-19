#!/usr/bin/env python3
"""
日报收集脚本 - 只收集最近2天的内容
遵循 RULES.md 规则1：日报只收集最近2天发布的内容
使用 config/content_sources.yaml 配置文件
"""

import argparse
import json
import subprocess
import sys
import yaml
from datetime import datetime, timedelta
from pathlib import Path

# 配置
WORKSPACE = Path("/workspace/projects/workspace")
MEMORY_DIR = WORKSPACE / "memory"
STATE_DIR = MEMORY_DIR / "state"
COLLECTED_URLS_FILE = STATE_DIR / "collected-urls.json"
CONFIG_FILE = WORKSPACE / "config" / "content_sources.yaml"

# 基础配置（默认）
KB_BASE_CONFIG = {
    "ai-latest-news": {
        "name": "🤖 AI最新资讯",
        "space_id": "7616519632920251572"
    },
    "game-development": {
        "name": "🎮 游戏开发",
        "space_id": "7616735513310924004"
    },
    "healthy-living": {
        "name": "🌱 健康生活",
        "space_id": "7616737910330510558"
    }
}


def load_search_config():
    """从配置文件加载搜索关键词"""
    kb_config = {}
    
    # 先加载基础配置
    for kb_key, base_info in KB_BASE_CONFIG.items():
        kb_config[kb_key] = base_info.copy()
        kb_config[kb_key]["search_queries"] = []
    
    # 尝试读取配置文件
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                config = yaml.safe_load(f)
            
            if config:
                # 解析 AI 最新资讯搜索词
                if "search_queries" in config.get("AI", {}):
                    kb_config["ai-latest-news"]["search_queries"] = config["AI"]["search_queries"]
                
                # 解析游戏开发搜索词
                if "search_queries" in config.get("game", {}):
                    kb_config["game-development"]["search_queries"] = config["game"]["search_queries"]
                
                # 解析健康生活搜索词
                if "search_queries" in config.get("health", {}):
                    kb_config["healthy-living"]["search_queries"] = config["health"]["search_queries"]
            
            print(f"✅ 已加载配置文件: {CONFIG_FILE}")
        except Exception as e:
            print(f"⚠️ 读取配置文件失败: {e}")
    else:
        print(f"⚠️ 配置文件不存在: {CONFIG_FILE}")
    
    # 如果配置文件中未定义搜索词，使用默认值
    for kb_key in kb_config:
        if not kb_config[kb_key].get("search_queries"):
            print(f"  使用默认搜索词: {kb_key}")
            if kb_key == "ai-latest-news":
                kb_config[kb_key]["search_queries"] = [
                    "OpenAI GPT Claude Anthropic AI latest news",
                    "人工智能 大模型 LLM 2026 最新动态"
                ]
            elif kb_key == "game-development":
                kb_config[kb_key]["search_queries"] = [
                    "Unity Unreal Godot game development",
                    "游戏开发 独立游戏 gamedev"
                ]
            elif kb_key == "healthy-living":
                kb_config[kb_key]["search_queries"] = [
                    "健康 运动 饮食 生活 2026",
                    "fitness nutrition health tips"
                ]
    
    return kb_config


# 全局配置，运行时加载
KB_CONFIG = load_search_config()

# 收集设置：只收集最近2天
COLLECT_DAYS = 2


def ensure_dirs():
    """确保目录存在"""
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    for kb in KB_CONFIG.keys():
        kb_dir = MEMORY_DIR / "kb-archive" / kb / datetime.now().strftime("%Y") / datetime.now().strftime("%m")
        kb_dir.mkdir(parents=True, exist_ok=True)


def load_collected_urls():
    """加载已收集的URL（去重用）"""
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


def search_content(query: str, days: int = 2) -> list:
    """搜索内容（最近N天）"""
    print(f"  🔍 搜索: {query} (最近{days}天)")
    
    try:
        # 使用 coze-web-search
        cmd = [
            "npx", "ts-node",
            str(WORKSPACE / "skills/coze-web-search/scripts/search.ts"),
            "-q", query,
            "--time-range", f"{days}d",
            "--count", "10"
        ]
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=120,
            cwd=WORKSPACE
        )
        
        if result.returncode == 0:
            # 解析结果（简化处理，实际应解析JSON）
            return parse_search_results(result.stdout)
        else:
            print(f"  ⚠️ 搜索失败: {result.stderr[:100]}")
            return []
    
    except Exception as e:
        print(f"  ⚠️ 搜索异常: {e}")
        return []


def parse_search_results(output: str) -> list:
    """解析搜索结果"""
    results = []
    lines = output.split("\n")
    
    current_title = ""
    current_url = ""
    
    for i, line in enumerate(lines):
        line = line.strip()
        
        # 匹配标题行，如 "[1] Models" 或 "OpenAI发布GPT-5.3 Instant"
        if line.startswith("[") and "]" in line:
            current_title = line.split("]", 1)[1].strip()
        elif line.startswith("URL:"):
            current_url = line.replace("URL:", "").strip()
            if current_url and current_title:
                results.append({"url": current_url, "title": current_title})
                current_title = ""
                current_url = ""
        # 备用：直接匹配 http 开头的行（其他格式）
        elif line.startswith("http") and " - " in line:
            parts = line.split(" - ", 1)
            if len(parts) >= 2:
                url = parts[0].strip()
                title = parts[1].strip()
                results.append({"url": url, "title": title})
    
    return results


def classify_content(url: str, title: str) -> tuple:
    """分类内容到知识库和模块"""
    title_lower = title.lower()
    
    # AI 关键词
    ai_keywords = ["ai", "人工智能", "gpt", "claude", "openai", "anthropic", "llm", "大模型"]
    if any(kw in title_lower for kw in ai_keywords):
        kb = "ai-latest-news"
        # 判断模块
        if any(kw in title_lower for kw in ["工具", "tool", "技巧", "tutorial"]):
            module = "tools"
        elif any(kw in title_lower for kw in ["论文", "paper", "研究", "research"]):
            module = "research"
        elif any(kw in title_lower for kw in ["案例", "case", "实践", "实战"]):
            module = "cases"
        else:
            module = "news"
        return kb, module
    
    # 游戏关键词
    game_keywords = ["game", "游戏", "unity", "unreal", "godot", "indie"]
    if any(kw in title_lower for kw in game_keywords):
        kb = "game-development"
        if any(kw in title_lower for kw in ["unity", "unreal", "godot", "引擎"]):
            module = "engine"
        elif any(kw in title_lower for kw in ["设计", "design"]):
            module = "design"
        elif any(kw in title_lower for kw in ["美术", "art", "模型", "动画"]):
            module = "art"
        elif any(kw in title_lower for kw in ["音频", "audio", "音效", "音乐"]):
            module = "audio"
        elif any(kw in title_lower for kw in ["indie", "独立"]):
            module = "indie"
        else:
            module = "tech"
        return kb, module
    
    # 健康关键词
    health_keywords = ["健康", "health", "健身", "运动", "饮食", "心理"]
    if any(kw in title_lower for kw in health_keywords):
        kb = "healthy-living"
        if any(kw in title_lower for kw in ["运动", "健身", "fitness", "跑步"]):
            module = "fitness"
        elif any(kw in title_lower for kw in ["饮食", "营养", "diet", "食谱"]):
            module = "diet"
        elif any(kw in title_lower for kw in ["心理", "mental", "压力", "情绪"]):
            module = "mental"
        elif any(kw in title_lower for kw in ["睡眠", "sleep", "失眠"]):
            module = "sleep"
        elif any(kw in title_lower for kw in ["医疗", "medical", "疾病", "医院"]):
            module = "medical"
        else:
            module = "tips"
        return kb, module
    
    # 默认归类到AI
    return "ai-latest-news", "news"


def save_content(kb: str, module: str, content: dict, date_str: str):
    """保存内容到本地"""
    year = date_str[:4]
    month = date_str[5:7]
    day = date_str[8:10]
    
    # 文件路径：memory/kb-archive/{kb}/{year}/{month}/{day}.md
    file_path = MEMORY_DIR / "kb-archive" / kb / year / month / f"{day}.md"
    file_path.parent.mkdir(parents=True, exist_ok=True)
    
    # 构建内容
    entry = f"""
### [{content['title']}]({content['url']})
> 模块: {module} | 收集时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}

---
"""
    
    # 追加到文件
    if file_path.exists():
        with open(file_path, "a", encoding="utf-8") as f:
            f.write(entry)
    else:
        # 新文件，添加标题
        header = f"# {KB_CONFIG[kb]['name']} - {date_str} 日报\n\n"
        file_path.write_text(header + entry, encoding="utf-8")
    
    return file_path


def collect_kb(kb_key: str, date_str: str) -> dict:
    """收集单个知识库的内容"""
    config = KB_CONFIG[kb_key]
    print(f"\n{'='*60}")
    print(f"📚 收集: {config['name']}")
    print(f"{'='*60}")
    
    all_results = []
    new_count = 0
    duplicate_count = 0
    
    # 对每个搜索词执行搜索
    for query in config['search_queries']:
        results = search_content(query, days=COLLECT_DAYS)
        
        for result in results:
            url = result['url']
            title = result['title']
            
            # 去重检查
            if is_url_collected(url):
                print(f"  ⏭️  已收集，跳过: {title[:40]}...")
                duplicate_count += 1
                continue
            
            # 分类
            kb, module = classify_content(url, title)
            
            # 如果分类到当前知识库，保存内容
            if kb == kb_key:
                print(f"  ✅ 新内容: {title[:40]}... [{module}]")
                
                # 保存到本地
                save_content(kb, module, result, date_str)
                
                # 标记为已收集
                mark_url_collected(url, kb, title)
                
                new_count += 1
                all_results.append(result)
    
    return {
        "kb": kb_key,
        "name": config['name'],
        "new": new_count,
        "duplicate": duplicate_count,
        "total": new_count + duplicate_count
    }


def generate_summary(results: list, date_str: str) -> str:
    """生成收集汇总"""
    lines = []
    lines.append(f"\n{'='*60}")
    lines.append(f"📊 日报收集汇总 - {date_str}")
    lines.append(f"{'='*60}")
    lines.append(f"收集范围: 最近{COLLECT_DAYS}天")
    lines.append("")
    
    total_new = 0
    for r in results:
        lines.append(f"{r['name']}: {r['new']} 条新内容 ({r['duplicate']} 条重复已跳过)")
        total_new += r['new']
    
    lines.append("")
    lines.append(f"总计: {total_new} 条新内容")
    lines.append(f"{'='*60}\n")
    
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="日报收集（最近2天）")
    parser.add_argument("--date", help="日期 (YYYY-MM-DD，默认今天)")
    args = parser.parse_args()
    
    # 确定日期
    if args.date:
        date_str = args.date
    else:
        date_str = datetime.now().strftime("%Y-%m-%d")
    
    print("\n" + "="*60)
    print("🔄 日报收集")
    print("="*60)
    print(f"📅 日期: {date_str}")
    print(f"⏰ 收集范围: 最近{COLLECT_DAYS}天")
    print("="*60)
    
    # 确保目录
    ensure_dirs()
    
    # 收集所有知识库
    results = []
    for kb_key in KB_CONFIG.keys():
        result = collect_kb(kb_key, date_str)
        results.append(result)
    
    # 生成汇总
    summary = generate_summary(results, date_str)
    print(summary)
    
    # 保存汇总到日志
    log_dir = MEMORY_DIR / "logs" / "daily"
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / f"{date_str}.log"
    log_file.write_text(summary, encoding="utf-8")
    
    print(f"✅ 日志已保存: {log_file}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
