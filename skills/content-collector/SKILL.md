---
name: content-collector
description: |
  Unified content collection and archiving system for multiple knowledge bases.
  Supports AI Latest News, Game Development, and Healthy Living knowledge bases.
  Use when collecting, organizing, or syncing content to Feishu wiki.
  Triggers on phrases like "收集内容", "整理资讯", "同步知识库", "归档内容".
---

# Content Collector

统一的内容收集、分类、归档和同步系统，支持多个知识库的自动化管理。

## 支持的知识库

| 知识库 | 主题 | 分类模块 | space_id |
|--------|------|----------|----------|
| 🤖 **AI最新资讯** | AI/人工智能 | 📰资讯/🛠️工具/📚研究/💡案例 | 7616519632920251572 |
| 🎮 **游戏开发** | 游戏开发 | 🎮引擎/🎯设计/💻技术/🎨美术/🎵音频/🏆独游 | 7616735513310924004 |
| 🌱 **健康生活** | 健康/生活 | 🏃运动/🥗饮食/😊心理/💤睡眠/🏥医疗/✨妙招 | 7616737910330510558 |

---

## 核心工作流程

### 5步标准流程

```
收集 → 分类 → 归档 → 同步 → 记录
```

#### 步骤1：内容收集

搜索和发现各知识库相关内容：

```bash
# AI内容
npx ts-node skills/coze-web-search/scripts/search.ts \
  -q "OpenAI Anthropic Google AI latest" --time-range 1w --count 10

# 游戏内容
npx ts-node skills/coze-web-search/scripts/search.ts \
  -q "Unity Unreal game development" --time-range 1w --count 10

# 健康内容
npx ts-node skills/coze-web-search/scripts/search.ts \
  -q "健康 运动 饮食 生活妙招" --time-range 1w --count 10
```

#### 步骤2：内容分类

自动判断内容归属的知识库和模块：

```python
# 分类逻辑
def classify_content(url, title, content):
    # 1. 判断知识库
    if any(kw in text for kw in ['AI', '人工智能', 'GPT', 'Claude', 'LLM', '机器学习']):
        kb = 'ai-latest-news'
    elif any(kw in text for kw in ['Unity', 'Unreal', '游戏', 'game', '独立游戏']):
        kb = 'game-development'
    elif any(kw in text for kw in ['健康', '运动', '饮食', '心理', '生活']):
        kb = 'healthy-living'
    
    # 2. 判断模块（根据知识库）
    module = classify_module(kb, title, content)
    
    return kb, module, confidence
```

**分类规则对照表：**

| 知识库 | 模块 | 关键词 |
|--------|------|--------|
| 🤖 AI | 📰行业资讯 | 发布、融资、OpenAI、Anthropic、Google |
| 🤖 AI | 🛠️工具技巧 | 工具、教程、技巧、Prompt、How to |
| 🤖 AI | 📚深度研究 | 论文、原理、分析、架构、Transformer |
| 🤖 AI | 💡案例分享 | 实践、案例、经验、踩坑、总结 |
| 🎮 游戏 | 🎮游戏引擎 | Unity、Unreal、Godot、引擎、渲染 |
| 🎮 游戏 | 🎯游戏设计 | 设计、机制、玩法、关卡、平衡 |
| 🎮 游戏 | 💻开发技术 | 代码、算法、AI、物理、网络 |
| 🎮 游戏 | 🎨美术资源 | 美术、模型、动画、特效、Shader |
| 🎮 游戏 | 🎵音频音效 | 音效、音乐、配音、声音、FMOD |
| 🎮 游戏 | 🏆独立游戏 | indie、独立、发布、成功案例 |
| 🌱 健康 | 🏃运动健身 | 运动、健身、跑步、瑜伽、锻炼 |
| 🌱 健康 | 🥗饮食营养 | 饮食、营养、食谱、减肥、健康餐 |
| 🌱 健康 | 😊心理健康 | 心理、压力、情绪、冥想、焦虑 |
| 🌱 健康 | 💤睡眠健康 | 睡眠、失眠、作息、熬夜、助眠 |
| 🌱 健康 | 🏥医疗资讯 | 疾病、医疗、预防、检查、疫苗 |
| 🌱 健康 | ✨生活妙招 | 生活、窍门、技巧、妙招、清洁 |

#### 步骤3：本地归档

**存储结构（四层级）：**

