#!/usr/bin/env python3
"""
智能链接分类器
根据链接内容自动判断适合放入哪个知识库
"""

import json
from urllib.parse import urlparse
from pathlib import Path

# 知识库分类规则
KNOWLEDGE_BASES = {
    "ai-latest-news": {
        "name": "AI最新资讯",
        "space_id": "7616519632920251572",
        "keywords": ["ai", "artificial intelligence", "machine learning", "llm", "大模型", "人工智能", "机器学习", "deep learning", "神经网络", "openai", "anthropic", "gpt", "claude"],
        "domains": ["openai.com", "anthropic.com", "deepmind.google", "ai.google", "arxiv.org", "paperswithcode.com", "jiqizhixin.com", "qbitai.com", "xinhuanet.com", "people.com.cn"],
        "categories": ["AI新闻", "技术突破", "产品发布", "研究论文"]
    },
    "game-dev": {
        "name": "游戏开发",
        "space_id": "7616735513310924004",
        "keywords": ["game", "gaming", "unity", "unreal", "godot", "游戏", "游戏开发", "unity3d", "ue5", "game design", "gamedev", "indie game"],
        "domains": ["unity.com", "unrealengine.com", "godotengine.org", "gamasutra.com", "gamedeveloper.com", "indiegames.com", "steamcommunity.com", "itch.io"],
        "categories": ["游戏引擎", "游戏设计", "开发教程", "行业资讯"]
    },
    "link-collection": {
        "name": "链接收藏",
        "space_id": None,  # 飞书文档
        "keywords": [],  # 通用收藏
        "domains": [],
        "categories": ["技术文章", "工具资源", "教程", "其他"]
    }
}

def extract_domain(url):
    """提取域名"""
    parsed = urlparse(url)
    domain = parsed.netloc.lower()
    if domain.startswith('www.'):
        domain = domain[4:]
    return domain

def classify_link(url, title="", content=""):
    """
    根据链接内容智能分类
    返回: (knowledge_base_key, confidence, reason)
    """
    url_lower = url.lower()
    title_lower = title.lower()
    content_lower = content.lower()
    combined_text = f"{url_lower} {title_lower} {content_lower}"
    
    scores = {}
    
    for kb_key, kb_info in KNOWLEDGE_BASES.items():
        score = 0
        reasons = []
        
        # 1. 检查域名匹配
        domain = extract_domain(url)
        if kb_info["domains"]:
            for kb_domain in kb_info["domains"]:
                if kb_domain in domain:
                    score += 50
                    reasons.append(f"域名匹配: {kb_domain}")
                    break
        
        # 2. 检查关键词匹配
        if kb_info["keywords"]:
            matched_keywords = []
            for keyword in kb_info["keywords"]:
                if keyword.lower() in combined_text:
                    score += 10
                    matched_keywords.append(keyword)
            if matched_keywords:
                reasons.append(f"关键词: {', '.join(matched_keywords[:3])}")
        
        scores[kb_key] = {
            "score": score,
            "reasons": reasons,
            "name": kb_info["name"]
        }
    
    # 选择得分最高的
    if scores:
        best_match = max(scores.items(), key=lambda x: x[1]["score"])
        kb_key, info = best_match
        
        # 如果最高分是0，放入链接收藏
        if info["score"] == 0:
            return "link-collection", 0.5, "未匹配到特定分类，放入链接收藏"
        
        confidence = min(info["score"] / 100, 1.0)
        reason = "; ".join(info["reasons"]) if info["reasons"] else "内容匹配"
        
        return kb_key, confidence, reason
    
    return "link-collection", 0.5, "默认分类"

def get_kb_info(kb_key):
    """获取知识库信息"""
    return KNOWLEDGE_BASES.get(kb_key, KNOWLEDGE_BASES["link-collection"])

def batch_classify(links):
    """
    批量分类链接
    links: [{"url": "...", "title": "...", "content": "..."}, ...]
    返回: 按知识库分类的结果
    """
    results = {
        "ai-latest-news": [],
        "game-dev": [],
        "link-collection": []
    }
    
    for link in links:
        url = link.get("url", "")
        title = link.get("title", "")
        content = link.get("content", "")
        
        kb_key, confidence, reason = classify_link(url, title, content)
        
        results[kb_key].append({
            "url": url,
            "title": title,
            "content": content,
            "confidence": confidence,
            "reason": reason
        })
    
    return results

if __name__ == "__main__":
    # 测试
    test_links = [
        {"url": "https://openai.com/blog/gpt-5", "title": "GPT-5 Released"},
        {"url": "https://unity.com/blog/unity-6", "title": "Unity 6新特性"},
        {"url": "https://example.com/random-article", "title": "随机文章"}
    ]
    
    results = batch_classify(test_links)
    print(json.dumps(results, ensure_ascii=False, indent=2))
