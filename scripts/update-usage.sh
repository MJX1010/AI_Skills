#!/bin/bash
# Token 追踪自动更新脚本
# 可添加到 crontab 或 heartbeat 中定期执行

cd /workspace/projects/workspace
node scripts/track-usage.js > /dev/null 2>&1
