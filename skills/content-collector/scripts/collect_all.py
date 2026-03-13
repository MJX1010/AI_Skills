#!/usr/bin/env python3
"""
统一内容收集器 - 批量收集所有知识库内容
Usage: python collect_all.py --week <current|YYYY-WXX>
"""

import argparse
import subprocess
import sys
from datetime import datetime

# 知识库列表
KNOWLEDGE_BASES = [
    "ai-latest-news",
    "game-development", 
    "healthy-living"
]

KB_NAMES = {
    "ai-latest-news": "🤖 AI最新资讯",
    "game-development": "🎮 游戏开发",
    "healthy-living": "🌱 健康生活"
}


def main():
    parser = argparse.ArgumentParser(description="批量收集所有知识库内容")
    parser.add_argument("--week", default="current",
                       help="周次 (current 或 YYYY-WXX)")
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("🔄 统一内容收集器 - 批量收集模式")
    print("=" * 60)
    print(f"📅 目标周次: {args.week}")
    print()
    
    results = {}
    
    for kb in KNOWLEDGE_BASES:
        print(f"\n{'=' * 60}")
        print(f"📚 正在收集: {KB_NAMES[kb]}")
        print("=" * 60)
        
        # 调用 collect.py 收集单个知识库
        cmd = [
            sys.executable,
            "skills/content-collector/scripts/collect.py",
            "--kb", kb,
            "--week", args.week
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                print(result.stdout)
                results[kb] = {"status": "success", "output": result.stdout}
            else:
                print(f"❌ 收集失败:")
                print(result.stderr)
                results[kb] = {"status": "failed", "error": result.stderr}
        
        except subprocess.TimeoutExpired:
            print(f"❌ 收集超时")
            results[kb] = {"status": "timeout"}
        
        except Exception as e:
            print(f"❌ 收集异常: {e}")
            results[kb] = {"status": "error", "error": str(e)}
    
    # 汇总报告
    print("\n" + "=" * 60)
    print("📊 收集完成汇总")
    print("=" * 60)
    
    for kb in KNOWLEDGE_BASES:
        status_icon = "✅" if results[kb]["status"] == "success" else "❌"
        print(f"{status_icon} {KB_NAMES[kb]}: {results[kb]['status']}")
    
    # 统计成功数
    success_count = sum(1 for r in results.values() if r["status"] == "success")
    print(f"\n总计: {success_count}/{len(KNOWLEDGE_BASES)} 个知识库收集成功")
    
    print("\n💡 提示: 使用 sync_feishu.py 同步到飞书知识库")
    
    return 0 if success_count == len(KNOWLEDGE_BASES) else 1


if __name__ == "__main__":
    sys.exit(main())