```
memory/
├── ai-content/
│   ├── weekly/
│   │   └── weekly-YYYY-WXX.md          # 周刊文件
│   ├── daily/
│   │   └── ai-content-YYYY-MM-DD.md    # 日归档
│   └── modules/
│       ├── news/                        # 📰行业资讯
│       ├── tools/                       # 🛠️工具技巧
│       ├── research/                    # 📚深度研究
│       └── cases/                       # 💡案例分享
├── game-content/
│   ├── weekly/
│   │   └── game-weekly-YYYY-WXX.md
│   ├── daily/
│   │   └── game-content-YYYY-MM-DD.md
│   └── modules/
│       ├── engine/                      # 🎮游戏引擎
│       ├── design/                      # 🎯游戏设计
│       ├── tech/                        # 💻开发技术
│       ├── art/                         # 🎨美术资源
│       ├── audio/                       # 🎵音频音效
│       └── indie/                       # 🏆独立游戏
└── health-content/
    ├── weekly/
    │   └── health-weekly-YYYY-WXX.md
    ├── daily/
    │   └── health-content-YYYY-MM-DD.md
    └── modules/
        ├── fitness/                     # 🏃运动健身
        ├── diet/                        # 🥗饮食营养
        ├── mental/                      # 😊心理健康
        ├── sleep/                       # 💤睡眠健康
        ├── medical/                     # 🏥医疗资讯
        └── tips/                        # ✨生活妙招
```

**周刊格式标准：**

```markdown
# [知识库名称]周刊：第X期（YYYY年MM月DD日）

---

**本期编辑** | OpenClaw AI  
**出版日期** | YYYY年MM月DD日  
**总第X期**

---

## 📌 本周话题
（本期热点综述）

---

## [模块1名称]

### 1. [文章标题](URL)
内容摘要...
> 来源：[网站名](URL) · YYYY-MM-DD

### 2. [文章标题](URL)
...

---

## [模块2名称]
...

---

## 🔗 链接引用

| 序号 | 标题 | 来源 | 日期 |
|------|------|------|------|
| 1 | [标题](URL) | 网站名 | MM-DD |
| 2 | [标题](URL) | 网站名 | MM-DD |

---

*本期周刊由 OpenClaw AI 自动生成*
```

#### 步骤4：同步飞书知识库

**同步流程：**

```bash
# 1. 获取知识库列表
feishu_wiki --action spaces

# 2. 获取指定知识库的节点
feishu_wiki --action nodes --space_id <space_id>

# 3. 按层级创建/获取节点
# 3.1 创建年度节点（如不存在）
feishu_wiki --action create \
  --space_id <space_id> \
  --parent_node_token <首页_token> \
  --title "2026年" \
  --obj_type docx

# 3.2 创建月度节点
feishu_wiki --action create \
  --space_id <space_id> \
  --parent_node_token <年度_token> \
  --title "3月" \
  --obj_type docx

# 3.3 创建周刊节点
feishu_wiki --action create \
  --space_id <space_id> \
  --parent_node_token <月度_token> \
  --title "第11期 - 3月13日" \
  --obj_type docx

# 4. 写入周刊内容
feishu_doc --action write \
  --doc_token <obj_token> \
  --content "$(cat memory/xxx-content/weekly/xxx-weekly-YYYY-WXX.md)"
```

**飞书知识库层级结构：**

```
知识库首页
├── 📅 2026年
│   ├── 📅 1月
│   │   ├── 📅 第1-4期
│   │   └── 📄 第X期 - MM月DD日
│   ├── 📅 2月
│   │   └── 📄 ...
│   └── 📅 3月
│       ├── 📄 第11期 - 3月13日  ✅ 本期周刊
│       └── 📄 ...
├── 📅 2025年
└── 📚 模块索引
    ├── 📰 行业资讯索引
    ├── 🛠️ 工具技巧索引
    └── ...
```

#### 步骤5：更新操作日志

在 `memory/YYYY-MM-DD.md` 记录完整操作：

