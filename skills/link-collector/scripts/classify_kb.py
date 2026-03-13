#!/usr/bin/env python3
"""
通用知识库内容分类器
根据内容自动判断归属的知识库和模块
支持：AI最新资讯、游戏开发、健康生活、通用收藏
"""

import json
from urllib.parse import urlparse
from pathlib import Path

# 知识库分类规则
KNOWLEDGE_BASES = {
    "ai-latest-news": {
        "name": "🤖 AI最新资讯",
        "icon": "🤖",
        "space_id": "7616519632920251572",
        "description": "AI行业动态、技术突破、产品发布",
        "modules": {
            "news": {"name": "📰 行业资讯", "keywords": ["发布", "推出", "融资", "OpenAI", "GPT", "Claude", "Anthropic"]},
            "tools": {"name": "🛠️ 工具技巧", "keywords": ["工具", "教程", "技巧", "Prompt", "效率"]},
            "research": {"name": "📚 深度研究", "keywords": ["论文", "原理", "架构", "分析", "ArXiv"]},
            "cases": {"name": "💡 案例分享", "keywords": ["实践", "案例", "经验", "踩坑"]},
        },
        "keywords": ["ai", "artificial intelligence", "machine learning", "llm", "大模型", "人工智能", "机器学习", 
                     "deep learning", "神经网络", "openai", "anthropic", "gpt", "claude", "gemini"],
        "domains": ["openai.com", "anthropic.com", "deepmind.google", "ai.google", "arxiv.org", 
                    "jiqizhixin.com", "qbitai.com", "paperswithcode.com"]
    },
    
    "game-dev": {
        "name": "🎮 游戏开发",
        "icon": "🎮",
        "space_id": "7616735513310924004",
        "description": "游戏引擎、开发技术、独立游戏",
        "modules": {
            "engines": {"name": "🎮 游戏引擎", "keywords": ["Unity", "Unreal", "Godot", "引擎更新"]},
            "design": {"name": "🎯 游戏设计", "keywords": ["游戏设计", "机制", "玩法", "关卡"]},
            "tech": {"name": "💻 开发技术", "keywords": ["编程", "图形", "AI", "物理"]},
            "art": {"name": "🎨 美术资源", "keywords": ["美术", "模型", "动画", "特效"]},
            "audio": {"name": "🎵 音频音效", "keywords": ["音效", "音乐", "配音"]},
            "indie": {"name": "🏆 独立游戏", "keywords": ["独立游戏", "indie", "发布"]},
        },
        "keywords": ["game", "gaming", "unity", "unreal", "godot", "游戏", "游戏开发", "gamedev", 
                     "indie game", "游戏设计", "关卡设计"],
        "domains": ["unity.com", "unrealengine.com", "godotengine.org", "gamasutra.com", 
                    "gamedeveloper.com", "indienova.com", "itch.io"]
    },
    
    "healthy-living": {
        "name": "🌱 健康生活",
        "icon": "🌱",
        "space_id": "7616737910330510558",
        "description": "生活妙招、健康知识、运动健身",
        "modules": {
            "fitness": {"name": "🏃 运动健身", "keywords": ["运动", "健身", "锻炼", "跑步", "瑜伽"]},
            "nutrition": {"name": "🥗 饮食营养", "keywords": ["饮食", "营养", "食谱", "减肥", "健康"]},
            "mental": {"name": "😊 心理健康", "keywords": ["心理", "压力", "情绪", "焦虑", "冥想"]},
            "sleep": {"name": "💤 睡眠健康", "keywords": ["睡眠", "失眠", "作息"]},
            "medical": {"name": "🏥 医疗资讯", "keywords": ["疾病", "医疗", "预防", "健康检查"]},
            "tips": {"name": "✨ 生活妙招", "keywords": ["生活", "窍门", "技巧", "妙招"]},
        },
        "keywords": ["健康", "养生", "运动", "健身", "饮食", "营养", "心理", "睡眠", "医疗", 
                     "生活窍门", "health", "fitness", "nutrition", "wellness"],
        "domains": ["dxy.com", "39.net", "keep.com", "xinli001.com", "health.com"]
    },
    
    "link-collection": {
        "name": "🔗 链接收藏",
        "icon": "🔗",
        "space_id": None,
        "description": "其他技术文章、工具资源",
        "modules": {
            "frontend": {"name": "🌐 前端开发", "keywords": ["前端", "React", "Vue", "JavaScript", "CSS"]},
            "backend": {"name": "⚙️ 后端开发", "keywords": ["后端", "Node.js", "Python", "Java", "Go"]},
            "devops": {"name": "🚀 DevOps", "keywords": ["DevOps", "Docker", "K8s", "CI/CD"]},
            "tools": {"name": "🛠️ 效率工具", "keywords": ["工具", "软件", "效率", "自动化"]},
        },
        "keywords": [],
        "domains": ["github.com", "stackoverflow.com", "medium.com", "dev.to"]
    }
}

