# HEARTBEAT.md - 定期检查任务

> 心跳每4小时运行一次，检查以下内容

---

## 📋 检查清单

### 1. 记忆维护（每周一次）
- [ ] 回顾本周 memory/YYYY-MM-DD.md 文件
- [ ] 将重要事件、决策更新到 MEMORY.md
- [ ] 清理过时的记忆内容

### 2. 项目状态检查（每天）
- [ ] 检查 workspace git 状态
- [ ] 查看是否有未提交的更改
- [ ] 确保重要文件已备份
- [ ] 更新 Token 使用统计：`node scripts/track-usage.js`
- [ ] 运行 `node scripts/usage.js` 并显示 Token 统计摘要

### 3. 系统健康检查（每次）
- [ ] OpenClaw 网关状态
- [ ] 飞书渠道连接状态
- [ ] 磁盘空间使用情况

### 4. 周刊自动归档（每周五下午 6:00 - 统一收集流程）

**使用统一内容收集器：** `skills/content-collector/`

#### 步骤1: 内容收集（全知识库）
- [ ] 运行统一收集脚本:
  ```bash
  python skills/content-collector/scripts/collect_all.py --week current
  ```
- [ ] 分别收集三个知识库内容：
  - 🤖 AI最新资讯 → `memory/ai-content/weekly/weekly-YYYY-WXX.md`
  - 🎮 游戏开发 → `memory/game-content/weekly/game-weekly-YYYY-WXX.md`
  - 🌱 健康生活 → `memory/health-content/weekly/health-weekly-YYYY-WXX.md`

#### 步骤2: 内容分类
- [ ] **AI最新资讯** - 分类到四模块：
  - 📰 行业资讯（新闻、产品发布、融资）
  - 🛠️ 工具技巧（工具推荐、教程）
  - 📚 深度研究（论文、原理分析）
  - 💡 案例分享（实战经验、案例）
- [ ] **游戏开发** - 分类到六模块：
  - 🎮 游戏引擎（Unity、Unreal、Godot）
  - 🎯 游戏设计（设计理念、机制）
  - 💻 开发技术（编程、图形、AI）
  - 🎨 美术资源（美术工具、素材）
  - 🎵 音频音效（音频工具、音乐）
  - 🏆 独立游戏（独立游戏发布、案例）
- [ ] **健康生活** - 分类到六模块：
  - 🏃 运动健身（锻炼方法、健身计划）
  - 🥗 饮食营养（健康饮食、食谱）
  - 😊 心理健康（压力管理、情绪调节）
  - 💤 睡眠健康（睡眠质量、作息）
  - 🏥 医疗资讯（疾病预防、健康检查）
  - ✨ 生活妙招（生活技巧、小窍门）

#### 步骤3: 本地归档
- [ ] 按「年/月/周/日」四级层级归档到本地
  ```
  memory/
  ├── ai-content/weekly/weekly-YYYY-WXX.md
  ├── game-content/weekly/game-weekly-YYYY-WXX.md
  └── health-content/weekly/health-weekly-YYYY-WXX.md
  ```
- [ ] 生成周刊格式：封面/本周话题/各模块/链接引用

#### 步骤4: 同步飞书知识库（分层级嵌套）

**知识库空间ID对照表：**
| 知识库 | space_id | 首页节点 |
|--------|----------|----------|
| 🤖 AI最新资讯 | 7616519632920251572 | PhL6wlstzissQ1kKPwMc18xbngg |
| 🎮 游戏开发 | 7616735513310924004 | U9EWwwL8ui16IEkrN8vcIRISnFg |
| 🌱 健康生活 | 7616737910330510558 | XD2PwwJukiD8a8koNAAc4Fedn5t |

**同步流程（每个知识库）：**
```bash
# 4.1 获取知识库节点
feishu_wiki --action nodes --space_id <space_id>

# 4.2 创建年度节点（如不存在）
feishu_wiki --action create \
  --space_id <space_id> \
  --parent_node_token <首页_token> \
  --title "2026年" \
  --obj_type docx

# 4.3 创建月度节点
feishu_wiki --action create \
  --space_id <space_id> \
  --parent_node_token <年度_token> \
  --title "3月" \
  --obj_type docx

# 4.4 创建周刊文档
feishu_wiki --action create \
  --space_id <space_id> \
  --parent_node_token <月度_token> \
  --title "第X期 - MM月DD日" \
  --obj_type docx

# 4.5 写入周刊内容
feishu_doc --action write \
  --doc_token <obj_token> \
  --content "$(cat memory/xxx-content/weekly/xxx-weekly-YYYY-WXX.md)"
```

