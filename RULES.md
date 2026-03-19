# 工作区统一规则与架构文档

> 本文档是工作区的**唯一权威规则源**，所有脚本、skills、任务必须遵循此文档。
> 最后更新：2026-03-19

---

## 📋 核心规则

### 规则1：日报收集范围（只收集前两天）

**定义**：日报只收集**最近2天**发布的内容，避免重复收集历史内容。

**具体逻辑**：
- 收集目标日期：今天和昨天（共2天）
- 搜索时间范围：`published_after: 2_days_ago`
- 去重机制：已收集的 URL 不再重复收集
- 存储标记：每个链接记录 `first_collected_date`

**实现**：
```python
# 只收集最近2天的内容
collect_days = 2  # 可配置
search_time_range = f"{collect_days}d"  # 2天内发布的内容
```

---

### 规则2：内容保留策略

| 内容类型 | 保留时间 | 自动清理 | 位置 |
|----------|----------|----------|------|
| **日报内容** | 最近 **7天** | ✅ 每天收集后自动清理 | `memory/*/daily/` |
| **周报内容** | 最近 **30天**（约1个月） | ✅ 每周收集后清理 | `memory/*/weekly/` |
| **模块归档** | 最近 **90天**（约3个月） | ✅ 每月清理 | `memory/*/modules/` |
| **飞书知识库** | **永久** | ❌ 不清理 | 飞书云端 |
| **链接收藏** | **永久** | ❌ 不清理 | `memory/link-collection/` |

**清理逻辑**：
- 每天收集完成后，自动删除超过保留期限的文件
- 保留空目录：`false`（清理时删除空文件夹）
- 清理前备份：可选（默认不备份）

---

### 规则3：知识库层级结构（统一标准）

**飞书知识库层级**：
```
知识库首页
├── 📅 2026年
│   ├── 📅 3月
│   │   ├── 📄 3月17日 日报        ← 日报
│   │   ├── 📄 3月18日 日报        ← 日报
│   │   ├── 📄 3月19日 日报        ← 日报
│   │   ├── 📄 第12期 - 03.17-03.23 周报  ← 周报（与日报同层级）
│   │   └── 📄 ...
│   └── 📅 4月
└── 📅 2025年
```

**本地存储层级**：
```
memory/
├── kb-archive/                    # 知识库内容（按年月）
│   ├── ai-latest-news/
│   │   └── 2026/
│   │       └── 03/
│   │           ├── 03-17.md       # 日报
│   │           ├── 03-18.md       # 日报
│   │           ├── 03-19.md       # 日报
│   │           └── week-12.md     # 周报（与日报同目录）
│   ├── game-development/
│   └── healthy-living/
│
└── link-collection/               # 链接收藏（永久保留）
    └── 2026/
        └── 03/
            └── 2026-03-19.md
```

**关键原则**：
- ✅ 日报和周报在同一「年/月」层级下
- ❌ 不单独为周报创建「周」文件夹
- ✅ 日报命名：`MM月DD日 日报`
- ✅ 周报命名：`第X期 - MM.DD-MM.DD 周报`

---

### 规则4：内容分类规则

#### 🤖 AI最新资讯（4模块）
| 模块 | 关键词 | 说明 |
|------|--------|------|
| 📰 行业资讯 | 发布、融资、OpenAI、Anthropic、Google、新闻 | 行业动态、产品发布 |
| 🛠️ 工具技巧 | 工具、教程、技巧、Prompt、How to | 实用工具、教程 |
| 📚 深度研究 | 论文、原理、分析、架构、Transformer | 技术深度内容 |
| 💡 案例分享 | 实践、案例、经验、踩坑、总结 | 实战经验 |

#### 🎮 游戏开发（6模块）
| 模块 | 关键词 | 说明 |
|------|--------|------|
| 🎮 游戏引擎 | Unity、Unreal、Godot、引擎、渲染 | 引擎技术 |
| 🎯 游戏设计 | 设计、机制、玩法、关卡、平衡 | 设计理念 |
| 💻 开发技术 | 代码、算法、AI、物理、网络 | 编程技术 |
| 🎨 美术资源 | 美术、模型、动画、特效、Shader | 美术制作 |
| 🎵 音频音效 | 音效、音乐、配音、声音、FMOD | 音频技术 |
| 🏆 独立游戏 | indie、独立、发布、成功案例 | 独立游戏 |

