#!/usr/bin/env python3
"""
日报完整流程 - 收集+推送
"""

import subprocess
import sys
from datetime import datetime

def main():
    date_str = datetime.now().strftime("%Y-%m-%d")
    
    print("\n" + "="*60)
    print("🔄 日报完整流程")
    print("="*60)
    print(f"📅 日期: {date_str}")
    print("="*60 + "\n")
    
    # 1. 收集日报
    print("【步骤1】收集日报内容...\n")
    result1 = subprocess.run(
        ["python3", "skills/knowledge-base/scripts/daily_collect.py"],
        cwd="/workspace/projects/workspace"
    )
    
    if result1.returncode != 0:
        print("\n❌ 收集失败，停止流程")
        return 1
    
    # 2. 推送日报
    print("\n【步骤2】推送日报到飞书...\n")
    result2 = subprocess.run(
        ["python3", "skills/knowledge-base/scripts/daily_push.py"],
        cwd="/workspace/projects/workspace"
    )
    
    if result2.returncode != 0:
        print("\n⚠️ 推送可能失败，但收集已完成")
    
    print("\n" + "="*60)
    print("✅ 日报流程完成!")
    print("="*60 + "\n")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
