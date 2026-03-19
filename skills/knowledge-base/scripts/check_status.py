#!/usr/bin/env python3
"""
状态检查脚本 - 查看任务执行状态
"""

import json
from datetime import datetime
from pathlib import Path

WORKSPACE = Path("/workspace/projects/workspace")
MEMORY_DIR = WORKSPACE / "memory"
STATE_FILE = MEMORY_DIR / "state" / "task-state.json"

TASKS = {
    "daily_collect": {"name": "日报收集", "schedule": "每天 08:00"},
    "daily_push": {"name": "日报推送", "schedule": "每天 08:30"},
    "weekly_collect": {"name": "周报收集", "schedule": "周五 18:00"},
    "weekly_push": {"name": "周报推送", "schedule": "周六 09:00"},
    "cleanup": {"name": "内容清理", "schedule": "每天 23:00"},
    "git_sync": {"name": "Git同步", "schedule": "每天 22:00"}
}


def load_state():
    """加载状态"""
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text())
    return {}


def format_time(iso_time):
    """格式化时间"""
    if not iso_time:
        return "从未"
    try:
        dt = datetime.fromisoformat(iso_time.replace("Z", "+00:00"))
        return dt.strftime("%m-%d %H:%M")
    except:
        return iso_time


def main():
    print("\n" + "="*60)
    print("📊 任务执行状态")
    print("="*60 + "\n")
    
    state = load_state()
    
    print(f"{'任务名称':<12} {'最后执行':<12} {'状态':<8} {'运行次数'}")
    print("-" * 50)
    
    for task_id, info in TASKS.items():
        task_state = state.get(task_id, {})
        last_run = format_time(task_state.get("last_run"))
        status = task_state.get("status", "未执行")
        count = task_state.get("count", 0)
        
        if status == "success":
            status = "✅ 成功"
        elif status == "failed":
            status = "❌ 失败"
        else:
            status = "⏳ 未执行"
        
        print(f"{info['name']:<10} {last_run:<12} {status:<8} {count}")
    
    print("\n" + "="*60)
    
    # 显示知识库内容统计
    print("\n📚 知识库内容统计\n")
    
    kb_dir = MEMORY_DIR / "kb-archive"
    if kb_dir.exists():
        for kb in ["ai-latest-news", "game-development", "healthy-living"]:
            kb_path = kb_dir / kb
            if kb_path.exists():
                count = sum(1 for _ in kb_path.rglob("*.md"))
                print(f"  {kb}: {count} 个文件")
    
    print("\n" + "="*60 + "\n")
    
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
