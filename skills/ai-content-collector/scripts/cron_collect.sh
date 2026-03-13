#!/bin/bash
# AI 内容收集定时任务脚本
# 可添加到 crontab: 0 9 * * * /workspace/projects/workspace/skills/ai-content-collector/scripts/cron_collect.sh

cd /workspace/projects/workspace

# 设置日志
LOG_FILE="/workspace/projects/logs/ai-content.log"
mkdir -p /workspace/projects/logs

echo "=== AI Content Collection - $(date) ===" >> $LOG_FILE

# 运行收集脚本
python3 skills/ai-content-collector/scripts/collect_daily.py --date today >> $LOG_FILE 2>&1

# 检查结果
if [ $? -eq 0 ]; then
    echo "✅ Collection successful" >> $LOG_FILE
else
    echo "❌ Collection failed" >> $LOG_FILE
fi

echo "" >> $LOG_FILE
