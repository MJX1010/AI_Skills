#!/bin/bash
# 每日资讯收集定时任务脚本
# 每天早上8点执行，收集前一天发布的资讯并同步到飞书

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

# 获取昨天日期
YESTERDAY=$(date -d "yesterday" +%Y-%m-%d)
TODAY=$(date +%Y-%m-%d)

echo "========================================"
echo "📅 每日资讯收集"
echo "⏰ 执行时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo "📊 收集日期: $YESTERDAY (前一天)"
echo "========================================"
echo ""

# 收集三个知识库的日报
TOTAL_COUNT=0

# 🤖 AI最新资讯
echo "🤖 收集 AI最新资讯..."
python3 skills/content-collector/scripts/collect.py --kb ai-latest-news --daily --date "$YESTERDAY" >> /tmp/daily_collect.log 2>&1
AI_COUNT=$(grep -c "^### " memory/ai-content/daily/$YESTERDAY.md 2>/dev/null || echo "0")
echo "   ✅ AI资讯: $AI_COUNT 篇"
TOTAL_COUNT=$((TOTAL_COUNT + AI_COUNT))

# 🎮 游戏开发
echo "🎮 收集 游戏开发..."
python3 skills/content-collector/scripts/collect.py --kb game-development --daily --date "$YESTERDAY" >> /tmp/daily_collect.log 2>&1
GAME_COUNT=$(grep -c "^### " memory/game-content/daily/$YESTERDAY.md 2>/dev/null || echo "0")
echo "   ✅ 游戏开发: $GAME_COUNT 篇"
TOTAL_COUNT=$((TOTAL_COUNT + GAME_COUNT))

# 🌱 健康生活
echo "🌱 收集 健康生活..."
python3 skills/content-collector/scripts/collect.py --kb healthy-living --daily --date "$YESTERDAY" >> /tmp/daily_collect.log 2>&1
HEALTH_COUNT=$(grep -c "^### " memory/health-content/daily/$YESTERDAY.md 2>/dev/null || echo "0")
echo "   ✅ 健康生活: $HEALTH_COUNT 篇"
TOTAL_COUNT=$((TOTAL_COUNT + HEALTH_COUNT))

echo ""
echo "========================================"
echo "📊 收集完成统计"
echo "========================================"
echo "🤖 AI最新资讯: $AI_COUNT 篇"
echo "🎮 游戏开发: $GAME_COUNT 篇"
echo "🌱 健康生活: $HEALTH_COUNT 篇"
echo "📈 总计: $TOTAL_COUNT 篇"
echo "========================================"

# 同步到飞书知识库
echo ""
echo "🔄 正在同步到飞书知识库..."
python3 scripts/sync_daily_to_feishu.py --date "$YESTERDAY" >> /tmp/daily_collect.log 2>&1

if [ $? -eq 0 ]; then
    echo "✅ 飞书同步成功"
else
    echo "⚠️ 飞书同步可能有问题，请检查日志"
fi

# 清理旧文件（保留最近7天日报，30天周刊）
echo ""
echo "🧹 清理旧文件..."
python3 scripts/cleanup_content.py >> /tmp/daily_collect.log 2>&1
echo "✅ 清理完成"

# 生成推送消息
MESSAGE="📅 $(date -d $YESTERDAY +%Y年%m月%d日) 资讯早报

📊 昨日新资讯: $TOTAL_COUNT 篇

🤖 AI最新资讯: $AI_COUNT 篇
🎮 游戏开发: $GAME_COUNT 篇
🌱 健康生活: $HEALTH_COUNT 篇

⏰ 每天早上8点自动收集前一天资讯
💡 来源: 量子位/36氪/虎嗅/爱范儿/少数派/知乎等
✅ 已同步至飞书知识库
🧹 自动清理7天前旧文件"

# 发送到飞书
echo ""
echo "📤 正在推送到飞书..."
openclaw message send --channel "$CHANNEL" --target "$FEISHU_TARGET" --message "$MESSAGE" >> /tmp/daily_collect.log 2>&1

if [ $? -eq 0 ]; then
    echo "✅ 推送成功"
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ✅ 日报推送成功: $TOTAL_COUNT 篇" >> /tmp/daily_collect_cron.log
else
    echo "❌ 推送失败"
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ❌ 日报推送失败" >> /tmp/daily_collect_cron.log
fi

echo ""
echo "✅ 每日资讯收集任务完成"
echo "[$(date '+%Y-%m-%d %H:%M:%S')] 任务完成" >> /tmp/daily_collect_cron.log
