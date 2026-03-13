---
name: link-collector
description: |
  Collect and organize multiple URLs into structured documents. 
  Store links ONLY in local filesystem (memory/link-collection/), NOT in Feishu knowledge bases.
  Links are classified by content and should be stored in the correct knowledge base:
  - AI-related → AI最新资讯
  - Game-related → 游戏开发  
  - Health-related → 健康生活
  - Other tech → link-collection (local only)
  Use when user wants to save, bookmark, or organize web links.
---

# Link Collector

批量抓取网页链接并整理成结构化文档，**仅存储在本地文件系统**，不按知识库冗余存放。

## ⚠️ 重要：分类存储规则

**每个链接必须按内容严格分类，不可冗余存放：**

| 内容类型 | 存储位置 | 示例关键词 |
|----------|----------|------------|
| **AI/技术文章** | 🤖 **AI最新资讯** 知识库 | AI、机器学习、LLM、GPT、OpenAI、Claude |
| **游戏/开发** | 🎮 **游戏开发** 知识库 | Unity、Unreal、游戏设计、独立游戏 |
| **健康/生活** | 🌱 **健康生活** 知识库 | 健康、运动、饮食、心理、医疗、生活窍门 |
| **其他技术** | 🔗 **本地文件系统** | 前端、后端、工具、教程等无法归入以上三类的 |

### 严格禁止
- ❌ 将AI文章存入健康生活
- ❌ 将游戏文章存入AI资讯
- ❌ 同一文章在多个知识库重复存放
- ❌ 无法分类的文章强行归类

### 处理流程
1. 分析链接内容
2. 匹配最适合的知识库
3. **无法匹配时 → 反馈给用户，不强行存储**

---

## 📁 本地存储结构

**仅在本地文件系统存储**（`memory/link-collection/`），**不存入飞书知识库**：

```
link-collection/
├── user-links/              # 用户发送的链接（无法归入AI/游戏/健康的其他技术链接）
│   ├── 2026/
│   │   ├── 03/
│   │   │   ├── week-11/
│   │   │   │   └── 2026-03-13.md
│   │   │   └── month-index-03.md
│   │   └── archive/
│   │       └── 2025/
├── self-collected/          # 系统自动收集的链接
└── wechat-articles/         # 微信文章（无法归入AI/游戏/健康的）
```

### 层级结构

| 层级 | 单位 | 说明 | 示例 |
|------|------|------|------|
| **Level 1** | 年 | 年份文件夹 | `2026/` |
| **Level 2** | 月 | 月份文件夹 | `03/` |
| **Level 3** | 周 | 周次文件夹 | `week-11/` |
| **Level 4** | 日 | 每日文档 | `2026-03-13.md` |
| **Archive** | 年 | 超过1年归档 | `archive/2025/` |

---

## 🔍 内容分类判断

### AI最新资讯（关键词）
- AI、人工智能、机器学习、深度学习
- LLM、大模型、GPT、Claude、Gemini
- OpenAI、Anthropic、Google AI
- 神经网络、NLP、计算机视觉

### 游戏开发（关键词）
- Unity、Unreal、Godot
- 游戏开发、游戏设计、独立游戏
- 游戏引擎、游戏美术、游戏音效
- gamedev、indie game

### 健康生活（关键词）
- 健康、养生、保健
- 运动、健身、锻炼
- 饮食、营养、食谱
- 心理、情绪、压力
- 睡眠、作息
- 医疗、疾病、预防
- 生活窍门、生活妙招

### 链接收藏（本地存储，以上均不匹配）
- 前端开发、后端开发
- 通用编程、算法
- 工具软件、效率工具
- 无法明确归类的其他内容

---

## 🛠️ 归档管理器

### 添加链接（仅本地存储）

```bash
# 添加用户发送的链接（其他技术类）
python3 scripts/archive_manager.py \
  --action add \
  --category user-links \
  --url "https://example.com/article" \
  --title "文章标题" \
  --summary "文章摘要" \
  --source "网站名"
```

### 生成本周汇总

```bash
python3 scripts/archive_manager.py \
  --action week-summary \
  --category user-links
```

### 归档旧内容（>1年）

```bash
python3 scripts/archive_manager.py --action archive
```

---

## 🔗 链接引用格式

```markdown
### [文章标题](URL)
文章摘要...

> 来源：[网站名](URL) · 发布日期

---
```

---

## 📋 分类示例

| 链接内容 | 分类判断 | 存储位置 |
|----------|----------|----------|
| OpenAI GPT-5发布 | AI相关 | AI最新资讯知识库 |
| Unity 6新特性 | 游戏相关 | 游戏开发知识库 |
| 春季养生食谱 | 健康相关 | 健康生活知识库 |
| React新特性介绍 | 其他技术 | 本地 link-collection/user-links/ |
| Vue3最佳实践 | 其他技术 | 本地 link-collection/user-links/ |
| 无法判断内容 | 不明确 | **反馈给用户，不存储** |

---

## ⚠️ 错误示例（禁止）

❌ **错误**：将技术文章存入健康生活
```
文章：Skills开发指南（AI技术）
错误存储：健康生活知识库
正确存储：AI最新资讯知识库
```

❌ **错误**：同一文章多处存放
```
文章：AI在游戏开发中的应用
错误存储：同时存入AI资讯 + 游戏开发
正确存储：根据主要内容选择其一（如侧重AI技术则存AI资讯）
```

❌ **错误**：强行归类
```
文章：某模糊内容
错误处理：随意归入某个知识库
正确处理：反馈给用户"无法分类，请确认存储位置"
```

---

## 🤖 通用内容分类器

自动将内容分类到四个知识库及各自模块：

### 支持的知识库

| 知识库 | 模块 | 说明 |
|--------|------|------|
| **🤖 AI最新资讯** | 📰 行业资讯 / 🛠️ 工具技巧 / 📚 深度研究 / 💡 案例分享 | AI行业动态 |
| **🎮 游戏开发** | 🎮 游戏引擎 / 🎯 游戏设计 / 💻 开发技术 / 🎨 美术资源 / 🎵 音频音效 / 🏆 独立游戏 | 游戏开发 |
| **🌱 健康生活** | 🏃 运动健身 / 🥗 饮食营养 / 😊 心理健康 / 💤 睡眠健康 / 🏥 医疗资讯 / ✨ 生活妙招 | 健康生活 |
| **🔗 链接收藏** | 🌐 前端开发 / ⚙️ 后端开发 / 🚀 DevOps / 🛠️ 效率工具 | 其他技术 |

### 使用方法

```bash
# 单条分类
python3 scripts/classify_kb.py

# 在Python中使用
from classify_kb import classify_content

kb_key, module_key, confidence, reason = classify_content(
    url="https://...",
    title="文章标题",
    content="文章内容"
)
# 返回: ("ai-latest-news", "research", 0.95, "知识库: AI最新资讯; 模块: 深度研究")
```

### 分类结果示例

```
🤖 AI最新资讯
  📰 行业资讯 (1篇): OpenAI发布GPT-4.5
  📚 深度研究 (1篇): Transformer原理解析

🎮 游戏开发
  🎮 游戏引擎 (1篇): Unity 6新特性
  🏆 独立游戏 (1篇): 独立游戏开发心得

🌱 健康生活
  🏃 运动健身 (1篇): 30天健身计划
```

### 应用场景

1. **手动收集链接时**：自动判断应存入哪个知识库
2. **自动内容收集时**：按分类归档到不同模块
3. **微信文章归档时**：智能识别内容类型

---

*最后更新: 2026-03-13*