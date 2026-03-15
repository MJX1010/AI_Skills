#!/bin/bash
# 启动Cron服务脚本
# 由于systemd不可用，需要手动启动

echo "Starting cron service..."

# 检查是否已经在运行
if pgrep -x "cron" > /dev/null; then
    echo "Cron is already running."
    exit 0
fi

# 启动cron
/usr/sbin/cron

# 验证
sleep 1
if pgrep -x "cron" > /dev/null; then
    echo "Cron started successfully."
    echo "Current crontab:"
    crontab -l
else
    echo "Failed to start cron."
    exit 1
fi
