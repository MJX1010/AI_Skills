#!/bin/bash
# 知识库日报推送定时任务脚本
# 每天早上8点执行

export PATH="/usr/local/bin:/usr/bin:/bin:/usr/local/sbin:/usr/sbin:/sbin"
export HOME="/root"

cd /workspace/projects/workspace

# 运行日报推送
python3 skills/link-collector/scripts/daily_push_enhanced.py >> /tmp/daily_push.log 2>&1

# 记录执行时间
echo "[$(date '+%Y-%m-%d %H:%M:%S')] 日报推送已执行" >> /tmp/daily_push_cron.log
