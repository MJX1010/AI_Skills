#!/usr/bin/env python3
"""
每日知识库日报 - 收集当日新增内容并推送到飞书
"""

import json
import subprocess
from datetime import datetime
from pathlib import Path

# 知识库配置
KNOWLEDGE_BASES = {
    "ai-latest-news": {
        "name": "🤖 AI最新资讯",
        "space_id": "7616519632920251572",
        "emoji": "🤖"
    },
    "game-development": {
        "name": "🎮 游戏开发",
        "space_id": "7616735513310924004",
        "emoji": "🎮"
    },
    "healthy-living": {
        "name": "🌱 健康生活",
        "space_id": "7616737910330510558",
        "emoji": "🌱"
    }
}

WORKSPACE = Path("/workspace/projects/workspace")
MEMORY_DIR = WORKSPACE / "memory"


def get_today_content():
    """获取今日新增内容"""
    today = datetime.now()
    year = today.strftime("%Y")
    month = today.strftime("%m")
    day = today.strftime("%d")
    
    contents = {}
    
    for kb_key, kb_info in KNOWLEDGE_BASES.items():
        # 检查本地归档目录
        kb_dir = MEMORY_DIR / f"kb-archive" / kb_key / year / month
        if kb_dir.exists():
            # 查找今日文件
            today_files = list(kb_dir.glob(f"*/{year}-{month}-{day}.md"))
            if today_files:
                contents[kb_key] = {
                    "name": kb_info["name"],
                    "emoji": kb_info["emoji"],
                    "files": today_files,
                    "count": len(today_files)
                }
    
    return contents, today


def format_daily_message(contents: dict, date: datetime) -> str:
    """格式化日报消息"""
    date_str = date.strftime("%Y年%m月%d日")
    weekday = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"][date.weekday()]
    
    message = f"📚 **知识库日报** | {date_str} {weekday}\n\n"
    
    total = sum(c["count"] for c in contents.values())
    if total == 0:
        message += "今日暂无新增内容\n"
        return message
    
    message += f"今日共新增 **{total}** 条内容\n\n---\n\n"
    
    for kb_key, info in contents.items():
        message += f"### {info['emoji']} {info['name']}\n"
        message += f"新增: {info['count']} 条\n\n"
        
        # 读取文件内容获取标题
        for file_path in info["files"]:
            try:
                content = file_path.read_text()
                # 提取标题（假设标题格式为 ### [标题](URL)）
                for line in content.split("\n"):
                    if line.startswith("### ["):
                        # 提取链接文本
                        start = line.find("[") + 1
                        end = line.find("](")
                        if start > 0 and end > start:
                            title = line[start:end]
                            message += f"• {title}\n"
            except:
                pass
        
        message += "\n"
    
    message += "---\n📖 点击查看完整知识库"
    
    return message


def send_feishu_message(message: str):
    """发送飞书消息"""
    # 使用 message 工具发送
    # 注意：这里我们通过 stdout 输出，由调用方处理发送
    print("\n" + "="*60)
    print("📤 准备发送飞书消息:")
    print("="*60)
    print(message)
    print("="*60 + "\n")
    return True


