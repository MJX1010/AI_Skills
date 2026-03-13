#!/usr/bin/env python3
"""
统一内容收集器 - 同步本地周刊到飞书知识库
Usage: python sync_feishu.py --kb <kb>|--all --week <current|YYYY-WXX>
"""

import argparse
import json
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path

# 知识库配置
KB_CONFIG = {
    "ai-latest-news": {
        "name": "AI最新资讯",
        "icon": "🤖",
        "space_id": "7616519632920251572",
        "home_node": "PhL6wlstzissQ1kKPwMc18xbngg",
        "output_dir": "memory/ai-content",
        "weekly_prefix": "weekly"
    },
    "game-development": {
        "name": "游戏开发",
        "icon": "🎮",
        "space_id": "7616735513310924004",
        "home_node": "U9EWwwL8ui16IEkrN8vcIRISnFg",
        "output_dir": "memory/game-content",
        "weekly_prefix": "game-weekly"
    },
    "healthy-living": {
        "name": "健康生活",
        "icon": "🌱",
        "space_id": "7616737910330510558",
        "home_node": "XD2PwwJukiD8a8koNAAc4Fedn5t",
        "output_dir": "memory/health-content",
        "weekly_prefix": "health-weekly"
    }
}


def run_feishu_command(action, **kwargs):
    """运行飞书命令"""
    cmd = ["feishu_wiki", "--action", action]
    
    for key, value in kwargs.items():
        if value is not None:
            cmd.extend([f"--{key}", str(value)])
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0:
            try:
                return json.loads(result.stdout)
            except json.JSONDecodeError:
                return {"output": result.stdout}
        else:
            return {"error": result.stderr}
    
    except Exception as e:
        return {"error": str(e)}


