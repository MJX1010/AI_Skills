#!/bin/bash
# 周刊精选推送定时任务脚本（带发送功能）
# 每周六早上9点执行

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

# 运行周刊精选推送
python3 skills/content-collector/scripts/weekly_digest_push.py >> /tmp/weekly_digest.log 2>&1

# 获取最新的周刊精选报告
LATEST_REPORT=$(ls -t /workspace/projects/workspace/memory/daily-push/digest-*.txt 2>/dev/null | head -1)

# 如果报告文件存在，发送到飞书
if [ -f "$LATEST_REPORT" ]; then
    REPORT_CONTENT=$(cat "$LATEST_REPORT")
    
    # 发送到飞书
    openclaw message send --channel "$CHANNEL" --target "$FEISHU_TARGET" --message "$REPORT_CONTENT" >> /tmp/weekly_digest.log 2>&1
    
    if [ $? -eq 0 ]; then
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] ✅ 周刊精选已发送到 $FEISHU_TARGET" >> /tmp/weekly_digest.log
    else
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] ❌ 周刊精选发送失败" >> /tmp/weekly_digest.log
    fi
else
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ⚠️ 周刊精选报告不存在" >> /tmp/weekly_digest.log
fi

echo "[$(date '+%Y-%m-%d %H:%M:%S')] 周刊精选推送任务完成" >> /tmp/weekly_digest.log
