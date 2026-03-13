#!/usr/bin/env python3
"""
AI内容四模块分类器
根据链接内容自动判断归属：资讯、工具技巧、深度研究、案例分享
"""

import json
from urllib.parse import urlparse
from pathlib import Path

# 四模块分类规则
CONTENT_MODULES = {
    "ai-news": {
        "name": "📰 AI行业资讯",
        "description": "新闻、产品发布、融资动态、行业数据",
        "keywords": [
            "发布", "推出", "上线", "融资", "估值", "亿美元", "收购", "合并",
            "OpenAI", "Anthropic", "Google", "Meta", "Microsoft", "AI巨头",
            "GPT", "Claude", "Llama", "Gemini", "大模型",
            "行业", "市场", "报告", "数据", "趋势",
            "突破", "进展", "里程碑", "首次", "最新",
            "CEO", "创始人", "高管", "采访", "演讲"
        ],
        "domains": [
            "techcrunch.com", "theverge.com", "wired.com",
            "jiqizhixin.com", "qbitai.com", "syncedreview.com",
            "xinhuanet.com", "people.com.cn", "cctv.com"
        ]
    },
    "ai-tools": {
        "name": "🛠️ AI工具与技巧",
        "description": "工具推荐、使用教程、Prompt技巧、效率方案",
        "keywords": [
            "工具", "推荐", "教程", "指南", "使用", "技巧", "方法",
            "Prompt", "提示词", "调教", "优化",
            "ChatGPT", "Claude", "Midjourney", "Stable Diffusion", "Copilot",
            "效率", "生产力", "自动化", "工作流",
            "How to", "攻略", "入门", "上手", "实践",
            "插件", "扩展", "应用", "软件", "APP"
        ],
        "domains": [
            "github.com", "huggingface.co",
            "youtube.com", "bilibili.com",
            "zhihu.com", "juejin.cn", "csdn.net"
        ]
    },
    "ai-research": {
        "name": "📚 主题深度研究",
        "description": "技术原理、趋势分析、论文解读、架构设计",
        "keywords": [
            "论文", "研究", "原理", "机制", "架构", "设计",
            "分析", "解析", "剖析", "深入", "底层",
            "Transformer", "Attention", "神经网络", "深度学习", "强化学习",
            "ArXiv", "论文解读", "综述", "survey",
            "AGI", "通用人工智能", "未来", "趋势", "预测",
            "技术", "算法", "模型", "训练", "推理"
        ],
        "domains": [
            "arxiv.org", "paperswithcode.com",
            "openai.com/research", "deepmind.google",
            "distill.pub", "mit.edu", "stanford.edu"
        ]
    },
    "ai-cases": {
        "name": "💡 经验与案例分享",
        "description": "实战经验、踩坑记录、成功案例、最佳实践",
        "keywords": [
            "实践", "实战", "案例", "项目", "应用", "落地",
            "经验", "总结", "复盘", "反思", "踩坑", "避坑",
            "成功", "失败", "教训", "心得", "体会",
            "从0到1", "构建", "搭建", "实现", "开发",
            "我们", "公司", "团队", "项目", "产品",
            "最佳实践", "规范", "标准", "流程"
        ],
        "domains": [
            "medium.com", "substack.com",
            "mp.weixin.qq.com", "zhuanlan.zhihu.com",
            "juejin.cn", "segmentfault.com"
        ]
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
    根据内容自动分类到四个模块
    返回: (module_key, confidence, reason)
    """
    url_lower = url.lower()
    title_lower = title.lower()
    content_lower = content.lower()
    combined_text = f"{url_lower} {title_lower} {content_lower}"
    
    scores = {}
    
    for module_key, module_info in CONTENT_MODULES.items():
        score = 0
        reasons = []
        
        # 1. 检查域名匹配
        domain = extract_domain(url)
        for mod_domain in module_info["domains"]:
            if mod_domain in domain:
                score += 40
                reasons.append(f"域名匹配: {mod_domain}")
                break
        
        # 2. 检查关键词匹配
        matched_keywords = []
        for keyword in module_info["keywords"]:
            if keyword.lower() in combined_text:
                score += 8
                matched_keywords.append(keyword)
        
        if matched_keywords:
            reasons.append(f"关键词: {', '.join(matched_keywords[:3])}")
        
        scores[module_key] = {
            "score": score,
            "reasons": reasons,
            "name": module_info["name"]
        }
    
    # 选择得分最高的
    if scores:
        best_match = max(scores.items(), key=lambda x: x[1]["score"])
        module_key, info = best_match
        
        # 如果最高分过低，可能是未分类内容
        if info["score"] < 20:
            return None, 0.3, "置信度较低，建议人工确认"
        
        confidence = min(info["score"] / 100, 1.0)
        reason = "; ".join(info["reasons"]) if info["reasons"] else "内容匹配"
        
        return module_key, confidence, reason
    
    return None, 0, "无法分类"

def batch_classify(links):
    """
    批量分类链接
    links: [{"url": "...", "title": "...", "content": "..."}, ...]
    """
    results = {
        "ai-news": [],
        "ai-tools": [],
        "ai-research": [],
        "ai-cases": [],
        "uncategorized": []
    }
    
    for link in links:
        url = link.get("url", "")
        title = link.get("title", "")
        content = link.get("content", "")
        
        module_key, confidence, reason = classify_content(url, title, content)
        
        if module_key:
            results[module_key].append({
                "url": url,
                "title": title,
                "content": content,
                "confidence": confidence,
                "reason": reason
            })
        else:
            results["uncategorized"].append({
                "url": url,
                "title": title,
                "content": content,
                "confidence": confidence,
                "reason": reason
            })
    
    return results

def get_module_info(module_key):
    """获取模块信息"""
    return CONTENT_MODULES.get(module_key)

if __name__ == "__main__":
    # 测试
    test_links = [
        {
            "url": "https://openai.com/blog/gpt-4-5", 
            "title": "OpenAI 发布 GPT-4.5：新功能全面升级",
            "content": "OpenAI今天宣布推出GPT-4.5，带来了更强大的推理能力和..."
        },
        {
            "url": "https://mp.weixin.qq.com/s/xxx", 
            "title": "我用ChatGPT提升工作效率的10个技巧",
            "content": "分享我在日常工作中使用ChatGPT的实用技巧..."
        },
        {
            "url": "https://arxiv.org/abs/2403.xxxxx", 
            "title": "Attention Is All You Need: 深入解析Transformer架构",
            "content": "本文深入分析了Transformer的注意力机制原理..."
        },
        {
            "url": "https://zhuanlan.zhihu.com/p/xxx", 
            "title": "从零搭建一个AI客服系统的踩坑记录",
            "content": "记录我们团队在构建AI客服系统过程中遇到的问题..."
        }
    ]
    
    results = batch_classify(test_links)
    
    for module, items in results.items():
        if items:
            info = get_module_info(module)
            name = info["name"] if info else "未分类"
            print(f"\n{name} ({len(items)}篇):")
            for item in items:
                print(f"  - {item['title'][:40]}... (置信度: {item['confidence']:.2f})")
    
    print("\n" + "="*60)
    print(json.dumps(results, ensure_ascii=False, indent=2))