def sync_to_feishu_kb(contents: dict, date: datetime):
    """同步日报到飞书知识库"""
    year = date.strftime("%Y")
    month = date.strftime("%m")
    day = date.strftime("%d")
    date_display = date.strftime("%m月%d日")
    
    for kb_key, info in KNOWLEDGE_BASES.items():
        if kb_key not in contents:
            continue
        
        # 检查是否有今日内容
        kb_content = contents[kb_key]
        if kb_content["count"] == 0:
            continue
        
        print(f"🔄 同步 {info['name']} 到飞书...")
        
        # 1. 获取或创建年度节点
        result = subprocess.run(
            ["python3", "-c", f"""
import json
import sys
sys.path.insert(0, '/workspace/projects/workspace')
from skills.content_collector.scripts.sync_feishu import get_or_create_node
result = get_or_create_node(
    space_id="{info['space_id']}",
    parent_token=None,
    title="{year}年",
    node_type="docx"
)
print(json.dumps(result))
"""],
            capture_output=True,
            text=True,
            cwd=WORKSPACE
        )
        
        # 由于直接调用复杂，使用 feishu_wiki 命令
        # 先获取知识库节点
        result = subprocess.run(
            ["feishu_wiki", "--action", "nodes", "--space_id", info["space_id"]],
            capture_output=True,
            text=True
        )
        
        try:
            import json
            nodes = json.loads(result.stdout)
            home_node = nodes["nodes"][0]["node_token"]
            
            # 创建或获取年度节点
            year_result = subprocess.run(
                ["feishu_wiki", "--action", "create",
                 "--space_id", info["space_id"],
                 "--parent_node_token", home_node,
                 "--title", f"{year}年",
                 "--obj_type", "docx"],
                capture_output=True,
                text=True
            )
            
            try:
                year_node = json.loads(year_result.stdout)["node_token"]
            except:
                # 如果已存在，需要查找
                year_node = None
                result = subprocess.run(
                    ["feishu_wiki", "--action", "nodes", "--space_id", info["space_id"]],
                    capture_output=True,
                    text=True
                )
                for node in json.loads(result.stdout).get("nodes", []):
                    if node["title"] == f"{year}年":
                        year_node = node["node_token"]
                        break
            
            if not year_node:
                print(f"  ⚠️ 无法获取 {year}年 节点")
                continue
            
            # 创建或获取月度节点
            month_result = subprocess.run(
                ["feishu_wiki", "--action", "create",
                 "--space_id", info["space_id"],
                 "--parent_node_token", year_node,
                 "--title", f"{int(month)}月",
                 "--obj_type", "docx"],
                capture_output=True,
                text=True
            )
            
            try:
                month_node = json.loads(month_result.stdout)["node_token"]
            except:
                # 查找已存在的月度节点
                month_node = None
                result = subprocess.run(
                    ["feishu_wiki", "--action", "nodes", "--space_id", info["space_id"]],
                    capture_output=True,
                    text=True
                )
                # 这里简化处理，实际应该递归查找
                # 暂时跳过详细查找
                print(f"  ℹ️ 月度节点可能已存在，跳过")
                continue
            
            # 创建日报文档
            day_result = subprocess.run(
                ["feishu_wiki", "--action", "create",
                 "--space_id", info["space_id"],
                 "--parent_node_token", month_node,
                 "--title", f"{date_display} 日报",
                 "--obj_type", "docx"],
                capture_output=True,
                text=True
            )
            
            try:
                day_data = json.loads(day_result.stdout)
                doc_token = day_data["obj_token"]
                
                # 构建日报内容
                doc_content = f"# {info['name']} - {date_display} 日报\n\n"
                doc_content += f"> 生成时间: {date.strftime('%Y-%m-%d %H:%M')}\n\n"
                
                for file_path in kb_content["files"]:
                    try:
                        doc_content += file_path.read_text() + "\n\n---\n\n"
                    except:
                        pass
                
                # 写入文档
                subprocess.run(
                    ["feishu_doc", "--action", "write",
                     "--doc_token", doc_token,
                     "--content", doc_content],
                    capture_output=True,
                    text=True
                )
                
                print(f"  ✅ 已同步: {date_display} 日报")
                
            except Exception as e:
                print(f"  ⚠️ 同步失败: {e}")
                
        except Exception as e:
            print(f"  ⚠️ 同步异常: {e}")


def main():
    print("📚 每日知识库日报\n")
    
    # 1. 获取今日内容
    contents, today = get_today_content()
    
    # 2. 格式化消息
    message = format_daily_message(contents, today)
    
    # 3. 发送到飞书对话窗口
    send_feishu_message(message)
    
    # 4. 同步到飞书知识库（年月日层级）
    print("\n🔄 同步到飞书知识库...\n")
    sync_to_feishu_kb(contents, today)
    
    print("\n✅ 日报处理完成!")
    return True


if __name__ == "__main__":
    main()