#### 🌱 健康生活（6模块）
| 模块 | 关键词 | 说明 |
|------|--------|------|
| 🏃 运动健身 | 运动、健身、跑步、瑜伽、锻炼 | 健身方法 |
| 🥗 饮食营养 | 饮食、营养、食谱、减肥、健康餐 | 健康饮食 |
| 😊 心理健康 | 心理、压力、情绪、冥想、焦虑 | 心理健康 |
| 💤 睡眠健康 | 睡眠、失眠、作息、熬夜、助眠 | 睡眠质量 |
| 🏥 医疗资讯 | 疾病、医疗、预防、检查、疫苗 | 医疗信息 |
| ✨ 生活妙招 | 生活、窍门、技巧、妙招、清洁 | 生活技巧 |

---

### 规则5：自动化任务调度

| 任务 | 频率 | 执行时间 | 脚本位置 |
|------|------|----------|----------|
| **日报收集** | 每天 | 08:00 | `skills/knowledge-base/scripts/daily_collect.py` |
| **日报推送** | 每天 | 08:30 | `skills/knowledge-base/scripts/daily_push.py` |
| **周报收集** | 每周 | 周五 18:00 | `skills/knowledge-base/scripts/weekly_collect.py` |
| **周报推送** | 每周 | 周六 09:00 | `skills/knowledge-base/scripts/weekly_push.py` |
| **Git同步** | 每天 | 22:00 | `skills/knowledge-base/scripts/git_sync.py` |
| **内容清理** | 每天 | 23:00 | `skills/knowledge-base/scripts/cleanup.py` |
| **Heartbeat** | 每4小时 | - | `HEARTBEAT.md` |

**静默时段**：23:00 - 08:00（不推送非紧急消息）

---

### 规则6：Skills 管理规范

**有效 Skills**（已整理，可使用）：
| Skill | 路径 | 状态 | 用途 |
|-------|------|------|------|
| **knowledge-base** | `skills/knowledge-base/` | ✅ 活跃 | 统一知识库管理（日报/周报/推送） |
| **link-collector** | `skills/link-collector/` | ✅ 活跃 | 链接收集和分类 |
| **coze-web-search** | `skills/coze-web-search/` | ✅ 活跃 | 网络搜索 |
| **coze-web-fetch** | `skills/coze-web-fetch/` | ✅ 活跃 | 网页内容提取 |
| **openclaw-updater** | `skills/openclaw-updater/` | ✅ 活跃 | OpenClaw更新检查 |
| **skill-creator** | `skills/skill-creator/` | ✅ 活跃 | 创建新skills |
| **skill-hub** | `skills/skill-hub/` | ✅ 活跃 | Skill管理 |

**已废弃 Skills**（请勿使用，保留用于参考）：
| Skill | 路径 | 状态 | 说明 |
|-------|------|------|------|
| ~~content-collector~~ | `skills/content-collector/` | ❌ 废弃 | 功能合并到 knowledge-base |
| ~~ai-content-collector~~ | `skills/ai-content-collector/` | ❌ 废弃 | 功能合并到 knowledge-base |
| ~~game-content-collector~~ | `skills/game-content-collector/` | ❌ 废弃 | 功能合并到 knowledge-base |
| ~~health-content-collector~~ | `skills/health-content-collector/` | ❌ 废弃 | 功能合并到 knowledge-base |
| ~~task-automation~~ | `skills/task-automation/` | ❌ 废弃 | 功能合并到 knowledge-base |

---

### 规则7：脚本管理规范

**有效脚本位置**：`skills/knowledge-base/scripts/`

