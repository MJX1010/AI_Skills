#!/usr/bin/env python3
"""
日报推送脚本 - 推送日报到飞书知识库
使用 OpenClaw 命令行工具
"""

import argparse
import json
import subprocess
from datetime import datetime
from pathlib import Path

WORKSPACE = Path("/workspace/projects/workspace")
MEMORY_DIR = WORKSPACE / "memory"

KB_CONFIG = {
    "ai-latest-news": {
        "name": "🤖 AI最新资讯",
        "space_id": "7616519632920251572"
    },
    "game-development": {
        "name": "🎮 游戏开发",
        "space_id": "7616735513310924004"
    },
    "healthy-living": {
        "name": "🌱 健康生活",
        "space_id": "7616737910330510558"
    }
}


def run_openclaw_tool(tool: str, **kwargs) -> dict:
    """运行 OpenClaw 工具"""
    cmd = ["openclaw", tool]
    for key, value in kwargs.items():
        cmd.extend([f"--{key}", str(value)])
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode == 0:
            # 尝试解析 JSON 输出
            try:
                # 找到 JSON 部分（通常在输出末尾）
                lines = result.stdout.strip().split("\n")
                for line in reversed(lines):
                    line = line.strip()
                    if line and line.startswith("{"):
                        return json.loads(line)
                return {"success": True, "output": result.stdout}
            except:
                return {"success": True, "output": result.stdout}
        else:
            return {"success": False, "error": result.stderr}
    except Exception as e:
        return {"success": False, "error": str(e)}


def read_daily_content(kb: str, date_str: str) -> str:
    """读取日报内容"""
    year = date_str[:4]
    month = date_str[5:7]
    day = date_str[8:10]
    
    file_path = MEMORY_DIR / "kb-archive" / kb / year / month / f"{day}.md"
    
    if file_path.exists():
        return file_path.read_text(encoding="utf-8")
    return ""


def count_articles(content: str) -> int:
    """统计文章数量"""
    return content.count("### [")


def get_or_create_node(space_id: str, parent_token: str, title: str) -> str:
    """获取或创建节点"""
    # 首先尝试列出节点查找已有节点
    result = run_openclaw_tool("feishu_wiki", action="nodes", space_id=space_id)
    
    if result.get("success") and "nodes" in result:
        for node in result["nodes"]:
            if node.get("title") == title:
                print(f"    📁 使用已有节点: {title}")
                return node.get("node_token")
    
    # 创建新节点
    result = run_openclaw_tool(
        "feishu_wiki",
        action="create",
        space_id=space_id,
        parent_node_token=parent_token,
        title=title,
        obj_type="docx"
    )
    
    if result.get("success") and "node_token" in result:
        print(f"    📁 创建新节点: {title}")
        return result["node_token"]
    
    return None


def sync_to_feishu(kb: str, content: str, date_str: str) -> bool:
    """同步到飞书知识库"""
    config = KB_CONFIG[kb]
    year = date_str[:4]
    month = str(int(date_str[5:7]))
    day = date_str[8:10]
    
    doc_title = f"{int(month)}月{int(day)}日 日报"
    
    print(f"\n  📤 同步 {config['name']} 到飞书...")
    
    # 1. 获取知识库首页
    result = run_openclaw_tool("feishu_wiki", action="nodes", space_id=config['space_id'])
    if not result.get("success") or "nodes" not in result or not result["nodes"]:
        print(f"    ⚠️ 无法获取知识库节点: {result.get('error', '未知错误')}")
        return False
    
    home_node = result["nodes"][0]["node_token"]
    
    # 2. 获取或创建年度节点
    year_node = get_or_create_node(config['space_id'], home_node, f"{year}年")
    if not year_node:
        print(f"    ⚠️ 无法获取年度节点")
        return False
    
    # 3. 获取或创建月度节点
    month_node = get_or_create_node(config['space_id'], year_node, f"{month}月")
    if not month_node:
        print(f"    ⚠️ 无法获取月度节点")
        return False
    
    # 4. 创建日报文档
    result = run_openclaw_tool(
        "feishu_wiki",
        action="create",
        space_id=config['space_id'],
        parent_node_token=month_node,
        title=doc_title,
        obj_type="docx"
    )
    
    if not result.get("success"):
        # 可能是已存在，尝试查找
        result = run_openclaw_tool("feishu_wiki", action="nodes", space_id=config['space_id'])
        if result.get("success") and "nodes" in result:
            for node in result["nodes"]:
                if node.get("title") == doc_title:
                    doc_token = node["obj_token"]
                    print(f"    📄 更新已有文档: {doc_title}")
                    break
            else:
                print(f"    ⚠️ 无法创建文档: {result.get('error', '未知错误')}")
                return False
        else:
            print(f"    ⚠️ 无法创建文档: {result.get('error', '未知错误')}")
            return False
    else:
        doc_token = result["obj_token"]
        print(f"    📄 创建新文档: {doc_title}")
    
    # 5. 写入内容
    result = run_openclaw_tool(
        "feishu_doc",
        action="write",
        doc_token=doc_token,
        content=content
    )
    
    if result.get("success"):
        print(f"    ✅ 内容已写入")
        return True
    else:
        print(f"    ⚠️ 写入失败: {result.get('error', '未知错误')}")
        return False


def generate_push_message(date_str: str, stats: dict) -> str:
    """生成推送消息"""
    date_obj = datetime.strptime(date_str, "%Y-%m-%d")
    weekday = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"][date_obj.weekday()]
    
    message = f"📚 **知识库日报** | {date_str} {weekday}\n\n"
    
    total = sum(s["count"] for s in stats.values())
    if total == 0:
        message += "今日暂无新增内容\n"
        return message
    
    message += f"今日共新增 **{total}** 条内容\n\n---\n\n"
    
    for kb, info in stats.items():
        if info["count"] > 0:
            message += f"{info['name']}: {info['count']} 条\n"
    
    message += "\n---\n📖 点击查看完整知识库"
    
    return message


def main():
    date_str = datetime.now().strftime("%Y-%m-%d")
    
    print("\n" + "="*60)
    print("📤 日报推送")
    print("="*60)
    print(f"📅 日期: {date_str}")
    print("="*60)
    
    stats = {}
    
    # 推送每个知识库
    for kb in KB_CONFIG.keys():
        content = read_daily_content(kb, date_str)
        count = count_articles(content)
        stats[kb] = {
            "name": KB_CONFIG[kb]["name"],
            "count": count
        }
        
        if count > 0:
            sync_to_feishu(kb, content, date_str)
        else:
            print(f"\n  ⏭️  {KB_CONFIG[kb]['name']}: 无内容，跳过")
    
    # 生成推送消息
    message = generate_push_message(date_str, stats)
    
    print("\n" + "="*60)
    print("📱 推送消息内容:")
    print("="*60)
    print(message)
    print("="*60)
    
    # 保存推送记录
    push_dir = MEMORY_DIR / "daily-push"
    push_dir.mkdir(parents=True, exist_ok=True)
    push_file = push_dir / f"{date_str}.json"
    push_file.write_text(json.dumps({
        "date": date_str,
        "stats": stats,
        "message": message,
        "pushed_at": datetime.now().isoformat()
    }, indent=2, ensure_ascii=False), encoding="utf-8")
    
    print(f"\n✅ 推送记录已保存: {push_file}")
    return 0


if __name__ == "__main__":
    main()
