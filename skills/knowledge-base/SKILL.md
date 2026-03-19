---
name: knowledge-base
description: |
  统一的知识库管理系统，整合日报、周报、推送、清理等全部功能。
  遵循 WORKSPACE/RULES.md 中的统一规则。
  
  核心规则：
  1. 日报只收集最近2天的内容
  2. 日报保留7天，周报保留30天
  3. 飞书层级：年/月/日报+周报（同层级）
  4. 三个知识库：AI最新资讯、游戏开发、健康生活
  
  Triggers: "收集日报", "收集周报", "推送知识库", "清理内容"
---

# Knowledge Base - 统一知识库管理

工作区的**唯一**知识库管理 skill，整合所有内容收集、分类、推送、清理功能。

## 📋 核心规则（来自 RULES.md）

### 规则1：日报收集范围
- **只收集最近2天**发布的内容
- 搜索时间范围：`published_after: 2_days_ago`
- 已收集的 URL 不再重复收集

### 规则2：保留策略
| 内容类型 | 保留时间 | 自动清理 |
|----------|----------|----------|
| 日报 | 7天 | ✅ |
| 周报 | 30天 | ✅ |
| 模块归档 | 90天 | ✅ |
| 飞书知识库 | 永久 | ❌ |

### 规则3：飞书层级结构
```
2026年 → 3月 → 3月17日 日报
              → 3月18日 日报
              → 第12期 - 03.17-03.23 周报
```
- 日报和周报在同一「年/月」层级
- 不单独创建「周」文件夹

---

## 🚀 快速使用

### 收集日报（最近2天）
```bash
python skills/knowledge-base/scripts/daily_collect.py
```

### 推送日报到飞书
```bash
python skills/knowledge-base/scripts/daily_push.py
```

### 收集周报
```bash
python skills/knowledge-base/scripts/weekly_collect.py
```

### 推送周报到飞书
```bash
python skills/knowledge-base/scripts/weekly_push.py
```

### 一键完成日报全流程
```bash
python skills/knowledge-base/scripts/daily_pipeline.py
```

### 一键完成周报全流程
```bash
python skills/knowledge-base/scripts/weekly_pipeline.py
```

---

## 📁 脚本列表

| 脚本 | 功能 | 执行频率 |
|------|------|----------|
| `daily_collect.py` | 收集最近2天内容 | 每天 08:00 |
| `daily_push.py` | 推送日报到飞书 | 每天 08:30 |
| `daily_pipeline.py` | 日报完整流程 | 每天 08:00 |
| `weekly_collect.py` | 收集本周内容 | 周五 18:00 |
| `weekly_push.py` | 推送周报到飞书 | 周六 09:00 |
| `weekly_pipeline.py` | 周报完整流程 | 周五 18:00 |
| `cleanup.py` | 清理过期内容 | 每天 23:00 |
| `git_sync.py` | Git同步 | 每天 22:00 |
| `check_status.py` | 查看任务状态 | 按需 |

---

## 📊 知识库配置

### 三个知识库

| 知识库 | 空间ID | 模块数 | 模块列表 |
|--------|--------|--------|----------|
| 🤖 AI最新资讯 | 7616519632920251572 | 4 | 行业资讯、工具技巧、深度研究、案例分享 |
| 🎮 游戏开发 | 7616735513310924004 | 6 | 游戏引擎、游戏设计、开发技术、美术资源、音频音效、独立游戏 |
| 🌱 健康生活 | 7616737910330510558 | 6 | 运动健身、饮食营养、心理健康、睡眠健康、医疗资讯、生活妙招 |

### 分类关键词

详见 `config/kb_rules.yaml`

---

## 🗂️ 存储结构

### 本地存储
```
memory/
├── kb-archive/                    # 知识库内容
│   ├── ai-latest-news/
│   │   └── 2026/
│   │       └── 03/
│   │           ├── 03-17.md       # 日报
│   │           ├── 03-18.md       # 日报
│   │           └── week-12.md     # 周报
│   ├── game-development/
│   └── healthy-living/
│
├── logs/                          # 日志
│   ├── daily/
│   └── weekly/
│
└── state/                         # 状态
    ├── collected-urls.json        # 已收集URL
    └── task-state.json            # 任务状态
```

### 飞书存储
```
知识库首页
├── 📅 2026年
│   ├── 📅 3月
│   │   ├── 📄 3月17日 日报
│   │   ├── 📄 3月18日 日报
│   │   └── 📄 第12期 - 03.17-03.23 周报
```

---

## ⚙️ 配置

### 配置文件

| 文件 | 位置 | 说明 |
|------|------|------|
| 内容来源 | `config/content_sources.yaml` | 搜索关键词和来源 |
| 保留策略 | `config/retention_policy.yaml` | 清理规则 |
| 分类规则 | `config/kb_rules.yaml` | 模块分类关键词 |

### 环境变量

```bash
# 可选：覆盖默认配置
export KB_COLLECT_DAYS=2          # 收集天数
export KB_DAILY_RETENTION=7       # 日报保留天数
export KB_WEEKLY_RETENTION=30     # 周报保留天数
```

---

## 🔄 自动化任务

### 调度配置（Crontab）

```bash
# 编辑 crontab
crontab -e

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
- 同步日志：`memory/logs/sync/YYYY-MM-DD.log`

### 查看状态
```bash
# 查看任务执行状态
python skills/knowledge-base/scripts/check_status.py

# 查看最近日志
tail -f memory/logs/daily/$(date +%Y-%m-%d).log
```

---

## 🔗 相关文档

- **统一规则**：`WORKSPACE/RULES.md`
- **心跳任务**：`WORKSPACE/HEARTBEAT.md`
- **内容来源**：`config/content_sources.yaml`
- **保留策略**：`config/retention_policy.yaml`

---

*统一知识库管理 - 一个 skill 管理所有知识库内容*
