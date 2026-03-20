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

# ⚠️ 飞书同步路径规则（重要）

## 同步策略

**核心原则：先查询飞书 → 有则复用 → 无则创建 → 避免重复**

### 查询路径
```
1. 列出首页下的子节点
   feishu_wiki --action nodes --space_id <space_id> --parent_node_token <root_token>

2. 查找匹配的年份节点（如："2026年"）
   - 找到 → 复用 node_token
   - 未找到 → 创建新节点

3. 在年份节点下查找月份节点（如："3月"）
   - 找到 → 复用 node_token
   - 未找到 → 创建新节点

4. 在月份节点下查找日报节点（如："📅 日报 2026-03" 或 "3月20日 日报"）
   - 找到 → 复用 obj_token（文档token）
   - 未找到 → 创建新节点

5. 追加内容到文档
   feishu_doc --action append --doc_token <obj_token> --content <content>
```

### 知识库节点层级

#### 🤖 AI最新资讯（space_id: 7616519632920251572）
```
首页 (PhL6wlstzissQ1kKPwMc18xbngg)
├── 2026年 (Xhe3w81rqiNX0akqdCLc4LvYn2c) ← 当前使用
│   └── 3月 (DXDSw3upPinqWgkqN8XcXLCOnLh)
│       └── 📅 日报 2026-03 (UJidwZYcaio533kTngicrLy8ned)
│           ├── 2026-03-17 日报
│           ├── 第12期 - 3月19日
│           └── 3月20日 日报 ← 新内容追加到这里
├── 2026年 (XIgwwKRA4irDmIkyIdCcm6ELnqZ) ← 旧节点（避免使用）
└── 2026年 (ZdRUwc4y1iySQokS2R9cPVglnfh) ← 旧节点（避免使用）
```

#### 🎮 游戏开发（space_id: 7616735513310924004）
```
首页 (U9EWwwL8ui16IEkrN8vcIRISnFg)
└── [按年份-月份层级创建]
```

#### 🌱 健康生活（space_id: 7616737910330510558）
```
首页 (XD2PwwJukiD8a8koNAAc4Fedn5t)
└── [按年份-月份层级创建]
```

### 同步流程示例

**用户发送链接：https://b23.tv/xxx**

**步骤1：本地归档**
```bash
python skills/knowledge-base/scripts/archive_content.py \
  --url "https://b23.tv/xxx" \
  --title "AI视频标题"
```
输出同步信息：space_id, parent_token, content_entry 等

**步骤2：查询飞书节点**
```bash
feishu_wiki --action nodes \
  --space_id 7616519632920251572 \
  --parent_node_token PhL6wlstzissQ1kKPwMc18xbngg
```
查找 "2026年" 节点 → 复用 Xhe3w81rqiNX0akqdCLc4LvYn2c

**步骤3：逐级查找/创建**
- 在年份节点下找 "3月" → 复用 DXDSw3upPinqWgkqN8XcXLCOnLh
- 在月份节点下找 "📅 日报 2026-03" → 复用 UJidwZYcaio533kTngicrLy8ned
- 在日报节点下找 "3月20日 日报" → 复用 SQ25w4aUIijQj4kkQK1c8bapnMh

**步骤4：追加内容**
```bash
feishu_doc --action append \
  --doc_token DwjydeEopoT6bdxfUWHc18PnnTe \
  --content "### 📺 [标题](url)\n> 来源: Bilibili | 收集时间: 2026-03-20\n\n---\n"
```

### 注意事项

1. **不要依赖本地缓存** - 每次同步前先查询飞书获取最新状态
2. **同名节点处理** - 飞书允许多个同名节点，选择第一个匹配的即可
3. **层级结构** - 目前AI知识库使用 "📅 日报 YYYY-MM" 作为中间层级
4. **文档追加** - 使用 `append` 而不是 `write`，避免覆盖已有内容
5. **重复检测** - 追加前检查文档内容，避免重复添加相同链接

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

### 3️⃣ 统一内容归档（推荐）⭐
```bash
# 统一归档（自动识别微信/B站/通用链接）
python skills/knowledge-base/scripts/archive_content.py --url "..."

# 带标题
python skills/knowledge-base/scripts/archive_content.py --url "..." --title "标题"
```

