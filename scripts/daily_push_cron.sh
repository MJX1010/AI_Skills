#!/bin/bash
# 知识库日报推送定时任务脚本
# 每天早上8点执行

export PATH="/usr/local/bin:/usr/bin:/bin:/usr/local/sbin:/usr/sbin:/sbin"
export HOME="/root"

cd /workspace/projects/workspace

# 加载配置文件
CONFIG_FILE="/workspace/projects/workspace/scripts/daily_push_config.env"
if [ -f "$CONFIG_FILE" ]; then
    source "$CONFIG_FILE"
fi

# 设置默认值
FEISHU_TARGET="${FEISHU_DAILY_PUSH_TARGET:-ou_f24a618d3c176917dccc8bec5bdccd12}"
CHANNEL="${CHANNEL:-feishu}"

# 运行日报推送
python3 skills/link-collector/scripts/daily_push_enhanced.py >> /tmp/daily_push.log 2>&1

# 获取今日报告文件
TODAY=$(date '+%Y%m%d')
REPORT_FILE="/workspace/projects/workspace/memory/daily-push/report-${TODAY}.txt"

# 如果报告文件存在，发送到飞书
if [ -f "$REPORT_FILE" ]; then
    # 读取报告内容
    REPORT_CONTENT=$(cat "$REPORT_FILE")
    
    # 发送到飞书（使用 openclaw message）
    openclaw message send --channel "$CHANNEL" --target "$FEISHU_TARGET" --message "$REPORT_CONTENT" >> /tmp/daily_push_cron.log 2>&1
    
    if [ $? -eq 0 ]; then
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] ✅ 日报已生成并发送到 $FEISHU_TARGET" >> /tmp/daily_push_cron.log
    else
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] ❌ 日报发送失败" >> /tmp/daily_push_cron.log
    fi
else
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ⚠️ 报告文件不存在: $REPORT_FILE" >> /tmp/daily_push_cron.log
fi

# 记录执行时间
echo "[$(date '+%Y-%m-%d %H:%M:%S')] 日报推送任务完成" >> /tmp/daily_push_cron.log
