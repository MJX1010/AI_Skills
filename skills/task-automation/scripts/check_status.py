#!/usr/bin/env python3
"""
任务状态检查器 - 查看自动化任务的执行状态
"""

import argparse
import json
from datetime import datetime
from pathlib import Path

STATE_FILE = Path("memory/task-automation/state.json")
LOG_DIR = Path("memory/task-automation/logs")

TASK_NAMES = {
    "weekly_collection": "周刊收集",
    "daily_digest": "知识库日报",
    "weekly_push": "周刊推送",
    "skills_maintenance": "Skills维护",
    "openclaw_update": "OpenClaw更新检查",
    "git_sync": "Git同步"
}


def load_state():
    """加载任务状态"""
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text())
    return {"tasks": {}}


def format_time(iso_time: str) -> str:
    """格式化时间"""
    if not iso_time:
        return "从未"
    try:
        dt = datetime.fromisoformat(iso_time.replace("Z", "+00:00"))
        return dt.strftime("%Y-%m-%d %H:%M")
    except:
        return iso_time


def get_time_diff(iso_time: str) -> str:
    """获取时间差"""
    if not iso_time:
        return ""
    try:
        dt = datetime.fromisoformat(iso_time.replace("Z", "+00:00"))
        now = datetime.now(dt.tzinfo)
        diff = now - dt
        
        if diff.days > 0:
            return f"({diff.days}天前)"
        hours = diff.seconds // 3600
        if hours > 0:
            return f"({hours}小时前)"
        minutes = diff.seconds // 60
        return f"({minutes}分钟前)"
    except:
        return ""


def print_status_all():
    """打印所有任务状态"""
    state = load_state()
    tasks = state.get("tasks", {})
    
    print("\n📊 任务执行状态\n")
    print(f"{'任务名称':<18} {'最后执行':<18} {'状态':<8} {'运行次数':<8} {'错误次数'}")
    print("-" * 75)
    
    for task_id, name in TASK_NAMES.items():
        task = tasks.get(task_id, {})
        last_run = format_time(task.get("last_run", ""))
        time_diff = get_time_diff(task.get("last_run", ""))
        status = task.get("last_status", "未执行")
        
        # 状态颜色标记
        if status == "success":
            status = "✅ 成功"
        elif status == "failed":
            status = "❌ 失败"
        else:
            status = "⏳ 未执行"
        
        run_count = task.get("run_count", 0)
        error_count = task.get("error_count", 0)
        
        print(f"{name:<15} {last_run:<12} {time_diff:<8} {status:<10} {run_count:<8} {error_count}")
    
    print()


def print_task_detail(task_id: str):
    """打印单个任务详情"""
    state = load_state()
    tasks = state.get("tasks", {})
    
    if task_id not in tasks:
        print(f"\n⚠️ 任务 '{task_id}' 暂无执行记录\n")
        return
    
    task = tasks[task_id]
    name = TASK_NAMES.get(task_id, task_id)
    
    print(f"\n📋 任务详情: {name}\n")
    print(f"  任务ID: {task_id}")
    print(f"  最后执行: {format_time(task.get('last_run', ''))}")
    print(f"  执行状态: {task.get('last_status', '未执行')}")
    print(f"  执行时长: {task.get('last_duration', 0):.2f} 秒")
    print(f"  总运行次数: {task.get('run_count', 0)}")
    print(f"  总错误次数: {task.get('error_count', 0)}")
    
    # 读取最近日志
    log_file = LOG_DIR / f"{task_id}.log"
    if log_file.exists():
        print(f"\n  📄 最近日志:\n")
        try:
            lines = log_file.read_text().split("\n")
            # 显示最后20行
            for line in lines[-20:]:
                if line.strip():
                    print(f"    {line}")
        except Exception as e:
            print(f"    读取日志失败: {e}")
    
    print()


def main():
    parser = argparse.ArgumentParser(description="任务状态检查器")
    parser.add_argument("--all", "-a", action="store_true", help="显示所有任务状态")
    parser.add_argument("--task", "-t", help="查看指定任务详情")
    
    args = parser.parse_args()
    
    if args.all:
        print_status_all()
    elif args.task:
        print_task_detail(args.task)
    else:
        print_status_all()


if __name__ == "__main__":
    main()