**飞书知识库层级结构：**
```
知识库首页
├── 📅 2026年
│   ├── 📅 3月
│   │   ├── 📄 第11期 - 3月13日  ✅ 本期周刊
│   │   └── 📄 ...
│   └── 📅 4月
└── 📅 2025年
```

#### 步骤5: 质量筛选（各知识库特殊规则）
- [ ] **AI最新资讯** - 过滤低质量来源（置信度<40%），标记高价值内容（>80%）
- [ ] **游戏开发** - 标记高价值内容（引擎更新/重大发布/实用教程）
- [ ] **健康生活** - 优先权威来源（丁香医生、三甲医院），医疗内容添加免责声明

#### 步骤6: 生成周报摘要
- [ ] 汇总三个知识库的本周精选内容
- [ ] AI资讯 Top 5 + 游戏开发 Top 3 + 健康生活 Top 3
- [ ] 生成综合周报并准备推送

#### 步骤7: 更新操作日志
- [ ] 在 `memory/YYYY-MM-DD.md` 记录完整操作：
  ```markdown
  ## 内容收集与同步
  时间：YYYY-MM-DD HH:MM
  
  ### 收集统计
  | 知识库 | 数量 | 分类分布 |
  |--------|------|----------|
  | 🤖 AI | 15条 | 资讯:8 / 工具:3 / 研究:2 / 案例:2 |
  | 🎮 游戏 | 12条 | 引擎:3 / 技术:4 / 设计:2 / 美术:2 / 独游:1 |
  | 🌱 健康 | 10条 | 运动:3 / 妙招:3 / 饮食:2 / 心理:2 |
  
  ### 同步状态
  | 知识库 | 周刊期数 | Wiki节点 | 状态 |
  |--------|----------|----------|------|
  | 🤖 AI | 第11期 | `xxx...` | ✅ 已同步 |
  | 🎮 游戏 | 第11期 | `xxx...` | ✅ 已同步 |
  | 🌱 健康 | 第11期 | `xxx...` | ✅ 已同步 |
  ```

### 5. 知识库日报推送（每天早上 8:00）
**步骤1: 检查更新**
- [ ] 检查三个知识库是否有新内容
- [ ] 统计各知识库新增文章数

**步骤2: 生成推送内容**
- [ ] 生成文本摘要（今日新增X篇，重点推荐Y篇）
- [ ] 生成飞书卡片（带跳转链接）
- [ ] 标注高优先级内容（🔥热点/⭐推荐）

**步骤3: 发送推送**
- [ ] 发送知识库更新通知
- [ ] 附带各知识库跳转链接
- [ ] 记录推送日志

**静默规则**: 23:00-08:00不推送，除非紧急重要内容

### 6. 周刊精选推送（每周六早上 9:00）
- [ ] 汇总三个知识库本周Top精选：
  - 🤖 AI资讯 Top 5
  - 🎮 游戏开发 Top 3
  - 🌱 健康生活 Top 3
- [ ] 生成综合周报并推送
- [ ] 附带完整周刊链接

### 7. 内容质量复盘（每周日晚上）
- [ ] 回顾本周自动分类准确率
- [ ] 统计各知识库内容数量和质量
- [ ] 记录需要人工干预的案例
- [ ] 优化分类关键词和规则

### 8. 通用链接归档（按需执行）
- [ ] 自动分类链接: `python skills/link-collector/scripts/universal_archive.py --url "..."`
- [ ] 支持自动判断知识库+模块
- [ ] 分类规则：
  - AI/ML → 🤖 AI最新资讯
  - 游戏开发 → 🎮 游戏开发
  - 健康/生活 → 🌱 健康生活
  - 其他技术 → 🔗 本地链接收藏

### 9. Skills 维护（每周日）
- [ ] 检查各 skill 的更新情况（查看官方源、GitHub 等）
- [ ] 如有更新，更新 skill 版本和功能
- [ ] 更新 skill 文档和来源配置
- [ ] 测试更新后的功能是否正常

### 10. OpenClaw 更新检查（每周日）
- [ ] 运行 `python skills/openclaw-updater/scripts/check_updates.py`
- [ ] 查看最新 GitHub releases
- [ ] 检查官方文档变更
- [ ] 如有更新，评估并执行更新
- [ ] 记录更新日志到 `memory/openclaw-updates.json`