def extract_domain(url):
    """提取域名"""
    parsed = urlparse(url)
    domain = parsed.netloc.lower()
    if domain.startswith('www.'):
        domain = domain[4:]
    return domain

def classify_content(url, title="", content=""):
    """
    根据内容自动分类到知识库和模块
    返回: (kb_key, module_key, confidence, reason)
    """
    url_lower = url.lower()
    title_lower = title.lower()
    content_lower = content.lower()
    combined_text = f"{url_lower} {title_lower} {content_lower}"
    
    # 第一步：判断知识库
    kb_scores = {}
    
    for kb_key, kb_info in KNOWLEDGE_BASES.items():
        score = 0
        reasons = []
        
        # 1. 域名匹配
        domain = extract_domain(url)
        for kb_domain in kb_info.get("domains", []):
            if kb_domain in domain:
                score += 50
                reasons.append(f"域名: {kb_domain}")
                break
        
        # 2. 关键词匹配
        matched_keywords = []
        for keyword in kb_info.get("keywords", []):
            if keyword.lower() in combined_text:
                score += 10
                matched_keywords.append(keyword)
        
        if matched_keywords:
            reasons.append(f"关键词: {', '.join(matched_keywords[:3])}")
        
        kb_scores[kb_key] = {
            "score": score,
            "reasons": reasons
        }
    
    # 选择最佳知识库
    if not kb_scores:
        return None, None, 0, "无法分类"
    
    best_kb = max(kb_scores.items(), key=lambda x: x[1]["score"])
    kb_key, kb_data = best_kb
    
    # 如果知识库得分过低，可能是通用内容
    if kb_data["score"] < 20:
        kb_key = "link-collection"
    
    kb_info = KNOWLEDGE_BASES[kb_key]
    
    # 第二步：判断模块（如果有模块定义）
    module_key = None
    module_score = 0
    
    if "modules" in kb_info and kb_info["modules"]:
        module_scores = {}
        
        for mod_key, mod_info in kb_info["modules"].items():
            score = 0
            matched = []
            
            for keyword in mod_info.get("keywords", []):
                if keyword.lower() in combined_text:
                    score += 15
                    matched.append(keyword)
            
            if matched:
                module_scores[mod_key] = {
                    "score": score,
                    "matched": matched
                }
        
        if module_scores:
            best_mod = max(module_scores.items(), key=lambda x: x[1]["score"])
            module_key, mod_data = best_mod
            module_score = mod_data["score"]
    
    # 计算总体置信度
    total_score = kb_data["score"] + module_score
    confidence = min(total_score / 100, 1.0)
    
    # 生成原因说明
    reason_parts = [f"知识库: {kb_info['name']}"]
    if kb_data["reasons"]:
        reason_parts.extend(kb_data["reasons"])
    if module_key:
        mod_name = kb_info["modules"][module_key]["name"]
        reason_parts.append(f"模块: {mod_name}")
    
    reason = "; ".join(reason_parts)
    
    return kb_key, module_key, confidence, reason