| 脚本 | 功能 | 调用方式 |
|------|------|----------|
| `daily_collect.py` | 收集最近2天内容 | `python skills/knowledge-base/scripts/daily_collect.py` |
| `daily_push.py` | 推送日报到飞书 | `python skills/knowledge-base/scripts/daily_push.py` |
| `weekly_collect.py` | 收集本周内容 | `python skills/knowledge-base/scripts/weekly_collect.py` |
| `weekly_push.py` | 推送周报到飞书 | `python skills/knowledge-base/scripts/weekly_push.py` |
| `cleanup.py` | 清理过期内容 | `python skills/knowledge-base/scripts/cleanup.py` |
| `git_sync.py` | Git同步 | `python skills/knowledge-base/scripts/git_sync.py` |

**已废弃脚本位置**：`scripts/`（根目录）
- 这些脚本是旧的实现，已废弃
- 保留作为参考，但不再维护
- 新功能请使用 `skills/knowledge-base/scripts/` 下的脚本

---

### 规则8：配置文件管理

**有效配置文件**：
| 文件 | 用途 | 位置 |
|------|------|------|
| `content_sources.yaml` | 内容来源配置 | `config/content_sources.yaml` |
| `retention_policy.yaml` | 保留策略配置 | `config/retention_policy.yaml` |
| `kb_rules.yaml` | 知识库规则配置 | `config/kb_rules.yaml` |

**配置优先级**：
1. 环境变量（最高优先级）
2. 配置文件
3. 代码默认值（最低优先级）

---

### 规则9：日志和状态管理

**日志位置**：`memory/logs/`
```
memory/logs/
├── daily/
│   └── 2026-03-19.log
├── weekly/
│   └── 2026-W12.log
└── sync/
    └── 2026-03-19.log
```

**状态文件**：`memory/state/`
```
memory/state/
├── daily-state.json       # 日报状态
├── weekly-state.json      # 周报状态
├── collected-urls.json    # 已收集URL（去重用）
└── feishu-nodes.json      # 飞书节点缓存
```

**已收集URL记录格式**：
```json
{
  "urls": {
    "https://example.com/article": {
      "first_collected": "2026-03-19T08:00:00Z",
      "last_seen": "2026-03-19T08:00:00Z",
      "kb": "ai-latest-news",
      "title": "文章标题"
    }
  }
}
```

---

### 规则10：飞书知识库操作规范

**空间ID对照表**：
| 知识库 | space_id | 首页节点 |
|--------|----------|----------|
| 🤖 AI最新资讯 | 7616519632920251572 | `PhL6wlstzissQ1kKPwMc18xbngg` |
| 🎮 游戏开发 | 7616735513310924004 | `U9EWwwL8ui16IEkrN8vcIRISnFg` |
| 🌱 健康生活 | 7616737910330510558 | `XD2PwwJukiD8a8koNAAc4Fedn5t` |

**操作命令**：
```bash
# 查看知识库
feishu_wiki --action spaces

# 查看节点
feishu_wiki --action nodes --space_id <space_id>

# 创建节点
feishu_wiki --action create \
  --space_id <space_id> \
  --parent_node_token <parent> \
  --title "节点标题" \
  --obj_type docx

# 写入文档
feishu_doc --action write \
  --doc_token <obj_token> \
  --content "文档内容"
```

---

## 🔧 快速参考

### 执行日报收集
```bash
python skills/knowledge-base/scripts/daily_collect.py
```

### 执行周报收集
```bash
python skills/knowledge-base/scripts/weekly_collect.py
```

### 手动推送日报
```bash
python skills/knowledge-base/scripts/daily_push.py
```

### 清理过期内容
```bash
python skills/knowledge-base/scripts/cleanup.py
```

### 查看任务状态
```bash
python skills/knowledge-base/scripts/check_status.py
```

---

## 📝 更新记录

| 日期 | 更新内容 |
|------|----------|
| 2026-03-19 | 创建统一规则文档，整合所有分散的规则 |
| 2026-03-19 | 废弃旧 skills（content-collector, task-automation 等） |
| 2026-03-19 | 统一脚本位置到 `skills/knowledge-base/scripts/` |
| 2026-03-19 | 明确"只收集前两天"规则 |

---

**注意**：此文档为唯一权威规则源，所有脚本和任务必须遵循。如有冲突，以此文档为准。