```markdown
## 内容收集与同步
时间：YYYY-MM-DD HH:MM

### 收集统计
| 知识库 | 收集数量 | 分类模块 |
|--------|----------|----------|
| 🤖 AI最新资讯 | 15条 | 资讯:8 / 工具:3 / 研究:2 / 案例:2 |
| 🎮 游戏开发 | 12条 | 引擎:3 / 设计:2 / 技术:4 / 美术:2 / 独游:1 |
| 🌱 健康生活 | 10条 | 运动:3 / 饮食:2 / 心理:2 / 妙招:3 |

### 同步状态
| 知识库 | 周刊期数 | Wiki节点 | 状态 |
|--------|----------|----------|------|
| 🤖 AI最新资讯 | 第11期 | `IcpqwuNF1iWG66krXBEckd5Gnyg` | ✅ 已同步 |
| 🎮 游戏开发 | 第11期 | `HclowsO6aiklATk86UVcDZEAnDg` | ✅ 已同步 |
| 🌱 健康生活 | 第11期 | `Ucaiwqi4AiYEnYkGtKrcBVUWnPe` | ✅ 已同步 |

### 本地备份
- `memory/ai-content/weekly/weekly-2026-W11.md`
- `memory/game-content/weekly/game-weekly-2026-W11.md`
- `memory/health-content/weekly/health-weekly-2026-W11.md`
```

---

## 使用方法

### 手动执行单知识库收集

```bash
# AI最新资讯
python skills/content-collector/scripts/collect.py \
  --kb ai-latest-news \
  --week current

# 游戏开发
python skills/content-collector/scripts/collect.py \
  --kb game-development \
  --week current

# 健康生活
python skills/content-collector/scripts/collect.py \
  --kb healthy-living \
  --week current
```

### 批量收集全部知识库

```bash
# 收集全部三个知识库的本周内容
python skills/content-collector/scripts/collect_all.py --week current

# 输出：
# ✅ AI最新资讯: 15条内容已归档
# ✅ 游戏开发: 12条内容已归档
# ✅ 健康生活: 10条内容已归档
```

### 同步到飞书知识库

```bash
# 同步指定知识库
python skills/content-collector/scripts/sync_feishu.py \
  --kb ai-latest-news \
  --week 2026-W11

# 同步全部知识库
python skills/content-collector/scripts/sync_feishu.py --all --week current
```

### 一键完成收集+同步

```bash
# 完整流程：收集 → 分类 → 归档 → 同步 → 记录
python skills/content-collector/scripts/full_pipeline.py --week current
```

---

## 自动化集成

### HEARTBEAT.md 配置

```markdown
### 周刊自动归档（每周五下午 6:00）
**步骤1: 内容收集**
- [ ] 运行统一收集脚本: `python skills/content-collector/scripts/collect_all.py --week current`
- [ ] 分别收集AI/游戏/健康三个知识库内容

**步骤2: 内容分类**
- [ ] 自动分类到各知识库的对应模块
- [ ] 按「年/月/周/日」层级归档到本地

**步骤3: 生成本地周刊**
- [ ] 生成三个周刊Markdown文件
- [ ] 格式：标题/本周话题/各模块/链接引用

**步骤4: 同步飞书知识库**
- [ ] 获取知识库节点: `feishu_wiki --action nodes --space_id <id>`
- [ ] 创建年度/月度/周刊层级节点
- [ ] 写入周刊内容: `feishu_doc --action write --doc_token <token>`

**步骤5: 更新操作日志**
- [ ] 在 `memory/YYYY-MM-DD.md` 记录同步操作
- [ ] 记录各知识库的Wiki节点Token
```

### Cron 定时任务

```bash
# 编辑 crontab
crontab -e

# 每周五下午6点执行完整收集和同步
0 18 * * 5 cd /workspace/projects/workspace && \
  python skills/content-collector/scripts/full_pipeline.py --week current
```

---

## 知识库空间ID对照表

| 知识库 | space_id | 当前首页节点 |
|--------|----------|--------------|
| 🤖 AI最新资讯 | 7616519632920251572 | `PhL6wlstzissQ1kKPwMc18xbngg` |
| 🎮 游戏开发 | 7616735513310924004 | `U9EWwwL8ui16IEkrN8vcIRISnFg` |
| 🌱 健康生活 | 7616737910330510558 | `XD2PwwJukiD8a8koNAAc4Fedn5t` |

---

## 注意事项

1. **内容分类** - 每篇文章必须明确归属一个知识库和一个模块
2. **链接引用** - 所有内容必须标注来源链接 `[标题](URL)`
3. **层级结构** - 飞书知识库按「年/月/周」三级嵌套
4. **本地备份** - 所有内容同步备份到本地 `memory/` 目录
5. **操作日志** - 每次同步必须在 `memory/YYYY-MM-DD.md` 记录
6. **医疗内容** - 健康生活知识库的医疗内容需添加免责声明

---

*统一内容收集器 - 支持多知识库自动化管理*