---

## 🔔 提醒规则

**静默时段：** 23:00 - 08:00（除非紧急情况）

**触发通知的条件：**
- 发现重要未读消息
- 日历事件即将发生（< 2小时）
- 系统出现异常
- 超过8小时未联系

**保持静默的情况：**
- 刚检查过（< 30分钟）
- 无明显异常
- 用户明显忙碌中

---

## 📝 记录格式

每次检查后更新 `memory/heartbeat-state.json`：

```json
{
  "lastChecks": {
    "memory": "2026-03-11T23:00:00Z",
    "git": "2026-03-11T20:00:00Z",
    "system": "2026-03-11T23:00:00Z",
    "token": "2026-03-11T23:00:00Z",
    "content_collection": "2026-03-14T10:00:00Z"
  }
}
```

---

## 🔄 内容收集器快速参考

### 统一内容收集器

**Skill 位置**: `skills/content-collector/`

**核心脚本**:
```bash
# 收集全部知识库
python skills/content-collector/scripts/collect_all.py --week current

# 收集指定知识库
python skills/content-collector/scripts/collect.py --kb ai-latest-news --week current
python skills/content-collector/scripts/collect.py --kb game-development --week current
python skills/content-collector/scripts/collect.py --kb healthy-living --week current

# 同步到飞书
python skills/content-collector/scripts/sync_feishu.py --all --week current

# 完整流程：收集+分类+归档+同步
python skills/content-collector/scripts/full_pipeline.py --week current
```

### 知识库分类规则

| 知识库 | 模块数 | 核心关键词 |
|--------|--------|------------|
| 🤖 AI最新资讯 | 4 | AI、GPT、Claude、LLM、机器学习、OpenAI |
| 🎮 游戏开发 | 6 | Unity、Unreal、游戏、game、indie、引擎 |
| 🌱 健康生活 | 6 | 健康、运动、饮食、心理、生活、健身 |

### 本地存储结构

```
memory/
├── ai-content/
│   ├── weekly/weekly-YYYY-WXX.md
│   ├── daily/ai-content-YYYY-MM-DD.md
│   └── modules/{news,tools,research,cases}/
├── game-content/
│   ├── weekly/game-weekly-YYYY-WXX.md
│   ├── daily/game-content-YYYY-MM-DD.md
│   └── modules/{engine,design,tech,art,audio,indie}/
└── health-content/
    ├── weekly/health-weekly-YYYY-WXX.md
    ├── daily/health-content-YYYY-MM-DD.md
    └── modules/{fitness,diet,mental,sleep,medical,tips}/
```

### 飞书同步命令

```bash
# 查看知识库
feishu_wiki --action spaces

# 查看节点
feishu_wiki --action nodes --space_id 7616519632920251572

# 创建文档
feishu_wiki --action create \
  --space_id <space_id> \
  --parent_node_token <parent> \
  --title "第X期 - MM月DD日"

# 写入内容
feishu_doc --action write \
  --doc_token <obj_token> \
  --content "# 标题..."
```

### 同步记录模板

在 `memory/YYYY-MM-DD.md` 中记录：

```markdown
## 内容收集与同步
时间：YYYY-MM-DD HH:MM

### 收集统计
| 知识库 | 数量 | 分类分布 |
|--------|------|----------|
| 🤖 AI | XX条 | 资讯:X / 工具:X / 研究:X / 案例:X |
| 🎮 游戏 | XX条 | 引擎:X / 设计:X / 技术:X / 美术:X / 音频:X / 独游:X |
| 🌱 健康 | XX条 | 运动:X / 饮食:X / 心理:X / 睡眠:X / 医疗:X / 妙招:X |

### 同步状态
| 知识库 | 周刊期数 | Wiki节点 | 状态 |
|--------|----------|----------|------|
| 🤖 AI | 第X期 | `node_token` | ✅ 已同步 |
| 🎮 游戏 | 第X期 | `node_token` | ✅ 已同步 |
| 🌱 健康 | 第X期 | `node_token` | ✅ 已同步 |

### 本地备份
- `memory/ai-content/weekly/weekly-YYYY-WXX.md`
- `memory/game-content/weekly/game-weekly-YYYY-WXX.md`
- `memory/health-content/weekly/health-weekly-YYYY-WXX.md`
```

---

*最后更新：2026-03-14*
*统一内容收集器版本：v1.0*
