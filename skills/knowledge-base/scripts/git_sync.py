#!/usr/bin/env python3
"""
Git 自动同步脚本
"""

import subprocess
from datetime import datetime
from pathlib import Path

WORKSPACE = Path("/workspace/projects/workspace")


def run_git_command(cmd: list, cwd: Path = WORKSPACE) -> tuple:
    """运行Git命令"""
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=cwd)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)


def git_sync():
    """执行Git同步"""
    print("🔄 Git 自动同步开始...\n")
    
    # 1. 检查Git状态
    success, stdout, stderr = run_git_command(["git", "status", "--porcelain"])
    if not success:
        print(f"❌ 获取Git状态失败: {stderr}")
        return False
    
    if not stdout.strip():
        print("✅ 没有需要提交的更改")
        return True
    
    # 2. 添加所有更改
    print("📦 添加更改...")
    success, _, stderr = run_git_command(["git", "add", "."])
    if not success:
        print(f"❌ git add 失败: {stderr}")
        return False
    
    # 3. 提交更改
    commit_msg = f"auto: daily sync at {datetime.now().strftime('%Y-%m-%d %H:%M')}"
    print(f"📝 提交更改: {commit_msg}")
    success, _, stderr = run_git_command(["git", "commit", "-m", commit_msg])
    if not success:
        print(f"❌ git commit 失败: {stderr}")
        return False
    
    # 4. 推送到远程
    print("☁️ 推送到远程...")
    success, _, stderr = run_git_command(["git", "push"])
    if not success:
        print(f"❌ git push 失败: {stderr}")
        return False
    
    print("\n✅ Git 同步完成！")
    return True


if __name__ == "__main__":
    git_sync()