**特点**：
- ✅ 自动识别链接类型（微信/B站/网页）
- ✅ 自动分类到 AI/游戏/健康 知识库
- ✅ 和日报同一层级存储（年/月/日）
- ✅ 自动去重

### 4️⃣ 单独归档（备用）
```bash
# 仅微信文章（自动分类）
python skills/knowledge-base/scripts/archive_wechat.py --url "https://mp.weixin.qq.com/s/..." --auto-classify

# 仅B站视频（自动分类）
python skills/knowledge-base/scripts/archive_bilibili.py --url "https://b23.tv/..." --auto-classify
```

**注意**：`archive_wechat.py` 和 `archive_bilibili.py` 已修复，现在可以独立运行，无需外部依赖。

### 5️⃣ 内容清理

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

| 脚本 | 功能 | 使用场景 | 状态 |
|------|------|----------|------|
| `daily_collect.py` | 收集最近2天内容 | 定时任务 | ✅ 正常 |
| `daily_push.py` | 推送日报到飞书 | 定时任务 | ✅ 正常 |
| `daily_pipeline.py` | 日报完整流程 | 定时任务 | ✅ 正常 |
| `weekly_collect.py` | 收集本周内容 | 周五定时 | ✅ 正常 |
| `weekly_push.py` | 推送周报到飞书 | 周六定时 | ✅ 正常 |
| `weekly_pipeline.py` | 周报完整流程 | 周五定时 | ✅ 正常 |
| `archive_content.py` | 统一归档（微信/B站/通用链接） | 收到任何链接时 | ✅ 正常 |
| `archive_wechat.py` | 微信文章归档 | 备用 | ✅ 已修复，独立运行 |
| `archive_bilibili.py` | B站视频归档 | 备用 | ✅ 已修复，独立运行 |
| `cleanup.py` | 清理过期内容 | 每天定时 | ✅ 正常 |
| `git_sync.py` | Git同步 | 每天定时 | ✅ 正常 |
| `check_status.py` | 查看任务状态 | 按需 | ✅ 正常 |
| `fetch_wechat.py` | 微信内容获取 | 内部调用 | ✅ 正常 |
| `fetch_bilibili.py` | B站内容获取 | 内部调用 | ✅ 正常 |

### 脚本使用说明

**`archive_content.py` - 链接归档核心脚本**

```bash
# 基本用法
python skills/knowledge-base/scripts/archive_content.py \
  --url "https://b23.tv/xxx" \
  --title "视频标题"
```

**输出字段说明：**
- `status`: success / skipped / error
- `kb`: 分类的知识库（ai-latest-news / game-development / healthy-living / link-collection）
- `file`: 本地存储路径
- `feishu_sync`: 飞书同步信息（仅在分类到知识库时返回）
  - `space_id`: 知识库空间ID
  - `parent_token`: 首页节点token
  - `year/month/day`: 日期信息
  - `doc_title`: 日报标题
  - `content_entry`: 要追加的内容

**重要：** 此脚本**不直接调用飞书API**，只负责本地归档和生成同步信息。飞书同步由 Agent 直接调用工具完成。

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
1. 执行 archive_content.py（本地归档）
   - 自动分类（AI/游戏/健康/其他）
   - 保存到 memory/kb-archive/{kb}/2026/03/20.md
   - 返回 feishu_sync 信息
    ↓
2. Agent 直接调用飞书工具（云端同步）
   - 查询飞书知识库现有节点
   - 找到则复用，未找到则创建
   - 追加内容到日报文档
    ↓
3. 反馈用户结果（本地 + 云端状态）
```

### 飞书同步详细步骤

**第一步：本地归档**
```bash
python skills/knowledge-base/scripts/archive_content.py \
  --url "https://b23.tv/xxx" \
  --title "视频标题"
```

**返回信息示例：**
```json
{
  "status": "success",
  "kb": "ai-latest-news",
  "feishu_sync": {
    "space_id": "7616519632920251572",
    "parent_token": "PhL6wlstzissQ1kKPwMc18xbngg",
    "kb_name": "🤖 AI最新资讯",
    "year": "2026",
    "month": "3",
    "day": "20",
    "doc_title": "3月20日 日报",
    "content_entry": "### 📺 [标题](url)\n> 来源: Bilibili | 收集时间: ...\n\n---\n"
  }
}
```

**第二步：查询飞书节点（逐级）**
```bash
# 1. 查询首页下的子节点
feishu_wiki --action nodes \
  --space_id 7616519632920251572 \
  --parent_node_token PhL6wlstzissQ1kKPwMc18xbngg

