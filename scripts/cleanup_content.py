#!/usr/bin/env python3
"""
自动清理旧内容文件
保留策略：
- 日报：最近7天
- 周刊：最近30天
Usage: python cleanup_content.py [--dry-run]
"""

import argparse
import os
import yaml
from datetime import datetime, timedelta
from pathlib import Path

# 内容目录
CONTENT_DIRS = [
    ("memory/ai-content/daily", 7),
    ("memory/ai-content/weekly", 30),
    ("memory/game-content/daily", 7),
    ("memory/game-content/weekly", 30),
    ("memory/health-content/daily", 7),
    ("memory/health-content/weekly", 30),
]


def load_retention_config():
    """加载保留策略配置"""
    config_path = Path("/workspace/projects/workspace/config/retention_policy.yaml")
    if config_path.exists():
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f) or {}
    return {}


def cleanup_directory(dir_path, retention_days, dry_run=False):
    """清理指定目录的旧文件"""
    base_path = Path("/workspace/projects/workspace")
    target_dir = base_path / dir_path
    
    if not target_dir.exists():
        print(f"  ⏭️  目录不存在: {dir_path}")
        return 0, 0
    
    cutoff_date = datetime.now() - timedelta(days=retention_days)
    deleted_count = 0
    kept_count = 0
    
    for file_path in target_dir.iterdir():
        if not file_path.is_file():
            continue
        
        # 获取文件修改时间
        try:
            mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
            
            if mtime < cutoff_date:
                # 文件太旧，需要删除
                if dry_run:
                    print(f"  🗑️  [预览] 将删除: {file_path.name} ({mtime.strftime('%Y-%m-%d')})")
                else:
                    file_path.unlink()
                    print(f"  🗑️  已删除: {file_path.name} ({mtime.strftime('%Y-%m-%d')})")
                deleted_count += 1
            else:
                kept_count += 1
        except Exception as e:
            print(f"  ⚠️  处理失败 {file_path.name}: {e}")
    
    return deleted_count, kept_count


def cleanup_empty_dirs(dry_run=False):
    """清理空目录"""
    base_path = Path("/workspace/projects/workspace/memory")
    removed_dirs = []
    
    for content_type in ["ai-content", "game-content", "health-content"]:
        content_path = base_path / content_type
        if not content_path.exists():
            continue
        
        for subdir in ["daily", "weekly"]:
            subdir_path = content_path / subdir
            if not subdir_path.exists():
                continue
            
            # 检查是否为空目录
            try:
                if not any(subdir_path.iterdir()):
                    if dry_run:
                        print(f"  📂 [预览] 将删除空目录: {subdir_path}")
                    else:
                        subdir_path.rmdir()
                        print(f"  📂 已删除空目录: {subdir_path}")
                    removed_dirs.append(str(subdir_path))
            except Exception as e:
                print(f"  ⚠️  删除目录失败 {subdir_path}: {e}")
    
    return removed_dirs


def main():
    parser = argparse.ArgumentParser(description="清理旧内容文件")
    parser.add_argument("--dry-run", action="store_true",
                       help="预览模式，不实际删除")
    parser.add_argument("--skip-empty-dirs", action="store_true",
                       help="跳过空目录清理")
    
    args = parser.parse_args()
    
    config = load_retention_config()
    
    print("=" * 60)
    print("🧹 内容文件清理")
    print("=" * 60)
    
    if args.dry_run:
        print("🔍 预览模式（不会实际删除文件）")
    print()
    
    total_deleted = 0
    total_kept = 0
    
    # 清理各目录
    for dir_path, retention_days in CONTENT_DIRS:
        dir_name = dir_path.split('/')[-2] + '/' + dir_path.split('/')[-1]
        print(f"\n📁 {dir_name} (保留{retention_days}天)")
        print("-" * 40)
        
        deleted, kept = cleanup_directory(dir_path, retention_days, args.dry_run)
        total_deleted += deleted
        total_kept += kept
        
        print(f"   删除: {deleted}个 | 保留: {kept}个")
    
    # 清理空目录
    if not args.skip_empty_dirs and not args.dry_run:
        print("\n📂 清理空目录")
        print("-" * 40)
        removed = cleanup_empty_dirs(args.dry_run)
        if removed:
            print(f"   已删除 {len(removed)} 个空目录")
        else:
            print("   没有空目录需要清理")
    
    # 汇总
    print("\n" + "=" * 60)
    print("📊 清理完成汇总")
    print("=" * 60)
    print(f"🗑️  删除文件: {total_deleted}个")
    print(f"📄 保留文件: {total_kept}个")
    
    if args.dry_run:
        print("\n💡 这是预览模式，实际删除请去掉 --dry-run 参数")
    
    print("=" * 60)
    
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
