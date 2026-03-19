#!/usr/bin/env python3
"""
任务执行器 - 运行指定的自动化任务
"""

import argparse
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

# 任务配置
TASKS = {
    "weekly_collection": {
        "name": "周刊收集",
        "script": "skills/content-collector/scripts/full_pipeline.py",
        "args": ["--week", "current"],
        "description": "收集三个知识库的本周内容并同步到飞书"
    },
    "daily_digest": {
        "name": "知识库日报",
        "script": "skills/task-automation/scripts/daily_digest.py",
        "args": [],
        "description": "推送今日知识库更新摘要"
    },
    "weekly_push": {
        "name": "周刊推送",
        "script": "skills/task-automation/scripts/weekly_push.py",
        "args": [],
        "description": "推送本周精选内容"
    },
    "skills_maintenance": {
        "name": "Skills维护",
        "script": "skills/task-automation/scripts/skills_maintenance.py",
        "args": [],
        "description": "检查并更新Skills"
    },
    "openclaw_update": {
        "name": "OpenClaw更新检查",
        "script": "skills/openclaw-updater/scripts/check_updates.py",
        "args": [],
        "description": "检查OpenClaw更新"
    },
    "git_sync": {
        "name": "Git同步",
        "script": "skills/task-automation/scripts/git_sync.py",
        "args": [],
        "description": "自动提交并推送Git更改"
    }
}

STATE_FILE = Path("memory/task-automation/state.json")
LOG_DIR = Path("memory/task-automation/logs")


def ensure_dirs():
    """确保目录存在"""
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    if not STATE_FILE.exists():
        STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
        STATE_FILE.write_text(json.dumps({"tasks": {}}, indent=2))


def load_state():
    """加载任务状态"""
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text())
    return {"tasks": {}}


def save_state(state):
    """保存任务状态"""
    STATE_FILE.write_text(json.dumps(state, indent=2))


def run_task(task_key: str, force: bool = False):
    """运行指定任务"""
    if task_key not in TASKS:
        print(f"❌ 未知任务: {task_key}")
        print(f"可用任务: {', '.join(TASKS.keys())}")
        return False

    task = TASKS[task_key]
    print(f"\n{'='*60}")
    print(f"🚀 执行任务: {task['name']}")
    print(f"📝 描述: {task['description']}")
    print(f"{'='*60}\n")

    # 执行脚本
    cmd = ["python", task["script"]] + task["args"]
    log_file = LOG_DIR / f"{task_key}.log"
    
    start_time = datetime.now()
    
    try:
        with open(log_file, "a") as f:
            f.write(f"\n{'='*60}\n")
            f.write(f"[{start_time.isoformat()}] 开始执行: {task['name']}\n")
            f.write(f"{'='*60}\n")
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd="/workspace/projects/workspace"
            )
            
            f.write(result.stdout)
            if result.stderr:
                f.write("\n[STDERR]\n")
                f.write(result.stderr)
            
            f.write(f"\n[{datetime.now().isoformat()}] 执行结束，返回码: {result.returncode}\n")
        
        # 更新状态
        state = load_state()
        if task_key not in state["tasks"]:
            state["tasks"][task_key] = {}
        
        state["tasks"][task_key].update({
            "last_run": start_time.isoformat(),
            "last_status": "success" if result.returncode == 0 else "failed",
            "last_duration": (datetime.now() - start_time).total_seconds(),
            "run_count": state["tasks"][task_key].get("run_count", 0) + 1
        })
        
        if result.returncode != 0:
            state["tasks"][task_key]["error_count"] = state["tasks"][task_key].get("error_count", 0) + 1
        
        save_state(state)
        
        if result.returncode == 0:
            print(f"✅ 任务执行成功: {task['name']}")
            return True
        else:
            print(f"❌ 任务执行失败: {task['name']}")
            print(f"📄 查看日志: {log_file}")
            return False
            
    except Exception as e:
        print(f"❌ 执行异常: {e}")
        return False


def list_tasks():
    """列出所有任务"""
    print("\n📋 可用任务列表:\n")
    print(f"{'任务ID':<20} {'任务名称':<15} {'描述'}")
    print("-" * 70)
    for key, task in TASKS.items():
        print(f"{key:<20} {task['name']:<15} {task['description']}")
    print()


def main():
    parser = argparse.ArgumentParser(description="自动化任务执行器")
    parser.add_argument("--task", "-t", help="要执行的任务ID")
    parser.add_argument("--list", "-l", action="store_true", help="列出所有任务")
    parser.add_argument("--force", "-f", action="store_true", help="强制立即执行")
    
    args = parser.parse_args()
    
    ensure_dirs()
    
    if args.list:
        list_tasks()
        return
    
    if not args.task:
        print("❌ 请指定任务ID (--task) 或使用 --list 查看所有任务")
        return
    
    success = run_task(args.task, args.force)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
