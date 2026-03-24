# 工作流优化方案 v2.0

> 基于 LitGate 全自动日报系统的实战经验优化
> 参考文章：《一套跑了 9 个月的全自动 AI 日报系统是怎么搭的》

---

## 📊 现状分析

### 当前工作流问题

| 问题 | 影响 | 优先级 |
|------|------|--------|
| 依赖 coze-web-search（已禁用）| 日报收集功能失效 | 🔴 高 |
| 串行处理，无并行 | 速度慢，耗时长 | 🟡 中 |
| 采集/分析/分发耦合 | 难以维护，无法单独替换 | 🟡 中 |
| 无中间格式 | 层间依赖严重 | 🟡 中 |
| 简单关键词分类 | 分类准确度低 | 🟢 低 |
| 无门禁机制 | 质量无法保证，可能推送垃圾内容 | 🟡 中 |

### LitGate 系统优势

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  数据采集层  │ ──→ │  AI分析层   │ ──→ │  内容分发层  │
│   (N8N)    │ RSS │  (Dify)    │ JSON │ (GitHub/企微)│
└─────────────┘     └─────────────┘     └─────────────┘
     解耦                解耦                解耦
```

1. **三层解耦**：各层通过标准格式（RSS/XML、JSON）串联
2. **并行提速**：三批并行 LLM，速度提升 3 倍
3. **门禁兜底**：JSON Schema 约束 + 安全阀机制
4. **稳定运行**：9 个月无故障

---

## 🎯 优化方案

### 核心原则

1. **三层解耦**：采集 / 分析 / 分发各管各的
2. **并行提速**：多线程/多进程处理
3. **门禁兜底**：每个关键环节都有校验
4. **渐进升级**：不影响现有功能的前提下逐步优化

---

## Phase 1: 紧急修复（已禁用 coze-web-search）

### 1.1 替换搜索方案

**方案 A：使用浏览器 + 搜索引擎**（推荐）
```python
# 使用 browser 工具访问搜索引擎
# 示例：site:jiqizhixin.com AI 2026
```

**方案 B：RSS 订阅源采集**（更稳定）
```python
# 使用 feedparser 解析 RSS
# 配置已存在于 content_sources.yaml
```

**方案 C：混合方案**（最全面）
- RSS 为主（稳定、实时）
- 浏览器搜索为辅（补充遗漏）
- 用户主动推送为补充（高质量）

### 1.2 快速实现

```bash
# 新增 RSS 采集脚本
python skills/knowledge-base/scripts/daily_collect_rss.py
```

---

## Phase 2: 架构解耦

### 2.1 三层架构设计

```
┌─────────────────────────────────────────────────────────────┐
│                      数据采集层 (Collect)                     │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │ RSS采集  │  │ 搜索采集 │  │ 用户推送 │  │ 手动录入 │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
│                      ↓                                      │
│              ┌──────────────┐                               │
│              │ raw_data.json│  ← 原始数据中间格式           │
│              └──────────────┘                               │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                      AI 分析层 (Analyze)                     │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────────────────────────────────────────────────┐  │
│  │              raw_data.json (输入)                     │  │
│  └──────────────────────────────────────────────────────┘  │
│                      ↓                                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │  去重过滤    │→│  LLM分析     │→│  评分排序    │     │
│  │              │  │ 分类/摘要    │  │              │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
│                      ↓                                      │
│              ┌──────────────┐                               │
│              │analyzed.json │  ← 分析结果中间格式           │
│              └──────────────┘                               │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                      内容分发层 (Distribute)                  │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │ 飞书知识库  │  │ 飞书对话    │  │ 本地存档    │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 中间格式定义

**raw_data.json**（采集层输出）
```json
{
  "collection_time": "2026-03-24T08:00:00Z",
  "source": "rss",
  "articles": [
    {
      "id": "sha256_hash",
      "title": "文章标题",
      "url": "https://...",
      "source_name": "机器之心",
      "published_at": "2026-03-24T07:00:00Z",
      "raw_content": "原始内容...",
      "collected_at": "2026-03-24T08:00:00Z"
    }
  ]
}
```

**analyzed.json**（分析层输出）
```json
{
  "analysis_time": "2026-03-24T08:05:00Z",
  "total_articles": 20,
  "valid_articles": 15,
  "top_articles": [
    {
      "id": "sha256_hash",
      "title": "文章标题",
      "url": "https://...",
      "kb": "ai-latest-news",
      "module": "news",
      "summary": "AI生成的摘要...",
      "keywords": ["GPT", "OpenAI"],
      "score": 8.5,
      "reason": "重要的技术突破...",
      "is_top": true
    }
  ]
}
```

---

## Phase 3: 并行提速

### 3.1 并行采集

```python
# 使用线程池并行采集多个 RSS 源
from concurrent.futures import ThreadPoolExecutor, as_completed

def fetch_rss(source):
    # 采集单个 RSS 源
    pass

with ThreadPoolExecutor(max_workers=5) as executor:
    futures = {executor.submit(fetch_rss, src): src for src in sources}
    for future in as_completed(futures):
        result = future.result()
        # 合并结果
```

### 3.2 并行 LLM 分析

```python
# 将文章分成 3 批，并行调用 LLM
def analyze_batch(articles_batch):
    # 调用 LLM API 分析一批文章
    pass

# 分 3 批并行处理
batch_size = len(articles) // 3
batches = [
    articles[0:batch_size],
    articles[batch_size:2*batch_size],
    articles[2*batch_size:]
]

with ThreadPoolExecutor(max_workers=3) as executor:
    results = list(executor.map(analyze_batch, batches))
```

### 3.3 预期性能提升

