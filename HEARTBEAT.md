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

### 4. AI 每周精选（每周五下午 6:00）
- [ ] 运行周刊收集脚本: `python skills/ai-content-collector/scripts/collect_weekly.py`
- [ ] 按「工具/资源 + 文章 + 工具」三段式整理内容
- [ ] 添加链接引用（标题链接 + 来源标注）
- [ ] 发布新一期周刊到飞书知识库

### 5. Skills 维护（每周日）
- [ ] 检查各 skill 的更新情况（查看官方源、GitHub 等）
- [ ] 如有更新，更新 skill 版本和功能
- [ ] 更新 skill 文档和来源配置
- [ ] 测试更新后的功能是否正常

### 6. OpenClaw 更新检查（每周日）
- [ ] 运行 `openclaw-updater` skill 检查更新
- [ ] 查看最新 GitHub releases
- [ ] 检查当前版本 vs 最新版本
- [ ] 如有更新，评估并执行更新
- [ ] 记录更新日志到 `memory/openclaw-updates.json`

### 6. OpenClaw 更新检查（每周日）
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
    "token": "2026-03-11T23:00:00Z"
  }
}
```

---

*最后更新：2026-03-13*
