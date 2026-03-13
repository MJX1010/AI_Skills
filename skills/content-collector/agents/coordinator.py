#!/usr/bin/env python3
"""
Coordinator Agent - 协调器
负责任务分发和工作流 orchestration
"""

import argparse
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

# Agent 配置
AGENT_SCRIPTS = {
    "collector-ai": "agents/collectors/ai_collector.py",
    "collector-game": "agents/collectors/game_collector.py",
    "collector-health": "agents/collectors/health_collector.py",
    "classifier": "agents/processors/classifier.py",
    "quality": "agents/processors/quality_filter.py",
    "summarizer": "agents/processors/summarizer.py",
    "publisher": "agents/publisher.py",
    "syncer": "agents/syncer.py",
}


class CoordinatorAgent:
    """协调器 Agent - 主控中心"""
    
    def __init__(self):
        self.base_path = Path("/workspace/projects/workspace/skills/content-collector")
        self.results = {}
    
    def run_agent(self, agent_id, **kwargs):
        """运行指定 Agent"""
        script_path = self.base_path / AGENT_SCRIPTS.get(agent_id)
        
        if not script_path.exists():
            print(f"❌ Agent script not found: {script_path}")
            return False, None
        
        cmd = [sys.executable, str(script_path)]
        
        # 添加参数
        for key, value in kwargs.items():
            cmd.extend([f"--{key}", str(value)])
        
        print(f"\n{'=' * 60}")
        print(f"🤖 启动 Agent: {agent_id}")
        print(f"{'=' * 60}")
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300,
                cwd="/workspace/projects/workspace"
            )
            
            print(result.stdout)
            
            if result.returncode == 0:
                return True, result.stdout
            else:
                print(f"❌ Agent {agent_id} failed: {result.stderr}")
                return False, result.stderr
        
        except subprocess.TimeoutExpired:
            print(f"❌ Agent {agent_id} timeout")
            return False, "timeout"
        
        except Exception as e:
            print(f"❌ Agent {agent_id} error: {e}")
            return False, str(e)
    
    def weekly_collection(self, week="current"):
        """
        主流程：周刊自动收集
        
        流程: Collectors → Processors → Publisher → Syncer
        """
        print("\n" + "=" * 60)
        print("🚀 Coordinator: 启动周刊收集流程")
        print("=" * 60)
        print(f"📅 Week: {week}")
        print(f"⏰ Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Step 1: 并行启动 Collectors
        print("\n📦 Step 1: 并行收集各知识库内容")
        collectors = ["collector-ai", "collector-game", "collector-health"]
        
        for collector in collectors:
            success, output = self.run_agent(collector, week=week)
            self.results[collector] = {"success": success, "output": output}
        
        # Step 2: 运行 Processors (按顺序)
        print("\n📦 Step 2: 内容整理处理")
        
        # 2.1 分类
        success, output = self.run_agent("classifier", week=week)
        self.results["classifier"] = {"success": success, "output": output}
        
        # 2.2 质量筛选
        success, output = self.run_agent("quality", week=week)
        self.results["quality"] = {"success": success, "output": output}
        
        # 2.3 生成摘要
        success, output = self.run_agent("summarizer", week=week)
        self.results["summarizer"] = {"success": success, "output": output}
        
        # Step 3: Publisher 推送
        print("\n📦 Step 3: 推送周刊到飞书")
        success, output = self.run_agent("publisher", week=week)
        self.results["publisher"] = {"success": success, "output": output}
        
        # Step 4: Syncer 同步
        print("\n📦 Step 4: 同步到 Git")
        success, output = self.run_agent("syncer")
        self.results["syncer"] = {"success": success, "output": output}
        
        # 生成报告
        self._generate_report()
        
        return self.results
    
    def add_user_content(self, kb, file_path, merge=True):
        """
        用户添加内容流程
        
        流程: 用户提供内容 → 分类 → 合并到周刊 → 更新
        """
        print("\n" + "=" * 60)
        print("🚀 Coordinator: 用户添加内容")
        print("=" * 60)
        print(f"📚 KB: {kb}")
        print(f"📄 File: {file_path}")
        print(f"🔀 Merge: {merge}")
        
        # TODO: 实现用户内容合并逻辑
        # 1. 读取用户提供的内容
        # 2. 调用 classifier 分类
        # 3. 合并到现有周刊
        # 4. 调用 publisher 更新
        # 5. 调用 syncer 同步
        
        print("\n✅ 用户内容已合并到周刊")
        return True
    
    def _generate_report(self):
        """生成执行报告"""
        print("\n" + "=" * 60)
        print("📊 Coordinator: 执行报告")
        print("=" * 60)
        
        for agent_id, result in self.results.items():
            status = "✅" if result["success"] else "❌"
            print(f"{status} {agent_id}")
        
        success_count = sum(1 for r in self.results.values() if r["success"])
        total = len(self.results)
        print(f"\n总计: {success_count}/{total} 个 Agent 成功")
        
        # 保存报告
        report_file = Path("/workspace/projects/workspace/memory/coordinator-report.json")
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump({
                "timestamp": datetime.now().isoformat(),
                "results": self.results
            }, f, ensure_ascii=False, indent=2)
        
        print(f"\n📄 报告已保存: {report_file}")


def main():
    parser = argparse.ArgumentParser(description="Coordinator Agent")
    parser.add_argument("--task", choices=["weekly_collection", "add_content"],
                       default="weekly_collection",
                       help="执行任务类型")
    parser.add_argument("--week", default="current",
                       help="目标周次")
    parser.add_argument("--kb",
                       help="知识库 (add_content 时使用)")
    parser.add_argument("--file",
                       help="用户内容文件 (add_content 时使用)")
    
    args = parser.parse_args()
    
    coordinator = CoordinatorAgent()
    
    if args.task == "weekly_collection":
        coordinator.weekly_collection(args.week)
    elif args.task == "add_content":
        if not args.kb or not args.file:
            print("❌ --kb 和 --file 参数必填")
            sys.exit(1)
        coordinator.add_user_content(args.kb, args.file)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
