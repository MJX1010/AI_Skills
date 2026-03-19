# HEARTBEAT.md - 定期检查任务

> 遵循 [RULES.md](RULES.md) 统一规则
> 心跳每4小时运行一次

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
- [ ] 更新 Token 使用统计

### 3. 系统健康检查（每次）
- [ ] OpenClaw 网关状态
- [ ] 飞书渠道连接状态
- [ ] 磁盘空间使用情况

### 4. 知识库日报收集（每天 08:00）

**使用统一脚本**（遵循 RULES.md 规则1：只收集最近2天）：
```bash
python skills/knowledge-base/scripts/daily_pipeline.py
```

**流程**：
1. 收集最近2天发布的内容
2. 自动去重（已收集URL不再重复收集）
3. 推送到飞书知识库（年月/日报 层级）
4. 推送到飞书对话窗口

**本地存储**：
- `memory/kb-archive/{kb}/{year}/{month}/{day}.md`

**飞书层级**：
```
2026年 → 3月 → 3月19日 日报
```

---

### 5. 知识库周报收集（每周五 18:00）

**使用统一脚本**：
```bash
python skills/knowledge-base/scripts/weekly_collect.py
python skills/knowledge-base/scripts/weekly_push.py
```

**流程**：
1. 汇总本周（周一到周日）所有日报内容
2. 生成周报 Markdown
3. 同步到飞书知识库（与日报同层级）

**飞书层级**：
```
2026年 → 3月 → 3月19日 日报
              → 第12期 - 03.17-03.23 周报  ← 与日报同层级
```

---

### 6. 内容清理（每天 23:00）

**使用统一脚本**（遵循 RULES.md 规则2）：
```bash
python skills/knowledge-base/scripts/cleanup.py
```

**清理策略**：
| 内容类型 | 保留时间 |
|----------|----------|
| 日报 | 7天 |
| 周报 | 30天 |
| 模块归档 | 90天 |

---

### 7. Git 同步（每天 22:00）

**使用统一脚本**：
```bash
python skills/knowledge-base/scripts/git_sync.py
```

---

### 8. Skills 维护（每周日）

- [ ] 检查各 skill 的更新情况
- [ ] 验证 SKILL.md 完整性
- [ ] 更新 skill 文档

**使用脚本**：
```bash
python skills/knowledge-base/scripts/skills_maintenance.py
```

---

### 9. OpenClaw 更新检查（每周日）

- [ ] 查看最新 GitHub releases
- [ ] 检查官方文档变更
- [ ] 记录更新日志

**使用脚本**：
```bash
python skills/openclaw-updater/scripts/check_updates.py
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

### 查看任务状态
```bash
python skills/knowledge-base/scripts/check_status.py
```

### 清理过期内容
```bash
python skills/knowledge-base/scripts/cleanup.py
```

---

## 📁 统一目录结构

```
workspace/
├── RULES.md                          # 统一规则文档（权威）
├── HEARTBEAT.md                      # 本文件
├── skills/
│   └── knowledge-base/               # 统一知识库管理
│       ├── SKILL.md
│       └── scripts/
│           ├── daily_collect.py      # 日报收集
│           ├── daily_push.py         # 日报推送
│           ├── weekly_collect.py     # 周报收集
│           ├── weekly_push.py        # 周报推送
│           ├── cleanup.py            # 内容清理
│           ├── git_sync.py           # Git同步
│           └── check_status.py       # 状态检查
├── config/
│   ├── content_sources.yaml          # 内容来源配置
│   └── retention_policy.yaml         # 保留策略配置
└── memory/
    ├── kb-archive/                   # 知识库内容
    │   ├── ai-latest-news/
    │   ├── game-development/
    │   └── healthy-living/
    ├── logs/                         # 日志
    └── state/                        # 状态文件
```

---

## 🔔 提醒规则

**静默时段**：23:00 - 08:00（除非紧急情况）

**触发通知的条件**：
- 发现重要未读消息
- 日历事件即将发生（< 2小时）
- 系统出现异常
- 超过8小时未联系

**保持静默的情况**：
- 刚检查过（< 30分钟）
- 无明显异常
- 用户明显忙碌中

---

## 📝 记录格式

每次检查后更新 `memory/heartbeat-state.json`：

```json
{
  "lastChecks": {
    "memory": "2026-03-19T08:00:00Z",
    "git": "2026-03-19T08:00:00Z",
    "system": "2026-03-19T08:00:00Z",
    "daily_collection": "2026-03-19T08:00:00Z",
    "weekly_collection": "2026-03-14T18:00:00Z"
  }
}
```

---

## 📚 相关文档

- **统一规则**: [RULES.md](RULES.md)
- **知识库管理**: `skills/knowledge-base/SKILL.md`
- **内容来源**: `config/content_sources.yaml`
- **保留策略**: `config/retention_policy.yaml`

---

*最后更新：2026-03-19*
*统一知识库管理版本：v1.0*
