---
name: knowledge-base
description: |
  统一的知识库管理系统，整合日报、周报、链接收集、推送、清理等全部功能。
  遵循 WORKSPACE/RULES.md 中的统一规则。
  
  核心功能：
  1. 日报收集（最近2天）
  2. 周报汇总
  3. 链接收集（用户发送的链接）
  4. 微信文章归档
  5. B站视频归档
  6. 推送到飞书
  7. 内容清理
  
  Triggers: "收集日报", "收集周报", "收集链接", "归档文章", "推送知识库", "清理内容"
---

# Knowledge Base - 统一知识库管理

工作区的**唯一**知识库管理 skill，整合所有内容收集、分类、推送、清理功能。

包括：
- ✅ 日报/周报自动收集
- ✅ 用户链接收集（AI/游戏/健康自动分类）
- ✅ 微信文章归档
- ✅ B站视频归档
- ✅ 飞书知识库同步
- ✅ 内容自动清理

---

## 📋 核心规则（来自 RULES.md）

### 规则1：日报收集范围
- **只收集最近2天**发布的内容
- 已收集的 URL 不再重复收集

### 规则2：保留策略
| 内容类型 | 保留时间 | 自动清理 |
|----------|----------|----------|
| 日报 | 7天 | ✅ |
| 周报 | 30天 | ✅ |
| 链接收藏 | 永久 | ❌ |

### 规则3：飞书层级结构
```
2026年 → 3月 → 3月17日 日报
              → 3月18日 日报
              → 第12期 - 03.17-03.23 周报
```

---

## 🚀 快速使用

### 1️⃣ 日报收集（最近2天）
```bash
# 收集日报
python skills/knowledge-base/scripts/daily_collect.py

# 或完整流程（收集+推送）
python skills/knowledge-base/scripts/daily_pipeline.py
```

### 2️⃣ 周报收集
```bash
# 收集周报
python skills/knowledge-base/scripts/weekly_collect.py

# 推送周报
python skills/knowledge-base/scripts/weekly_push.py
```

### 3️⃣ 链接收集（用户发送的链接）
```bash
# 收集单个链接（自动分类到AI/游戏/健康）
python skills/knowledge-base/scripts/collect_link.py --url "https://..."

# 带标题
python skills/knowledge-base/scripts/collect_link.py --url "https://..." --title "文章标题"
```

**分类规则**：
| 内容类型 | 目标位置 |
|----------|----------|
| AI/技术文章 | 🤖 AI最新资讯 知识库 |
| 游戏/开发 | 🎮 游戏开发 知识库 |
| 健康/生活 | 🌱 健康生活 知识库 |
| 其他技术 | 🔗 本地链接收藏 |

### 4️⃣ 微信文章归档
```bash
# 归档微信文章
python skills/knowledge-base/scripts/archive_wechat.py --url "https://mp.weixin.qq.com/s/..."

# 自动分类
python skills/knowledge-base/scripts/archive_wechat.py --url "..." --auto-classify
```

### 5️⃣ B站视频归档
```bash
# 归档B站视频
python skills/knowledge-base/scripts/archive_bilibili.py --url "https://b23.tv/..."
```

### 6️⃣ 内容清理
```bash
# 清理过期内容
python skills/knowledge-base/scripts/cleanup.py
```

### 7️⃣ 查看状态
```bash
# 查看任务执行状态
python skills/knowledge-base/scripts/check_status.py
```

---

## 📁 脚本列表

| 脚本 | 功能 | 使用场景 |
|------|------|----------|
| `daily_collect.py` | 收集最近2天内容 | 定时任务 |
| `daily_push.py` | 推送日报到飞书 | 定时任务 |
| `daily_pipeline.py` | 日报完整流程 | 定时任务 |
| `weekly_collect.py` | 收集本周内容 | 周五定时 |
| `weekly_push.py` | 推送周报到飞书 | 周六定时 |
| **⭐ `collect_link.py`** | **收集用户链接** | **用户发送链接时** |
| `archive_wechat.py` | 归档微信文章 | 收到微信文章 |
| `archive_bilibili.py` | 归档B站视频 | 收到B站链接 |
| `cleanup.py` | 清理过期内容 | 每天定时 |
| `git_sync.py` | Git同步 | 每天定时 |
| `check_status.py` | 查看任务状态 | 按需 |

