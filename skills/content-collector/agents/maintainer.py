#!/usr/bin/env python3
"""
Maintainer Agent - 系统维护器
负责 OpenClaw 流程维护和系统健康检查
"""

import argparse
import subprocess
import sys
from datetime import datetime


def check_disk_space():
    """检查磁盘空间"""
    try:
        result = subprocess.run(
            ["df", "-h", "/"],
            capture_output=True,
            text=True,
            timeout=10
        )
        lines = result.stdout.strip().split('\n')
        if len(lines) > 1:
            parts = lines[1].split()
            usage = parts[4]  # 使用率
            return True, f"磁盘使用: {usage}"
    except Exception as e:
        return False, str(e)
    return False, "Unknown"


def check_git_status():
    """检查 Git 状态"""
    try:
        result = subprocess.run(
            ["git", "status", "--short"],
            capture_output=True,
            text=True,
            timeout=10,
            cwd="/workspace/projects/workspace"
        )
        if result.stdout.strip():
            return False, f"有未提交变更: {len(result.stdout.strip().split(chr(10)))} 个文件"
        return True, "Git 状态正常"
    except Exception as e:
        return False, str(e)


def main():
    parser = argparse.ArgumentParser(description="Maintainer Agent")
    parser.add_argument("--check", choices=["health", "git", "disk", "all"],
                       default="all",
                       help="检查类型")
    
    args = parser.parse_args()
    
    print("\n" + "=" * 60)
    print("🔧 Maintainer Agent: 系统维护")
    print("=" * 60)
    print(f"⏰ 检查时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    checks = []
    
    # 健康检查
    if args.check in ["health", "all"]:
        print("\n💚 系统健康检查:")
        
        # 磁盘空间
        ok, msg = check_disk_space()
        status = "✅" if ok else "⚠️"
        print(f"  {status} {msg}")
        checks.append(("disk", ok, msg))
        
        # Git 状态
        ok, msg = check_git_status()
        status = "✅" if ok else "⚠️"
        print(f"  {status} {msg}")
        checks.append(("git", ok, msg))
    
    # 汇总
    print("\n" + "=" * 60)
    print("📊 检查汇总")
    print("=" * 60)
    
    all_ok = all(c[1] for c in checks)
    
    for name, ok, msg in checks:
        status = "✅" if ok else "❌"
        print(f"{status} {name}: {msg}")
    
    if all_ok:
        print("\n✅ 系统状态正常")
        return 0
    else:
        print("\n⚠️  发现异常，请检查")
        return 1


if __name__ == "__main__":
    sys.exit(main())
