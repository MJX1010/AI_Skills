#!/usr/bin/env python3
"""
Syncer Agent - Git 同步器
负责同步本地缓存和 Skill 到 Git
"""

import argparse
import subprocess
import sys
from datetime import datetime
from pathlib import Path


def run_git_command(cmd, cwd="/workspace/projects/workspace"):
    """运行 Git 命令"""
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30,
            cwd=cwd
        )
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)


def main():
    parser = argparse.ArgumentParser(description="Syncer Agent")
    parser.add_argument("--message", help="Commit message")
    
    args = parser.parse_args()
    
    print("\n" + "=" * 60)
    print("🔄 Syncer Agent: Git 同步")
    print("=" * 60)
    
    # 检查是否有变更
    success, stdout, stderr = run_git_command(["git", "status", "--short"])
    
    if not stdout.strip():
        print("✅ 没有需要同步的变更")
        return 0
    
    print("📋 待同步文件:")
    print(stdout)
    
    # git add
    print("\n📦 git add -A...")
    success, stdout, stderr = run_git_command(["git", "add", "-A"])
    if not success:
        print(f"❌ git add 失败: {stderr}")
        return 1
    print("✅ git add 完成")
    
    # git commit
    commit_msg = args.message or f"content(weekly): update knowledge base content {datetime.now().strftime('%Y-%m-%d')}"
    print(f"\n📝 git commit -m \"{commit_msg}\"...")
    success, stdout, stderr = run_git_command(["git", "commit", "-m", commit_msg])
    if not success:
        print(f"❌ git commit 失败: {stderr}")
        return 1
    print("✅ git commit 完成")
    print(stdout)
    
    # git push (可选)
    # print("\n☁️  git push...")
    # success, stdout, stderr = run_git_command(["git", "push", "origin", "main"])
    # if not success:
    #     print(f"⚠️  git push 失败: {stderr}")
    # else:
    #     print("✅ git push 完成")
    
    print("\n✅ Git 同步完成")
    return 0


if __name__ == "__main__":
    sys.exit(main())