def batch_classify(links):
    """
    批量分类链接
    links: [{"url": "...", "title": "...", "content": "..."}, ...]
    返回按知识库和模块分类的结果
    """
    results = {}
    
    # 初始化结构
    for kb_key in KNOWLEDGE_BASES.keys():
        kb_info = KNOWLEDGE_BASES[kb_key]
        results[kb_key] = {
            "name": kb_info["name"],
            "icon": kb_info.get("icon", ""),
            "modules": {}
        }
        
        if "modules" in kb_info:
            for mod_key in kb_info["modules"].keys():
                results[kb_key]["modules"][mod_key] = []
        else:
            results[kb_key]["items"] = []
    
    # 分类
    for link in links:
        url = link.get("url", "")
        title = link.get("title", "")
        content = link.get("content", "")
        
        kb_key, module_key, confidence, reason = classify_content(url, title, content)
        
        item = {
            "url": url,
            "title": title,
            "content": content,
            "confidence": confidence,
            "reason": reason
        }
        
        if kb_key and kb_key in results:
            if module_key and module_key in results[kb_key].get("modules", {}):
                results[kb_key]["modules"][module_key].append(item)
            else:
                if "items" not in results[kb_key]:
                    results[kb_key]["items"] = []
                results[kb_key]["items"].append(item)
    
    return results

def get_kb_info(kb_key):
    """获取知识库信息"""
    return KNOWLEDGE_BASES.get(kb_key)

def print_classification(results):
    """打印分类结果"""
    for kb_key, kb_data in results.items():
        if kb_data.get("modules"):
            has_content = any(len(v) > 0 for v in kb_data["modules"].values())
        else:
            has_content = len(kb_data.get("items", [])) > 0
        
        if not has_content:
            continue
        
        print(f"\n{kb_data['icon']} {kb_data['name']}")
        print("=" * 60)
        
        if kb_data.get("modules"):
            for mod_key, items in kb_data["modules"].items():
                if items:
                    kb_info = KNOWLEDGE_BASES[kb_key]
                    mod_info = kb_info["modules"][mod_key]
                    print(f"\n  {mod_info['name']} ({len(items)}篇):")
                    for item in items:
                        conf = item['confidence']
                        conf_emoji = "🟢" if conf > 0.7 else "🟡" if conf > 0.4 else "🔴"
                        print(f"    {conf_emoji} {item['title'][:50]}... ({conf:.0%})")
        
        if kb_data.get("items"):
            print(f"\n  通用收藏 ({len(kb_data['items'])}篇):")
            for item in kb_data["items"]:
                conf = item['confidence']
                conf_emoji = "🟢" if conf > 0.7 else "🟡" if conf > 0.4 else "🔴"
                print(f"    {conf_emoji} {item['title'][:50]}... ({conf:.0%})")

if __name__ == "__main__":
    # 测试
    test_links = [
        # AI资讯
        {"url": "https://openai.com/blog/gpt-4-5", "title": "OpenAI 发布 GPT-4.5：新功能全面升级", "content": "OpenAI今天宣布推出GPT-4.5..."},
        {"url": "https://arxiv.org/abs/2403.xxxxx", "title": "Attention Is All You Need: Transformer原理深度解析", "content": "本文深入分析了Transformer的注意力机制..."},
        
        # 游戏开发
        {"url": "https://unity.com/blog/unity-6", "title": "Unity 6 新特性介绍", "content": "Unity Technologies宣布推出Unity 6..."},
        {"url": "https://indienova.com/article/xxx", "title": "独立游戏开发心得：从0到发布Steam", "content": "记录我开发独立游戏的完整历程..."},
        
        # 健康生活
        {"url": "https://dxy.com/health-tips", "title": "春季养生：如何调理身体", "content": "春季是养生的好时机..."},
        {"url": "https://keep.com/workout-plan", "title": "30天健身计划：从入门到进阶", "content": "科学的健身计划帮助你..."},
        
        # 通用技术
        {"url": "https://github.com/xxx/react-hooks", "title": "React Hooks最佳实践", "content": "分享React Hooks的使用技巧..."},
    ]
    
    print("🤖 通用知识库内容分类器")
    print("=" * 60)
    
    results = batch_classify(test_links)
    print_classification(results)
    
    print("\n" + "=" * 60)
    print("\n📊 统计汇总:")
    for kb_key, kb_data in results.items():
        count = 0
        if kb_data.get("modules"):
            count = sum(len(v) for v in kb_data["modules"].values())
        else:
            count = len(kb_data.get("items", []))
        if count > 0:
            print(f"  {kb_data['icon']} {kb_data['name']}: {count}篇")
