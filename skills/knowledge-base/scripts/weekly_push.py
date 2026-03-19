#!/usr/bin/env python3
"""
周报推送脚本 - 推送周报到飞书知识库
使用 OpenClaw 的 feishu 工具
"""

import json
from datetime import datetime, timedelta
from pathlib import Path

# 导入 OpenClaw 的 feishu 工具
try:
    from feishu_wiki import feishu_wiki
    from feishu_doc import feishu_doc
    FEISHU_AVAILABLE = True
except ImportError:
    FEISHU_AVAILABLE = False
    print("⚠️ 飞书工具不可用，请确保 OpenClaw 环境正常")

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


def get_week_range(date=None):
    """获取本周日期范围"""
    if date is None:
        date = datetime.now()
    monday = date - timedelta(days=date.weekday())
    sunday = monday + timedelta(days=6)
    return monday, sunday


def read_weekly_content(kb: str, week_num: int, year: str) -> str:
    """读取周报内容"""
    file_path = MEMORY_DIR / "kb-archive" / kb / year / f"week-{week_num}.md"
    if file_path.exists():
        return file_path.read_text(encoding="utf-8")
    return ""


def get_or_create_node(space_id: str, parent_token: str, title: str, obj_type: str = "docx") -> str:
    """获取或创建节点"""
    if not FEISHU_AVAILABLE:
        return None
    
    try:
        # 首先尝试获取已有节点
        result = feishu_wiki(space_id=space_id, action="nodes")
        if result and "nodes" in result:
            for node in result["nodes"]:
                if node.get("title") == title:
                    print(f"    📁 使用已有节点: {title}")
                    return node.get("node_token")
        
        # 创建新节点
        result = feishu_wiki(
            space_id=space_id,
            action="create",
            parent_node_token=parent_token,
            title=title,
            obj_type=obj_type
        )
        
        if result and "node_token" in result:
            print(f"    📁 创建新节点: {title}")
            return result["node_token"]
        
        return None
    except Exception as e:
        print(f"    ⚠️ 节点操作失败: {e}")
        return None


def sync_to_feishu(kb: str, content: str, monday: datetime, sunday: datetime) -> bool:
    """同步到飞书知识库"""
    if not FEISHU_AVAILABLE:
        print(f"    ⚠️ 飞书工具不可用，跳过同步")
        return False
    
    config = KB_CONFIG[kb]
    year = monday.strftime("%Y")
    month = str(int(monday.strftime("%m")))
    week_num = monday.isocalendar()[1]
    date_range = f"{monday.strftime('%m.%d')}-{sunday.strftime('%m.%d')}"
    
    doc_title = f"第{week_num}期 - {date_range} 周报"
    
    print(f"\n  📤 同步 {config['name']} 到飞书...")
    
    try:
        # 1. 获取知识库首页
        result = feishu_wiki(space_id=config['space_id'], action="nodes")
        if not result or "nodes" not in result or not result["nodes"]:
            print(f"    ⚠️ 无法获取知识库节点")
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
        
        # 4. 检查是否已有周报文档
        existing_doc = None
        month_nodes = feishu_wiki(space_id=config['space_id'], action="nodes")
        if month_nodes and "nodes" in month_nodes:
            for node in month_nodes["nodes"]:
                if node.get("title") == doc_title:
                    existing_doc = node
                    break
        
        if existing_doc:
            doc_token = existing_doc["obj_token"]
            print(f"    📄 更新已有文档: {doc_title}")
        else:
            # 创建新文档
            doc_result = feishu_wiki(
                space_id=config['space_id'],
                action="create",
                parent_node_token=month_node,
                title=doc_title,
                obj_type="docx"
            )
            
            if not doc_result or "obj_token" not in doc_result:
                print(f"    ⚠️ 无法创建文档")
                return False
            
            doc_token = doc_result["obj_token"]
            print(f"    📄 创建新文档: {doc_title}")
        
        # 5. 写入内容
        feishu_doc(doc_token=doc_token, action="write", content=content)
        print(f"    ✅ 内容已写入")
        
        return True
        
    except Exception as e:
        print(f"    ⚠️ 同步异常: {e}")
        return False


def main():
    monday, sunday = get_week_range()
    week_num = monday.isocalendar()[1]
    year = monday.strftime("%Y")
    
    print("\n" + "="*60)
    print("📤 周报推送")
    print("="*60)
    print(f"📅 本周: {monday.strftime('%Y-%m-%d')} ~ {sunday.strftime('%Y-%m-%d')}")
    print(f"📊 第 {week_num} 周")
    print("="*60)
    
    if not FEISHU_AVAILABLE:
        print("\n  ⚠️ 飞书工具不可用")
    
    for kb in KB_CONFIG.keys():
        content = read_weekly_content(kb, week_num, year)
        
        if not content:
            print(f"\n  ⏭️  {KB_CONFIG[kb]['name']}: 无周报内容，跳过")
            continue
        
        sync_to_feishu(kb, content, monday, sunday)
    
    print("\n" + "="*60)
    print("✅ 周报推送完成!")
    print("="*60 + "\n")
    
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
