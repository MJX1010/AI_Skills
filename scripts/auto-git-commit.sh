#!/bin/bash
# Git 自动提交脚本
# 提交所有改动，使用自动生成的时间戳提交信息

cd /workspace/projects/workspace

# 检查是否有改动
if [ -z "$(git status --porcelain)" ]; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] 没有需要提交的改动"
    exit 0
fi

# 添加所有改动
git add -A

# 生成提交信息
CHANGED_FILES=$(git diff --cached --name-only | wc -l)
COMMIT_MSG="auto: $(date '+%Y-%m-%d %H:%M') 自动提交 ${CHANGED_FILES} 个文件"

# 提交并推送
git commit -m "$COMMIT_MSG"
git push

echo "[$(date '+%Y-%m-%d %H:%M:%S')] ✅ 已提交并推送: $COMMIT_MSG"