---

## 多 Agent 协作架构 (Beta)

除了传统的脚本方式，我们还提供了 **多 Agent 协作架构**，实现更高效的内容收集和处理。

### 架构设计

```
Coordinator (协调器)
    │
    ├── Collectors (收集器) - 3个并行
    │   ├── AI Collector 🤖
    │   ├── Game Collector 🎮
    │   └── Health Collector 🌱
    │
    ├── Processors (整理器) - N个并行
    │   ├── Classifier 📂
    │   ├── Quality Filter 🔍
    │   └── Summarizer 📝
    │
    ├── Publisher (推送器) - 1个
    │   └── 生成周刊 + 推送到飞书
    │
    ├── Syncer (同步器) - 1个
    │   └── 同步到 Git
    │
    └── Maintainer (维护器) - 1个
        └── 系统健康检查
```

### Agent 列表

| Agent | 类型 | 职责 | 命令 |
|-------|------|------|------|
| **Coordinator** | 协调器 | 任务分发、工作流编排 | `coordinator.py` |
| **AI Collector** | 收集器 | AI 内容收集 | `collectors/ai_collector.py` |
| **Game Collector** | 收集器 | 游戏内容收集 | `collectors/game_collector.py` |
| **Health Collector** | 收集器 | 健康内容收集 | `collectors/health_collector.py` |
| **Classifier** | 处理器 | 内容分类 | `processors/classifier.py` |
| **Quality Filter** | 处理器 | 质量筛选 | `processors/quality_filter.py` |
| **Publisher** | 推送器 | 生成周刊、推送飞书 | `publisher.py` |
| **Syncer** | 同步器 | Git 同步 | `syncer.py` |
| **Maintainer** | 维护器 | 系统维护 | `maintainer.py` |

### 使用方式

#### 1. 启动完整流程（Coordinator 自动分发）

```bash
# 启动 Coordinator，自动分发任务到各 Agent
python skills/content-collector/agents/coordinator.py \
  --task weekly_collection \
  --week current
```

执行流程：
1. Coordinator 启动 3 个 Collector Agents 并行收集
2. 等待收集完成后，启动 Processors 整理内容
3. 启动 Publisher 生成周刊
4. 启动 Syncer 同步到 Git

#### 2. 单独运行某个 Agent

```bash
# 单独收集 AI 内容
python skills/content-collector/agents/collectors/ai_collector.py --week current

# 单独分类内容
python skills/content-collector/agents/processors/classifier.py --week current

# 单独筛选质量
python skills/content-collector/agents/processors/quality_filter.py --week current

# 单独生成周刊
python skills/content-collector/agents/publisher.py --week current

# 单独同步到 Git
python skills/content-collector/agents/syncer.py

# 系统维护检查
python skills/content-collector/agents/maintainer.py --check all
```

#### 3. 用户添加内容（在原有基础上增加）

```bash
# 用户提供搜索内容文件，Coordinator 负责合并
python skills/content-collector/agents/coordinator.py \
  --task add_content \
  --kb ai-latest-news \
  --file user_search_results.md \
  --merge
```

### 用户搜索内容格式

当用户提供搜索内容时，请按以下格式提供：

```markdown
# 用户搜索内容 - AI最新资讯

## 📰 行业资讯

### 1. [文章标题](URL)
文章摘要/关键内容摘录...
> 来源：[网站名](URL) · 发布日期

### 2. [另一篇文章](URL)
...

## 🛠️ 工具技巧

### 1. [工具/教程标题](URL)
...
```

**支持的操作**:
- ✅ 在原有周刊基础上增加内容
- ✅ 补充遗漏的分类模块
- ✅ 更新已有文章的摘要

### 配置文件

Agent 配置位于 `agents/config.yaml`：

```yaml
agents:
  collectors:
    - id: collector-ai
      kb: ai-latest-news
      schedule: "0 18 * * 5"  # 每周五 18:00
    - id: collector-game
      kb: game-development
      schedule: "0 18 * * 5"
    - id: collector-health
      kb: healthy-living
      schedule: "0 18 * * 5"
  
  processors:
    - id: classifier
      parallel: true
    - id: quality
      parallel: true
  
  publisher:
    single_instance: true
  
  syncer:
    single_instance: true
  
  maintainer:
    schedule: "0 */4 * * *"  # 每4小时检查
```

### 架构文档

详细架构设计请参考：
- `agents/ARCHITECTURE.md` - 完整架构文档