def run_feishu_doc_command(action, doc_token, content):
    """运行飞书文档写入命令"""
    cmd = [
        "feishu_doc",
        "--action", action,
        "--doc_token", doc_token,
        "--content", content
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        return result.returncode == 0, result.stdout, result.stderr
    
    except Exception as e:
        return False, "", str(e)


def get_week_info(week_arg):
    """获取周信息"""
    if week_arg == "current":
        today = datetime.now()
        year = today.year
        week_num = int(today.strftime("%W")) + 1
        return f"{year}-W{week_num:02d}", year, week_num
    else:
        parts = week_arg.split("-W")
        year = int(parts[0])
        week_num = int(parts[1])
        return week_arg, year, week_num


def get_or_create_node(space_id, parent_token, title, obj_type="docx"):
    """获取或创建节点"""
    # 首先列出父节点下的子节点
    nodes_result = run_feishu_command("nodes", space_id=space_id)
    
    if "error" in nodes_result:
        return None, f"获取节点失败: {nodes_result['error']}"
    
    nodes = nodes_result.get("nodes", [])
    
    # 查找是否已存在同名节点
    for node in nodes:
        if node.get("title") == title:
            return node.get("node_token"), node.get("obj_token")
    
    # 不存在则创建
    create_result = run_feishu_command(
        "create",
        space_id=space_id,
        parent_node_token=parent_token,
        title=title,
        obj_type=obj_type
    )
    
    if "error" in create_result:
        return None, f"创建节点失败: {create_result['error']}"
    
    return create_result.get("node_token"), create_result.get("obj_token")


def sync_kb_to_feishu(kb_key, week_str, year, week_num):
    """同步单个知识库到飞书"""
    config = KB_CONFIG[kb_key]
    space_id = config["space_id"]
    
    print(f"\n{'=' * 60}")
    print(f"📚 同步知识库: {config['icon']} {config['name']}")
    print(f"🆔 Space ID: {space_id}")
    print("=" * 60)
    
    # 1. 计算日期
    jan_1 = datetime(year, 1, 1)
    week_start = jan_1 + timedelta(weeks=week_num-1, days=-jan_1.weekday())
    month = week_start.month
    day = week_start.day
    
    # 2. 读取本地周刊文件
    weekly_file = Path(f"/workspace/projects/workspace/{config['output_dir']}/weekly/{config['weekly_prefix']}-{week_str}.md")
    
    if not weekly_file.exists():
        return False, f"周刊文件不存在: {weekly_file}"
    
    with open(weekly_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print(f"📄 读取周刊: {weekly_file}")
    print(f"📊 内容长度: {len(content)} 字符")
    
    # 3. 创建层级结构（年/月/周刊）
    print(f"\n📁 创建层级结构...")
    
    # 3.1 创建年度节点
    year_title = f"{year}年"
    year_node, year_obj = get_or_create_node(space_id, config["home_node"], year_title)
    if year_node is None:
        return False, f"创建年度节点失败: {year_obj}"
    print(f"  ✅ 年度节点: {year_title} ({year_node})")
    
    # 3.2 创建月度节点
    month_title = f"{month}月"
    month_node, month_obj = get_or_create_node(space_id, year_node, month_title)
    if month_node is None:
        return False, f"创建月度节点失败: {month_obj}"
    print(f"  ✅ 月度节点: {month_title} ({month_node})")
    
    # 3.3 创建周刊文档
    weekly_title = f"第{week_num}期 - {month}月{day}日"
    weekly_node, weekly_obj = get_or_create_node(space_id, month_node, weekly_title, "docx")
    if weekly_node is None:
        return False, f"创建周刊文档失败: {weekly_obj}"
    print(f"  ✅ 周刊文档: {weekly_title} ({weekly_node})")
    
    # 4. 写入周刊内容
    print(f"\n📝 写入周刊内容...")
    success, stdout, stderr = run_feishu_doc_command("write", weekly_obj, content)
    
    if not success:
        return False, f"写入内容失败: {stderr}"
    
    print(f"  ✅ 内容写入成功")
    
    # 5. 返回结果
    result = {
        "kb": kb_key,
        "name": config["name"],
        "week": week_str,
        "week_num": week_num,
        "title": weekly_title,
        "node_token": weekly_node,
        "obj_token": weekly_obj,
        "wiki_url": f"https://xxx.feishu.cn/wiki/{weekly_node}"
    }
    
    return True, result


def main():
    parser = argparse.ArgumentParser(description="同步本地周刊到飞书知识库")
    parser.add_argument("--kb", 
                       choices=["ai-latest-news", "game-development", "healthy-living"],
                       help="目标知识库（与 --all 互斥）")
    parser.add_argument("--all", action="store_true",
                       help="同步所有知识库")
    parser.add_argument("--week", default="current",
                       help="周次 (current 或 YYYY-WXX)")
    
    args = parser.parse_args()
    
    if not args.kb and not args.all:
        parser.error("必须指定 --kb 或 --all")
    
    # 获取周信息
    week_str, year, week_num = get_week_info(args.week)
    print("=" * 60)
    print("🔄 统一内容收集器 - 飞书同步")
    print("=" * 60)
    print(f"📅 目标周次: {week_str} (第{week_num}周)")
    print()
    
    # 确定要同步的知识库
    if args.all:
        kb_list = list(KB_CONFIG.keys())
    else:
        kb_list = [args.kb]
    
    # 同步每个知识库
    results = {}
    
    for kb in kb_list:
        success, result = sync_kb_to_feishu(kb, week_str, year, week_num)
        results[kb] = {"success": success, "result": result}
        
        if success:
            print(f"\n✅ {KB_CONFIG[kb]['name']} 同步成功")
            print(f"   Wiki节点: {result['node_token']}")
            print(f"   访问链接: {result['wiki_url']}")
        else:
            print(f"\n❌ {KB_CONFIG[kb]['name']} 同步失败")
            print(f"   错误: {result}")
    
    # 汇总报告
    print("\n" + "=" * 60)
    print("📊 同步完成汇总")
    print("=" * 60)
    
    for kb in kb_list:
        config = KB_CONFIG[kb]
        status_icon = "✅" if results[kb]["success"] else "❌"
        print(f"{status_icon} {config['icon']} {config['name']}")
        
        if results[kb]["success"]:
            result = results[kb]["result"]
            print(f"   节点: {result['node_token']}")
    
    success_count = sum(1 for r in results.values() if r["success"])
    print(f"\n总计: {success_count}/{len(kb_list)} 个知识库同步成功")
    
    # 输出操作日志模板
    print("\n" + "=" * 60)
    print("📝 操作日志模板（请复制到 memory/YYYY-MM-DD.md）")
    print("=" * 60)
    print()
    print("## 内容收集与同步")
    print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print()
    print("### 同步状态")
    print("| 知识库 | 周刊期数 | Wiki节点 | 状态 |")
    print("|--------|----------|----------|------|")
    
    for kb in kb_list:
        config = KB_CONFIG[kb]
        status = "✅ 已同步" if results[kb]["success"] else "❌ 失败"
        
        if results[kb]["success"]:
            node = results[kb]["result"]["node_token"]
        else:
            node = "N/A"
        
        print(f"| {config['icon']} {config['name']} | 第{week_num}期 | `{node}` | {status} |")
    
    print()
    print("### 本地备份")
    for kb in kb_list:
        config = KB_CONFIG[kb]
        print(f"- `{config['output_dir']}/weekly/{config['weekly_prefix']}-{week_str}.md`")
    
    return 0 if success_count == len(kb_list) else 1


if __name__ == "__main__":
    sys.exit(main())
