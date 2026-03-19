#!/usr/bin/env python3
"""
清理脚本 - 删除过期的日报和周报
遵循 RULES.md 规则2：日报保留7天，周报保留30天
"""

import json
import shutil
from datetime import datetime, timedelta
from pathlib import Path

WORKSPACE = Path("/workspace/projects/workspace")
MEMORY_DIR = WORKSPACE / "memory"

# 保留策略
RETENTION = {
    "daily": 7,      # 日报保留7天
    "weekly": 30,    # 周报保留30天
    "modules": 90    # 模块归档保留90天
}


def is_expired(file_path: Path, days: int) -> bool:
    """检查文件是否过期"""
    try:
        mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
        age = datetime.now() - mtime
        return age.days > days
    except:
        return False


def cleanup_kb_archive():
    """清理知识库归档"""
    print("\n🧹 清理知识库归档...")
    
    kb_dir = MEMORY_DIR / "kb-archive"
    if not kb_dir.exists():
        print("  ℹ️ 无内容需要清理")
        return
    
    cleaned = 0
    
    for kb in kb_dir.iterdir():
        if not kb.is_dir():
            continue
        
        for year in kb.iterdir():
            if not year.is_dir():
                continue
            
            for month in year.iterdir():
                if not month.is_dir():
                    continue
                
                for file in month.iterdir():
                    if not file.is_file():
                        continue
                    
                    # 判断是日报还是周报
                    if file.name.startswith("week-"):
                        # 周报保留30天
                        if is_expired(file, RETENTION["weekly"]):
                            print(f"  🗑️  删除过期周报: {file}")
                            file.unlink()
                            cleaned += 1
                    elif file.suffix == ".md" and len(file.stem) <= 2:
                        # 日报（如 01.md, 02.md）保留7天
                        if is_expired(file, RETENTION["daily"]):
                            print(f"  🗑️  删除过期日报: {file}")
                            file.unlink()
                            cleaned += 1
    
    print(f"  ✅ 已清理 {cleaned} 个文件")


def cleanup_logs():
    """清理日志"""
    print("\n🧹 清理日志...")
    
    log_dir = MEMORY_DIR / "logs"
    if not log_dir.exists():
        print("  ℹ️ 无日志需要清理")
        return
    
    cleaned = 0
    
    for subdir in ["daily", "weekly", "sync"]:
        subdir_path = log_dir / subdir
        if not subdir_path.exists():
            continue
        
        for file in subdir_path.iterdir():
            if not file.is_file():
                continue
            
            # 日志保留30天
            if is_expired(file, 30):
                print(f"  🗑️  删除过期日志: {file.name}")
                file.unlink()
                cleaned += 1
    
    print(f"  ✅ 已清理 {cleaned} 个日志文件")


def cleanup_empty_dirs():
    """清理空目录"""
    print("\n🧹 清理空目录...")
    
    removed = 0
    
    # 从底层向上清理
    for root, dirs, files in os.walk(MEMORY_DIR, topdown=False):
        for dir_name in dirs:
            dir_path = Path(root) / dir_name
            try:
                # 只清理特定路径下的空目录
                if "kb-archive" in str(dir_path) or "logs" in str(dir_path):
                    if dir_path.exists() and not any(dir_path.iterdir()):
                        dir_path.rmdir()
                        removed += 1
            except:
                pass
    
    print(f"  ✅ 已清理 {removed} 个空目录")


def save_cleanup_log():
    """保存清理日志"""
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "retention_policy": RETENTION,
        "note": "Auto cleanup executed"
    }
    
    log_file = MEMORY_DIR / "state" / "cleanup-log.json"
    log_file.parent.mkdir(parents=True, exist_ok=True)
    
    logs = []
    if log_file.exists():
        logs = json.loads(log_file.read_text())
    
    logs.append(log_entry)
    
    # 只保留最近100条日志
    logs = logs[-100:]
    
    log_file.write_text(json.dumps(logs, indent=2))


def main():
    import os
    
    print("\n" + "="*60)
    print("🧹 内容清理")
    print("="*60)
    print(f"日报保留: {RETENTION['daily']} 天")
    print(f"周报保留: {RETENTION['weekly']} 天")
    print(f"模块保留: {RETENTION['modules']} 天")
    print("="*60)
    
    # 执行清理
    cleanup_kb_archive()
    cleanup_logs()
    cleanup_empty_dirs()
    
    # 保存日志
    save_cleanup_log()
    
    print("\n✅ 清理完成!")
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
