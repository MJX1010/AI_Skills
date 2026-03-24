#!/usr/bin/env python3
"""
日报完整流程 v2 - 使用 RSS 采集替代搜索
"""

import subprocess
import sys
from datetime import datetime

def main():
    date_str = datetime.now().strftime("%Y-%m-%d")
    
    print("\n" + "="*60)
    print("🔄 日报完整流程 v2 (RSS采集)")
    print("="*60)
    print(f"📅 日期: {date_str}")
    print("="*60 + "\n")
    
    # 1. RSS 采集
    print("【步骤1】RSS 采集...\n")
    result1 = subprocess.run(
        [
            "python3", 
            "skills/knowledge-base/scripts/daily_collect_rss.py",
            "--days", "2",
            "--archive"
        ],
        cwd="/workspace/projects/workspace"
    )
    
    if result1.returncode != 0:
        print("\n❌ RSS 采集失败，停止流程")
        return 1
    
    # 2. 推送日报到飞书
    print("\n【步骤2】推送日报到飞书...\n")
    result2 = subprocess.run(
        ["python3", "skills/knowledge-base/scripts/daily_push.py"],
        cwd="/workspace/projects/workspace"
    )
    
    if result2.returncode != 0:
        print("\n⚠️ 推送可能失败，但 RSS 采集已完成")
    
    print("\n" + "="*60)
    print("✅ 日报流程完成!")
    print("="*60 + "\n")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
