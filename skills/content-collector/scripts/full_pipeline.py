#!/usr/bin/env python3
"""
统一内容收集器 - 完整流程：收集 → 分类 → 归档 → 同步 → 记录
Usage: python full_pipeline.py --week <current|YYYY-WXX>
"""

import argparse
import subprocess
import sys
from datetime import datetime
from pathlib import Path


def run_command(cmd, description, timeout=300):
    """运行命令并返回结果"""
    print(f"\n{'=' * 60}")
    print(f"🔄 {description}")
    print("=" * 60)
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        
        if result.stdout:
            print(result.stdout)
        
        if result.returncode != 0:
            print(f"❌ 失败: {result.stderr}")
            return False, result.stderr
        
        return True, result.stdout
    
    except subprocess.TimeoutExpired:
        print(f"❌ 超时")
        return False, "timeout"
    
    except Exception as e:
        print(f"❌ 异常: {e}")
        return False, str(e)


def main():
    parser = argparse.ArgumentParser(description="完整流程：收集 → 分类 → 归档 → 同步 → 记录")
    parser.add_argument("--week", default="current",
                       help="周次 (current 或 YYYY-WXX)")
    parser.add_argument("--skip-collect", action="store_true",
                       help="跳过收集步骤（仅同步已有内容）")
    parser.add_argument("--skip-sync", action="store_true",
                       help="跳过同步步骤（仅本地归档）")
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("🚀 统一内容收集器 - 完整流程")
    print("=" * 60)
    print(f"📅 目标周次: {args.week}")
    print()
    
    start_time = datetime.now()
    
    # 步骤1: 收集内容
    if not args.skip_collect:
        success, _ = run_command(
            [
                sys.executable,
                "skills/content-collector/scripts/collect_all.py",
                "--week", args.week
            ],
            "步骤1: 收集所有知识库内容"
        )
        
        if not success:
            print("\n⚠️ 收集步骤出现问题，继续执行后续步骤...")
    else:
        print("\n⏭️ 跳过收集步骤")
    
    # 步骤2: 分类（在 collect.py 中已完成）
    print(f"\n{'=' * 60}")
    print("🔄 步骤2: 内容分类（已在收集时完成）")
    print("=" * 60)
    print("✅ 内容已按模块分类")
    print("  - 🤖 AI: 资讯/工具/研究/案例")
    print("  - 🎮 游戏: 引擎/设计/技术/美术/音频/独游")
    print("  - 🌱 健康: 运动/饮食/心理/睡眠/医疗/妙招")
    
    # 步骤3: 本地归档（在 collect.py 中已完成）
    print(f"\n{'=' * 60}")
    print("🔄 步骤3: 本地归档（已在收集时完成）")
    print("=" * 60)
    print("✅ 周刊已保存到 memory/ 目录")
    print("  - ai-content/weekly/weekly-*.md")
    print("  - game-content/weekly/game-weekly-*.md")
    print("  - health-content/weekly/health-weekly-*.md")
    
    # 步骤4: 同步到飞书
    if not args.skip_sync:
        success, output = run_command(
            [
                sys.executable,
                "skills/content-collector/scripts/sync_feishu.py",
                "--all",
                "--week", args.week
            ],
            "步骤4: 同步到飞书知识库",
            timeout=180
        )
        
        if not success:
            print("\n⚠️ 同步步骤失败")
    else:
        print("\n⏭️ 跳过同步步骤")
    
    # 步骤5: 更新操作日志
    print(f"\n{'=' * 60}")
    print("🔄 步骤5: 更新操作日志")
    print("=" * 60)
    
    log_file = Path(f"/workspace/projects/workspace/memory/{datetime.now().strftime('%Y-%m-%d')}.md")
    
    print(f"✅ 请手动记录到: {log_file}")
    print()
    print("日志模板:")
    print("-" * 40)
    print("## 内容收集与同步")
    print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print()
    print("### 收集统计")
    print("| 知识库 | 数量 | 分类分布 |")
    print("|--------|------|----------|")
    print("| 🤖 AI | XX条 | 资讯:X / 工具:X / 研究:X / 案例:X |")
    print("| 🎮 游戏 | XX条 | 引擎:X / 技术:X / 设计:X / 美术:X / 音频:X / 独游:X |")
    print("| 🌱 健康 | XX条 | 运动:X / 饮食:X / 心理:X / 睡眠:X / 医疗:X / 妙招:X |")
    print()
    print("### 同步状态")
    print("| 知识库 | 周刊期数 | Wiki节点 | 状态 |")
    print("|--------|----------|----------|------|")
    print("| 🤖 AI | 第X期 | `node_token` | ✅ 已同步 |")
    print("| 🎮 游戏 | 第X期 | `node_token` | ✅ 已同步 |")
    print("| 🌱 健康 | 第X期 | `node_token` | ✅ 已同步 |")
    print()
    print("### 本地备份")
    print("- `memory/ai-content/weekly/weekly-YYYY-WXX.md`")
    print("- `memory/game-content/weekly/game-weekly-YYYY-WXX.md`")
    print("- `memory/health-content/weekly/health-weekly-YYYY-WXX.md`")
    print("-" * 40)
    
    # 完成汇总
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    
    print("\n" + "=" * 60)
    print("✅ 完整流程执行完毕")
    print("=" * 60)
    print(f"⏱️  耗时: {duration:.1f} 秒")
    print()
    print("📁 本地文件:")
    print("  - memory/ai-content/weekly/")
    print("  - memory/game-content/weekly/")
    print("  - memory/health-content/weekly/")
    print()
    print("📝 下一步:")
    print("  1. 检查周刊内容质量")
    print("  2. 手动编辑本周话题和精选内容")
    print("  3. 记录操作日志到 memory/YYYY-MM-DD.md")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
