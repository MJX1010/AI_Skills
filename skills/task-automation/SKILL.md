---
name: task-automation
description: |
  管理和执行自动化任务，包括心跳检查、周刊收集、知识库同步、定时推送等。
  提供任务调度、执行、状态监控的全套工具。
  Triggers: "运行自动化任务", "检查任务状态", "执行任务", "task", "automation"
---

# 自动化任务管理器

统一管理和执行所有自动化任务，包括定时收集、同步、推送等。

## 📋 任务清单

| 任务名称 | 频率 | 执行时间 | 优先级 | 脚本路径 |
|----------|------|----------|--------|----------|
| **Heartbeat** | 每4小时 | - | P0 | `HEARTBEAT.md` |
| **周刊收集** | 每周 | 周五 18:00 | P1 | `scripts/weekly_collection.py` |
| **知识库日报** | 每天 | 08:00 | P2 | `scripts/daily_digest.py` |
| **周刊推送** | 每周 | 周六 09:00 | P2 | `scripts/weekly_push.py` |
| **Skills维护** | 每周 | 周日 10:00 | P3 | `scripts/skills_maintenance.py` |
| **OpenClaw更新** | 每周 | 周日 12:00 | P3 | `scripts/openclaw_update.py` |
| **Git同步** | 每天 | 22:00 | P2 | `scripts/git_sync.py` |

---

## 🚀 快速使用

### 执行单个任务

```bash
# 运行周刊收集
python skills/task-automation/scripts/run_task.py --task weekly_collection

# 运行日报推送
python skills/task-automation/scripts/run_task.py --task daily_digest

# 运行 Git 同步
python skills/task-automation/scripts/run_task.py --task git_sync
```

### 检查任务状态

```bash
# 查看所有任务状态
python skills/task-automation/scripts/check_status.py --all

# 查看指定任务状态
python skills/task-automation/scripts/check_status.py --task weekly_collection
```

### 手动触发任务

```bash
# 强制立即执行（忽略调度时间）
python skills/task-automation/scripts/run_task.py --task weekly_collection --force
```

---

## 📁 任务详细说明

### 1️⃣ Heartbeat 心跳检查

**文件**: `HEARTBEAT.md`

**检查项**:
- 记忆维护（每周一次）
- 项目状态检查（Git状态、Token统计）
- 系统健康检查（OpenClaw状态、飞书连接）
- 周刊自动归档（每周五）
- 知识库日报推送（每天8:00）
- 周刊精选推送（每周六）
- Skills维护（每周日）
- OpenClaw更新检查（每周日）

**状态记录**: `memory/heartbeat-state.json`

**执行**:
```bash
# 心跳检查由系统每4小时自动触发
# 手动执行参考 HEARTBEAT.md 中的检查清单
```

---

### 2️⃣ 周刊收集 (weekly_collection)

**频率**: 每周五 18:00

**流程**:
1. 收集三个知识库内容
2. 分类整理到各模块
3. 生成本地周刊 Markdown
4. 同步到飞书知识库
5. 更新操作日志

**执行**:
```bash
# 使用 content-collector
python skills/content-collector/scripts/full_pipeline.py --week current

# 或分步执行
python skills/content-collector/scripts/collect_all.py --week current
python skills/content-collector/scripts/sync_feishu.py --all --week current
```

**输出**:
- `memory/ai-content/weekly/weekly-YYYY-WXX.md`
- `memory/game-content/weekly/game-weekly-YYYY-WXX.md`
- `memory/health-content/weekly/health-weekly-YYYY-WXX.md`
- 飞书知识库对应周刊文档

---

### 3️⃣ 知识库日报 (daily_digest)

**频率**: 每天 08:00

**流程**:
1. 检查三个知识库当日新增内容
2. 生成文本摘要
3. 生成飞书卡片
4. 发送推送通知

**执行**:
```bash
python skills/task-automation/scripts/daily_digest.py
```

**静默规则**: 23:00-08:00 不推送（除非紧急）

---

### 4️⃣ 周刊精选推送 (weekly_push)

**频率**: 每周六 09:00

**流程**:
1. 汇总本周三个知识库 Top 精选
2. 生成综合周报
3. 推送并附带完整周刊链接

**执行**:
```bash
python skills/task-automation/scripts/weekly_push.py
```

---

### 5️⃣ Skills 维护 (skills_maintenance)

**频率**: 每周日 10:00

**检查项**:
- 检查各 skill 的更新情况
- 更新 skill 版本和功能
- 更新 skill 文档和来源配置
- 测试更新后的功能

**执行**:
```bash
# 检查所有 skills
python skills/skill-hub/scripts/check_updates.py --all

# 更新指定 skill
python skills/skill-hub/scripts/update_skill.py --skill <name>
```

---

### 6️⃣ OpenClaw 更新检查 (openclaw_update)

**频率**: 每周日 12:00

**检查项**:
- 查看最新 GitHub releases
- 检查官方文档变更
- 评估并执行更新
- 记录更新日志

