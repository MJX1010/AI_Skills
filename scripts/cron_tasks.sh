#!/bin/bash
# 知识库定时任务脚本
# 每小时检查一次，在指定时间执行相应任务并推送结果

WORKSPACE="/workspace/projects/workspace"
LOG_FILE="$WORKSPACE/memory/logs/cron.log"
PUSH_LOG="$WORKSPACE/memory/logs/push.log"

# 确保日志目录存在
mkdir -p "$WORKSPACE/memory/logs"

# 获取当前时间
HOUR=$(date +%H)
MIN=$(date +%M)
WEEKDAY=$(date +%w)  # 0=周日, 1=周一, ..., 6=周六
DATE_STR=$(date '+%Y-%m-%d')

echo "[$(date '+%Y-%m-%d %H:%M:%S')] 定时任务检查 - 当前时间: ${HOUR}:${MIN}, 星期${WEEKDAY}" >> "$LOG_FILE"

cd "$WORKSPACE"

# ============================================
# 08:00 - 日报收集
# ============================================
if [ "$HOUR" = "08" ] && [ "$MIN" -lt "05" ]; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] 开始执行日报收集..." >> "$LOG_FILE"
    python3 skills/knowledge-base/scripts/daily_pipeline.py >> "$LOG_FILE" 2>&1
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] 日报收集完成" >> "$LOG_FILE"
fi

# ============================================
# 08:30 - 推送日报结果（方案1）
# ============================================
if [ "$HOUR" = "08" ] && [ "$MIN" = "30" ]; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] 准备推送日报结果..." >> "$PUSH_LOG"
    
    # 生成推送消息
    PUSH_MSG=$(python3 skills/knowledge-base/scripts/send_notification.py 2>/dev/null)
    
    # 保存推送消息到文件（供后续读取）
    echo "$PUSH_MSG" > "$WORKSPACE/memory/logs/daily_push_${DATE_STR}.txt"
    
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] 日报推送消息已生成" >> "$PUSH_LOG"
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] 推送内容保存至: memory/logs/daily_push_${DATE_STR}.txt" >> "$PUSH_LOG"
fi

# ============================================
# 每周五 18:00 - 周报收集
# ============================================
if [ "$WEEKDAY" = "5" ] && [ "$HOUR" = "18" ] && [ "$MIN" -lt "05" ]; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] 开始执行周报收集..." >> "$LOG_FILE"
    python3 skills/knowledge-base/scripts/weekly_pipeline.py >> "$LOG_FILE" 2>&1
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] 周报收集完成" >> "$LOG_FILE"
fi

# ============================================
# 每周五 18:30 - 推送周报结果（方案1）
# ============================================
if [ "$WEEKDAY" = "5" ] && [ "$HOUR" = "18" ] && [ "$MIN" = "30" ]; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] 准备推送周报结果..." >> "$PUSH_LOG"
    
    # 生成推送消息（标记为周报）
    PUSH_MSG=$(python3 skills/knowledge-base/scripts/send_notification.py 2>/dev/null)
    
    # 保存推送消息到文件
    echo "$PUSH_MSG" > "$WORKSPACE/memory/logs/weekly_push_${DATE_STR}.txt"
    
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] 周报推送消息已生成" >> "$PUSH_LOG"
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] 推送内容保存至: memory/logs/weekly_push_${DATE_STR}.txt" >> "$PUSH_LOG"
fi

# ============================================
# 每天 22:00 - Git 同步
# ============================================
if [ "$HOUR" = "22" ] && [ "$MIN" -lt "05" ]; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] 开始执行 Git 同步..." >> "$LOG_FILE"
    cd "$WORKSPACE" && git add -A && git commit -m "auto: daily backup $(date '+%Y-%m-%d %H:%M')" >> "$LOG_FILE" 2>&1 && git push >> "$LOG_FILE" 2>&1
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Git 同步完成" >> "$LOG_FILE"
fi

# ============================================
# 每天 23:00 - 内容清理
# ============================================
if [ "$HOUR" = "23" ] && [ "$MIN" -lt "05" ]; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] 开始执行内容清理..." >> "$LOG_FILE"
    python3 skills/knowledge-base/scripts/cleanup.py >> "$LOG_FILE" 2>&1
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] 内容清理完成" >> "$LOG_FILE"
fi

# ============================================
# 每周日 10:00 - Skills 维护
# ============================================
if [ "$WEEKDAY" = "0" ] && [ "$HOUR" = "10" ] && [ "$MIN" -lt "05" ]; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] 开始执行 Skills 维护..." >> "$LOG_FILE"
    # 这里可以添加 skills 维护逻辑
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Skills 维护完成" >> "$LOG_FILE"
fi

echo "[$(date '+%Y-%m-%d %H:%M:%S')] 定时任务检查结束" >> "$LOG_FILE"
