# 定时任务配置说明

## 📅 定时任务列表

| 时间 | 任务 | 脚本 | 说明 |
|------|------|------|------|
| 每天 08:00 | 日报收集 | `daily_pipeline.py` | 收集最近2天内容并推送到飞书 |
| 每周五 18:00 | 周报收集 | `weekly_pipeline.py` | 汇总本周内容并推送到飞书 |
| 每天 22:00 | Git 同步 | `git_sync.py` | 自动提交并推送更改 |
| 每天 23:00 | 内容清理 | `cleanup.py` | 清理过期内容（日报7天/周报30天） |
| 每周日 10:00 | Skills 维护 | - | 检查 skills 更新 |

---

## 🚀 使用方法

由于当前环境没有 `crontab`，提供以下替代方案：

### 方案1：使用系统 systemd（推荐，如果有权限）

```bash
# 创建 systemd 服务文件
sudo tee /etc/systemd/system/kb-collector.service << 'EOF'
[Unit]
Description=Knowledge Base Collector
After=network.target

[Service]
Type=oneshot
ExecStart=/workspace/projects/workspace/scripts/cron_tasks.sh
User=root
EOF

# 创建 systemd 定时器
sudo tee /etc/systemd/system/kb-collector.timer << 'EOF'
[Unit]
Description=Run KB Collector every hour

[Timer]
OnCalendar=hourly
Persistent=true

[Install]
WantedBy=timers.target
EOF

# 启用并启动
sudo systemctl daemon-reload
sudo systemctl enable kb-collector.timer
sudo systemctl start kb-collector.timer
```

### 方案2：使用 while 循环后台运行

```bash
# 在后台持续运行，每小时检查一次
while true; do
    /workspace/projects/workspace/scripts/cron_tasks.sh
    sleep 3600  # 每小时检查一次
done &
```

### 方案3：手动执行（临时）

```bash
# 直接执行脚本
/workspace/projects/workspace/scripts/cron_tasks.sh
```

### 方案4：使用 OpenClaw 的 cron 功能

```bash
# 使用 openclaw cron 命令（如果支持）
openclaw cron add --name "daily_collect" --schedule "0 8 * * *" \
  --command "python3 /workspace/projects/workspace/skills/knowledge-base/scripts/daily_pipeline.py"
```

---

## 📝 手动执行命令

如果暂时无法配置自动定时任务，可以手动执行：

```bash
# 日报收集（每天执行）
python3 skills/knowledge-base/scripts/daily_pipeline.py

# 周报收集（每周五执行）
python3 skills/knowledge-base/scripts/weekly_pipeline.py

# Git 同步
python3 skills/knowledge-base/scripts/git_sync.py

# 内容清理
python3 skills/knowledge-base/scripts/cleanup.py
```

---

## 📊 日志位置

定时任务日志：`memory/logs/cron.log`

```bash
# 查看定时任务日志
tail -f /workspace/projects/workspace/memory/logs/cron.log
```

---

## ⚙️ 修改定时任务

编辑脚本文件修改任务时间：

```bash
nano /workspace/projects/workspace/scripts/cron_tasks.sh
```

修改以下变量：
- `HOUR` - 小时 (00-23)
- `MIN` - 分钟 (00-59)
- `WEEKDAY` - 星期 (0-6, 0=周日)

---

*配置时间：2026-03-19*
