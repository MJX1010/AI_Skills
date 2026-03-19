# 工作区全面整理记录

时间：2026-03-19 08:30

## 问题诊断

### 发现的问题
1. **脚本重复**：`scripts/` 目录下有旧脚本，与 `skills/` 下的新脚本重复
2. **规则分散**：规则分散在 HEARTBEAT.md、各 SKILL.md、config/ 目录中
3. **逻辑不一致**：日报收集逻辑不统一，没有明确的"只收集前两天"规则
4. **层级混乱**：飞书知识库层级结构有多个版本，日报和周报位置不统一

---

## 整理方案

### 1. 创建统一规则文档 RULES.md
位置：`/workspace/projects/workspace/RULES.md`

**核心规则**：
- 规则1：日报只收集最近2天的内容
- 规则2：日报保留7天，周报保留30天
- 规则3：飞书层级统一为 年/月/日报+周报（同层级）
- 规则4：统一的内容分类规则
- 规则5-10：任务调度、Skills管理、脚本管理、配置管理、日志管理、飞书操作规范

### 2. 创建统一 knowledge-base skill
位置：`skills/knowledge-base/`

**整合的功能**：
- 日报收集（最近2天）
- 日报推送到飞书
- 周报收集
- 周报推送到飞书
- 内容清理
- Git同步
- 状态检查

**脚本列表**：
| 脚本 | 功能 |
|------|------|
| `daily_collect.py` | 收集最近2天内容，自动去重 |
| `daily_push.py` | 推送日报到飞书知识库和对话 |
| `daily_pipeline.py` | 日报完整流程（收集+推送） |
| `weekly_collect.py` | 收集本周所有日报汇总成周报 |
| `weekly_push.py` | 推送周报到飞书 |
| `cleanup.py` | 清理过期内容（日报7天/周报30天） |
| `check_status.py` | 查看任务执行状态 |

### 3. 废弃旧 skills 和脚本

**废弃的 skills**（保留但不使用）：
- ~~content-collector~~ → 功能合并到 knowledge-base
- ~~ai-content-collector~~ → 功能合并到 knowledge-base
- ~~game-content-collector~~ → 功能合并到 knowledge-base
- ~~health-content-collector~~ → 功能合并到 knowledge-base
- ~~task-automation~~ → 功能合并到 knowledge-base

**废弃的脚本**（保留在 scripts/ 但不维护）：
- `scripts/daily_collect.py` → 使用 `skills/knowledge-base/scripts/daily_collect.py`
- `scripts/sync_daily_to_feishu.py` → 使用 `skills/knowledge-base/scripts/daily_push.py`
- `scripts/skills_maintenance.py` → 使用 `skills/knowledge-base/scripts/skills_maintenance.py`

### 4. 统一飞书层级结构

**最终结构**：
```
知识库首页
├── 📅 2026年
│   ├── 📅 3月
│   │   ├── 📄 3月17日 日报
│   │   ├── 📄 3月18日 日报
│   │   ├── 📄 3月19日 日报
│   │   ├── 📄 第12期 - 03.17-03.23 周报  ← 与日报同层级
│   │   └── 📄 ...
│   └── 📅 4月
└── 📅 2025年
```

**本地存储结构**：
```
memory/
├── kb-archive/
│   ├── ai-latest-news/
│   │   └── 2026/
│   │       └── 03/
│   │           ├── 17.md       # 日报
│   │           ├── 18.md       # 日报
│   │           ├── 19.md       # 日报
│   │           └── week-12.md  # 周报
│   ├── game-development/
│   └── healthy-living/
├── logs/
│   ├── daily/
│   └── weekly/
└── state/
    ├── collected-urls.json     # 已收集URL（去重用）
    └── task-state.json         # 任务状态
```

### 5. 日报收集规则实现

**代码实现**：
```python
# 只收集最近2天的内容
COLLECT_DAYS = 2

# 去重机制
- 使用 collected-urls.json 记录已收集的URL
- 新内容检查：if is_url_collected(url): skip
- 标记已收集：mark_url_collected(url, kb, title)
```

### 6. 更新 HEARTBEAT.md