| 步骤 | 当前耗时 | 优化后 | 提升 |
|------|---------|--------|------|
| 采集 | 10-15 min | 3-5 min | 3x |
| LLM分析 | 20-30 min | 5-10 min | 3x |
| 推送 | 2-3 min | 2-3 min | - |
| **总计** | **30-50 min** | **10-18 min** | **3x** |

---

## Phase 4: 门禁兜底

### 4.1 JSON Schema 校验

```python
from jsonschema import validate, ValidationError

ANALYZED_SCHEMA = {
    "type": "object",
    "required": ["analysis_time", "total_articles", "valid_articles", "top_articles"],
    "properties": {
        "total_articles": {"type": "integer", "minimum": 0},
        "valid_articles": {"type": "integer", "minimum": 0},
        "top_articles": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["id", "title", "url", "kb", "score"],
                "properties": {
                    "score": {"type": "number", "minimum": 0, "maximum": 10}
                }
            }
        }
    }
}

def validate_output(data):
    try:
        validate(data, ANALYZED_SCHEMA)
        return True
    except ValidationError as e:
        print(f"❌ 输出格式校验失败: {e.message}")
        return False
```

### 4.2 安全阀机制

```python
# 门禁检查
def safety_check(analyzed_data):
    # 1. 最低文章数检查
    if analyzed_data["valid_articles"] < 5:
        print("❌ 有效文章不足 5 篇，终止推送")
        return False
    
    # 2. 质量检查：平均分是否过低
    avg_score = sum(a["score"] for a in analyzed_data["top_articles"]) / len(analyzed_data["top_articles"])
    if avg_score < 5.0:
        print(f"⚠️ 平均分 {avg_score} 过低，建议人工审核")
        return False
    
    # 3. 重复内容检查
    urls = [a["url"] for a in analyzed_data["top_articles"]]
    if len(urls) != len(set(urls)):
        print("❌ 存在重复 URL")
        return False
    
    return True
```

---

## Phase 5: LLM 智能分析

### 5.1 分析 Prompt 设计

```python
ARTICLE_ANALYSIS_PROMPT = """
你是一位资深科技资讯编辑。请对以下文章进行分析：

文章标题：{title}
文章内容：{content}

请输出以下 JSON 格式：
{{
    "kb": "ai-latest-news 或 game-development 或 healthy-living 或 link-collection",
    "module": "news/tools/research/cases/engine/design/art/audio/indie/fitness/nutrition/mental",
    "summary": "100字以内的核心摘要",
    "keywords": ["关键词1", "关键词2", "关键词3"],
    "score": 0-10 的质量评分,
    "reason": "评分理由",
    "is_top": true/false 是否值得放入 Top 10
}}

评分标准：
- 10分：重大技术突破、行业里程碑事件
- 8-9分：重要产品发布、深度技术解析
- 6-7分：一般性新闻、常规更新
- 4-5分：参考价值较低的内容
- 1-3分：质量差、重复内容
"""
```

### 5.2 调用方式

```python
import requests

def analyze_with_llm(articles):
    """使用 LLM 分析文章"""
    results = []
    
    for article in articles:
        prompt = ARTICLE_ANALYSIS_PROMPT.format(
            title=article["title"],
            content=article["raw_content"][:2000]  # 限制长度
        )
        
        # 调用 LLM API（如 Claude、GPT 等）
        response = call_llm_api(prompt)
        
        # 解析 JSON 输出
        try:
            analysis = json.loads(response)
            analysis["id"] = article["id"]
            analysis["title"] = article["title"]
            analysis["url"] = article["url"]
            results.append(analysis)
        except json.JSONDecodeError:
            print(f"⚠️ LLM 输出解析失败: {article['title']}")
    
    return results
```

---

## 📅 实施计划

### Week 1: 紧急修复
- [x] 禁用 coze-web-search（已完成）
- [ ] 实现 RSS 采集脚本 `daily_collect_rss.py`
- [ ] 更新 daily_pipeline.py 使用新采集方式

### Week 2: 架构解耦
- [ ] 设计中间格式（raw_data.json, analyzed.json）
- [ ] 重构采集层，输出 raw_data.json
- [ ] 创建独立的分析层脚本 `daily_analyze.py`

### Week 3: 并行提速
- [ ] 实现并行 RSS 采集
- [ ] 实现并行 LLM 分析（分 3 批）
- [ ] 性能测试和调优

### Week 4: 门禁与质量
- [ ] 实现 JSON Schema 校验
- [ ] 实现安全阀机制
- [ ] 集成到推送流程

---

## 🔄 新工作流命令

```bash
# 完整日报流程（新）
python skills/knowledge-base/scripts/daily_pipeline_v2.py

# 单独执行各阶段
python skills/knowledge-base/scripts/collect.py    # 采集
python skills/knowledge-base/scripts/analyze.py    # 分析
python skills/knowledge-base/scripts/distribute.py # 分发

# 手动触发
python skills/knowledge-base/scripts/collect.py --source rss
python skills/knowledge-base/scripts/collect.py --source search
python skills/knowledge-base/scripts/collect.py --source manual
```

---

## 📊 预期收益

| 指标 | 当前 | 优化后 | 提升 |
|------|------|--------|------|
| 总耗时 | 30-50 min | 10-18 min | **3x** |
| 分类准确度 | 60-70% | 85-95% | **+30%** |
| 系统稳定性 | 依赖外部服务 | 自主可控 | **高** |
| 可维护性 | 耦合严重 | 三层解耦 | **高** |
| 质量控制 | 无 | 多重门禁 | **高** |

---

*优化方案 v2.0 - 基于 LitGate 实战经验*