**执行**:
```bash
python skills/openclaw-updater/scripts/check_updates.py
```

**日志**: `memory/openclaw-updates.json`

---

### 7️⃣ Git 同步 (git_sync)

**频率**: 每天 22:00

**流程**:
1. 检查 workspace 变更
2. 自动提交更改
3. 推送到远程仓库

**执行**:
```bash
python skills/task-automation/scripts/git_sync.py
```

---

## 🔧 配置管理

### 任务配置

配置文件: `skills/task-automation/config/tasks.yaml`

```yaml
tasks:
  heartbeat:
    enabled: true
    interval: 4h
    priority: P0
    
  weekly_collection:
    enabled: true
    schedule: "0 18 * * 5"  # 每周五 18:00
    priority: P1
    
  daily_digest:
    enabled: true
    schedule: "0 8 * * *"   # 每天 08:00
    priority: P2
    
  weekly_push:
    enabled: true
    schedule: "0 9 * * 6"   # 每周六 09:00
    priority: P2
    
  skills_maintenance:
    enabled: true
    schedule: "0 10 * * 0"  # 每周日 10:00
    priority: P3
    
  openclaw_update:
    enabled: true
    schedule: "0 12 * * 0"  # 每周日 12:00
    priority: P3
    
  git_sync:
    enabled: true
    schedule: "0 22 * * *"  # 每天 22:00
    priority: P2
```

### 知识库配置

```yaml
knowledge_bases:
  ai-latest-news:
    space_id: "7616519632920251572"
    home_token: "PhL6wlstzissQ1kKPwMc18xbngg"
    modules: [news, tools, research, cases]
    
  game-development:
    space_id: "7616735513310924004"
    home_token: "U9EWwwL8ui16IEkrN8vcIRISnFg"
    modules: [engine, design, tech, art, audio, indie]
    
  healthy-living:
    space_id: "7616737910330510558"
    home_token: "XD2PwwJukiD8a8koNAAc4Fedn5t"
    modules: [fitness, diet, mental, sleep, medical, tips]
```

---

## 📊 状态监控

### 任务状态文件

`memory/task-automation/state.json`:

```json
{
  "tasks": {
    "weekly_collection": {
      "last_run": "2026-03-14T18:00:00Z",
      "last_status": "success",
      "next_run": "2026-03-21T18:00:00Z",
      "run_count": 12,
      "error_count": 0
    },
    "daily_digest": {
      "last_run": "2026-03-19T08:00:00Z",
      "last_status": "success",
      "next_run": "2026-03-20T08:00:00Z",
      "run_count": 78,
      "error_count": 1
    }
  }
}
```

### 查看运行日志

```bash
# 查看最近日志
tail -100 memory/task-automation/logs/weekly_collection.log

# 查看所有错误日志
grep "ERROR" memory/task-automation/logs/*.log
```

---

## 🛠️ 故障排除

### 任务执行失败

```bash
# 1. 查看错误日志
python skills/task-automation/scripts/check_status.py --task <name> --verbose

# 2. 手动重试
python skills/task-automation/scripts/run_task.py --task <name> --force

# 3. 重置任务状态
python skills/task-automation/scripts/reset_task.py --task <name>
```

### 飞书同步失败

```bash
# 检查飞书连接
feishu_wiki --action spaces

# 重新同步指定知识库
python skills/content-collector/scripts/sync_feishu.py --kb ai-latest-news --week current
```

### Git 同步失败

```bash
# 手动检查 Git 状态
cd /workspace/projects/workspace && git status

# 手动提交
git add . && git commit -m "backup: $(date)" && git push
```

---

## 📝 添加新任务

1. **创建任务脚本**
   ```bash
   touch skills/task-automation/scripts/my_task.py
   chmod +x skills/task-automation/scripts/my_task.py
   ```

2. **注册任务配置**
   编辑 `skills/task-automation/config/tasks.yaml`:
   ```yaml
   tasks:
     my_task:
       enabled: true
       schedule: "0 9 * * 1"  # 每周一 09:00
       priority: P2
       script: scripts/my_task.py
   ```

3. **测试任务**
   ```bash
   python skills/task-automation/scripts/run_task.py --task my_task --force
   ```

---

## 🔔 通知配置

任务执行结果可通过以下方式通知:

| 渠道 | 配置 | 用途 |
|------|------|------|
| 飞书消息 | `config/notifications.yaml` | 任务成功/失败通知 |
| 日志文件 | `memory/task-automation/logs/` | 详细执行日志 |
| 状态文件 | `memory/task-automation/state.json` | 任务状态追踪 |

---

## 📚 相关 Skills

| Skill | 用途 | 路径 |
|-------|------|------|
| content-collector | 内容收集与同步 | `skills/content-collector/` |
| link-collector | 链接归档（本地） | `skills/link-collector/` |
| openclaw-updater | OpenClaw更新检查 | `skills/openclaw-updater/` |
| skill-hub | Skill管理 | `skills/skill-hub/` |

---

*自动化任务管理器 - 让重复工作自动化*