# 2. 在年份节点下查询
feishu_wiki --action nodes \
  --space_id 7616519632920251572 \
  --parent_node_token <year_node_token>

# 3. 在月份节点下查询
feishu_wiki --action nodes \
  --space_id 7616519632920251572 \
  --parent_node_token <month_node_token>

# 4. 在日报容器下查询
feishu_wiki --action nodes \
  --space_id 7616519632920251572 \
  --parent_node_token <daily_container_token>
```

**第三步：获取/创建节点**
- 如果找到匹配的节点 → 复用其 `node_token` 或 `obj_token`
- 如果未找到 → 创建新节点：
```bash
feishu_wiki --action create \
  --space_id 7616519632920251572 \
  --parent_node_token <parent_token> \
  --title "节点标题" \
  --obj_type docx
```

**第四步：追加内容**
```bash
feishu_doc --action append \
  --doc_token <obj_token> \
  --content "内容"
```

### 关键要点

1. **脚本只负责本地归档** - `archive_content.py` 不直接调用飞书API
2. **Agent 负责飞书同步** - 只有 Agent 能直接调用 `feishu_wiki` 和 `feishu_doc` 工具
3. **先查询后创建** - 每次同步前必须先查询飞书，避免重复创建节点

---

## 🔒 Git 自动提交规则

### 原则

**每次修改工作区内容后，必须自动提交到 Git**

### 执行时机

- ✅ 完成用户请求后（如：归档链接、更新文档）
- ✅ 后台任务（heartbeat/cron）结束时
- ✅ 任何文件改动完成后

### 提交脚本

```bash
#!/bin/bash
cd /workspace/projects/workspace
if [ -n "$(git status --porcelain)" ]; then
    git add -A
    git commit -m "auto: $(date '+%Y-%m-%d %H:%M') 自动提交"
    git push
fi
```

### 使用方式

**手动执行：**
```bash
sh /workspace/projects/workspace/scripts/auto-git-commit.sh
```

**Agent 自动执行：**
每次完成用户请求后，Agent 会自动检查并提交改动。

### 提交信息格式

```
auto: 2026-03-20 08:23 自动提交
```

或带描述：
```
auto: 2026-03-20 08:23 归档B站视频到AI知识库
```
3. **查询优先于创建** - 每次同步前必须先查询飞书，避免重复创建节点
4. **层级结构** - AI知识库使用特定的层级：首页 → 年份 → 月份 → 日报容器 → 具体日报
5. **追加而非覆盖** - 使用 `append` 操作向现有文档添加内容

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

## 🛠️ 维护记录

### 2026-03-19 脚本修复

**修复内容**：
- ✅ `archive_wechat.py` - 移除 `archive_manager` 依赖，现在可独立运行
- ✅ `archive_bilibili.py` - 移除 `archive_manager` 依赖，现在可独立运行
- ✅ 所有 14 个脚本均已验证，无外部依赖问题

**脚本状态**：
| 脚本 | 修复状态 |
|------|----------|
| `daily_collect.py` | ✅ 正常 |
| `daily_push.py` | ✅ 正常 |
| `daily_pipeline.py` | ✅ 正常 |
| `weekly_collect.py` | ✅ 正常 |
| `weekly_push.py` | ✅ 正常 |
| `weekly_pipeline.py` | ✅ 正常 |
| `archive_content.py` | ✅ 正常 |
| `archive_wechat.py` | ✅ 已修复 |
| `archive_bilibili.py` | ✅ 已修复 |
| `cleanup.py` | ✅ 正常 |
| `git_sync.py` | ✅ 正常 |
| `check_status.py` | ✅ 正常 |
| `fetch_wechat.py` | ✅ 正常 |
| `fetch_bilibili.py` | ✅ 正常 |

---

*统一知识库管理 - 一个 skill 管理所有内容收集*