---

## 📊 知识库配置

### 三个知识库

| 知识库 | 空间ID | 模块数 | 模块列表 |
|--------|--------|--------|----------|
| 🤖 AI最新资讯 | 7616519632920251572 | 4 | 行业资讯、工具技巧、深度研究、案例分享 |
| 🎮 游戏开发 | 7616735513310924004 | 6 | 游戏引擎、游戏设计、开发技术、美术资源、音频音效、独立游戏 |
| 🌱 健康生活 | 7616737910330510558 | 6 | 运动健身、饮食营养、心理健康、睡眠健康、医疗资讯、生活妙招 |

### 链接分类关键词

#### 🤖 AI关键词
`ai`, `人工智能`, `gpt`, `claude`, `openai`, `anthropic`, `llm`, `大模型`, `机器学习`

#### 🎮 游戏关键词
`game`, `游戏`, `unity`, `unreal`, `godot`, `indie`, `gamedev`

#### 🌱 健康关键词
`健康`, `health`, `健身`, `运动`, `饮食`, `心理`, `生活`

---

## 🗂️ 存储结构

### 知识库内容
```
memory/kb-archive/
├── ai-latest-news/
│   └── 2026/
│       └── 03/
│           ├── 17.md          # 日报
│           ├── 18.md          # 日报
│           └── week-12.md     # 周报
├── game-development/
└── healthy-living/
```

### 链接收藏
```
memory/link-collection/
├── 2026/
│   └── 03/
│       ├── 2026-03-19.md      # 其他技术链接
│       └── wechat/
│           └── 2026-03-19.md  # 微信文章
└── bilibili/
    └── 2026-03-19.md          # B站视频
```

---

## 🔗 链接收集工作流

### 用户发送链接时的处理流程

```
用户发送链接
    ↓
收集链接信息（URL、标题）
    ↓
自动分类（AI/游戏/健康/其他）
    ↓
获取内容（使用 coze-web-fetch）
    ↓
保存到对应位置
    ├── AI/游戏/健康 → 知识库日报 + 飞书
    └── 其他技术 → 本地链接收藏
    ↓
标记为已收集（防止重复）
    ↓
反馈用户结果
```

### 使用示例

**用户发送**：`https://b23.tv/vWwyalF`

**自动处理**：
```bash
python skills/knowledge-base/scripts/collect_link.py \
  --url "https://b23.tv/vWwyalF" \
  --title "APP 从 0 → 上线发布！免费 Vibe Coding 流程"
```

**输出**：
```
🔗 处理链接: https://b23.tv/vWwyalF...
📂 分类: 🤖 AI最新资讯 / tools
📊 置信度: 0.85
✅ 已保存到知识库: memory/kb-archive/ai-latest-news/2026/03/19.md
```

---

## 🔄 自动化任务

### Crontab 配置

```bash
# 日报：每天 08:00
0 8 * * * cd /workspace/projects/workspace && python skills/knowledge-base/scripts/daily_pipeline.py

# 周报：每周五 18:00
0 18 * * 5 cd /workspace/projects/workspace && python skills/knowledge-base/scripts/weekly_pipeline.py

# 清理：每天 23:00
0 23 * * * cd /workspace/projects/workspace && python skills/knowledge-base/scripts/cleanup.py

# Git同步：每天 22:00
0 22 * * * cd /workspace/projects/workspace && python skills/knowledge-base/scripts/git_sync.py
```

---

## 📝 日志和监控

### 日志位置
- 日报日志：`memory/logs/daily/YYYY-MM-DD.log`
- 周报日志：`memory/logs/weekly/YYYY-WXX.log`
- 链接收集：`memory/logs/links/YYYY-MM-DD.log`

### 状态文件
- 已收集URL：`memory/state/collected-urls.json`
- 任务状态：`memory/state/task-state.json`

---

## 🔗 相关文档

- **统一规则**：`WORKSPACE/RULES.md`
- **心跳任务**：`WORKSPACE/HEARTBEAT.md`

---

*统一知识库管理 - 一个 skill 管理所有内容收集*