整合新规则，简化检查清单：
- 日报收集使用 `daily_pipeline.py`
- 周报收集使用 `weekly_collect.py` + `weekly_push.py`
- 清理使用 `cleanup.py`
- 所有操作遵循 RULES.md

---

## 使用方法

### 执行日报（完整流程）
```bash
python skills/knowledge-base/scripts/daily_pipeline.py
```

### 执行周报
```bash
python skills/knowledge-base/scripts/weekly_collect.py
python skills/knowledge-base/scripts/weekly_push.py
```

### 查看状态
```bash
python skills/knowledge-base/scripts/check_status.py
```

### 清理过期内容
```bash
python skills/knowledge-base/scripts/cleanup.py
```

---

## 保留的旧内容

**保留但不使用的 skills**：
- `skills/content-collector/` - 参考用
- `skills/ai-content-collector/` - 参考用
- `skills/game-content-collector/` - 参考用
- `skills/health-content-collector/` - 参考用
- `skills/task-automation/` - 参考用

**保留但不维护的脚本**：
- `scripts/` 目录下的所有脚本

---

## Git 提交记录

### 提交1：统一知识库管理
```bash
git add -A
git commit -m "refactor: 统一知识库管理，整合所有脚本和规则"
```
提交哈希：`48f6760`

### 提交2：添加整理记录
```bash
git commit -m "docs: 添加工作区整理记录"
```
提交哈希：`c05a4fc`

### 提交3：删除旧脚本和废弃 skills
```bash
git add -A
git commit -m "chore: 删除旧脚本和废弃 skills"
```
提交哈希：`3fbc7fa`

---

## 删除的内容

### 已删除的旧脚本（scripts/）
- ✅ `cleanup_content.py`
- ✅ `daily_collect.py` (旧版)
- ✅ `daily_content_collect.sh`
- ✅ `daily_push_config.env`
- ✅ `daily_push_cron.sh`
- ✅ `skills_maintenance.py` (旧版)
- ✅ `start_cron.sh`
- ✅ `sync_daily_to_feishu.py`
- ✅ `weekly_digest_cron.sh`

**保留的脚本**：
- `track-usage.js` - Token使用统计
- `usage.js` - 使用统计
- `update-usage.sh` - 更新统计

### 已删除的废弃 skills
- ✅ `skills/ai-content-collector/`
- ✅ `skills/ai-content-collector.skill`
- ✅ `skills/content-collector/`
- ✅ `skills/game-content-collector/`
- ✅ `skills/health-content-collector/`
- ✅ `skills/task-automation/`

**保留的 skills**：
- `skills/knowledge-base/` - 统一知识库管理（新建）
- `skills/coze-web-search/` - 网络搜索
- `skills/coze-web-fetch/` - 网页提取
- `skills/coze-image-gen/` - 图片生成
- `skills/coze-voice-gen/` - 语音生成
- `skills/link-collector/` - 链接收集
- `skills/openclaw-updater/` - OpenClaw更新
- `skills/skill-creator/` - 创建skills
- `skills/skill-hub/` - Skill管理

---

## 当前工作区结构

```
workspace/
├── RULES.md                          # 统一规则（权威）
├── HEARTBEAT.md                      # 心跳任务
├── scripts/                          # 保留的脚本
│   ├── track-usage.js
│   ├── usage.js
│   └── update-usage.sh
├── skills/                           # 有效的 skills
│   ├── knowledge-base/               # 统一知识库管理
│   ├── link-collector/
│   ├── openclaw-updater/
│   ├── skill-creator/
│   ├── skill-hub/
│   └── coze-*/
├── config/
└── memory/
```

---

## 使用方法（最终版）

### 执行日报（完整流程）
```bash
python skills/knowledge-base/scripts/daily_pipeline.py
```

### 执行周报
```bash
python skills/knowledge-base/scripts/weekly_collect.py
python skills/knowledge-base/scripts/weekly_push.py
```

### 查看状态
```bash
python skills/knowledge-base/scripts/check_status.py
```

### 清理过期内容
```bash
python skills/knowledge-base/scripts/cleanup.py
```

---

*整理完成时间：2026-03-19 08:50*
*Git 状态：已推送至远程仓库*
