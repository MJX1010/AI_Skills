#!/bin/bash
# 日报定时任务 - 每天 08:00 执行

cd /workspace/projects/workspace

# 记录开始时间
echo "[$(date '+%Y-%m-%d %H:%M:%S')] 开始执行日报收集..." >> memory/logs/cron.log

# 执行日报收集
python skills/knowledge-base/scripts/daily_pipeline.py >> memory/logs/cron.log 2>&1

# 自动提交git
sh scripts/auto-git-commit.sh >> memory/logs/cron.log 2>&1

echo "[$(date '+%Y-%m-%d %H:%M:%S')] 日报任务完成" >> memory/logs/cron.log
