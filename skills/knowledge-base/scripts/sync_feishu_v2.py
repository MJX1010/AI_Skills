#!/usr/bin/env python3
"""
改进的飞书知识库同步工具
策略：先查询飞书 → 找到则复用 → 没找到则创建 → 更新缓存
"""

import json
import subprocess
from pathlib import Path

WORKSPACE = Path("/workspace/projects/workspace")
STATE_FILE = WORKSPACE / "memory" / "state" / "feishu-nodes-v2.json"

KB_CONFIG = {
    "ai-latest-news": {
        "name": "🤖 AI最新资讯",
        "space_id": "7616519632920251572",
        "root_token": "PhL6wlstzissQ1kKPwMc18xbngg"
    },
    "game-development": {
        "name": "🎮 游戏开发",
        "space_id": "7616735513310924004",
        "root_token": "U9EWwwL8ui16IEkrN8vcIRISnFg"
    },
    "healthy-living": {
        "name": "🌱 健康生活",
        "space_id": "7616737910330510558",
        "root_token": "XD2PwwJukiD8a8koNAAc4Fedn5t"
    }
}


def run_feishu_wiki(action, **kwargs):
    """调用飞书 wiki 工具"""
    cmd = ["openclaw", "tool", "feishu_wiki", "--action", action]
    for key, value in kwargs.items():
        cmd.extend([f"--{key}", str(value)])
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0:
        try:
            return json.loads(result.stdout)
        except:
            return {"error": "parse_failed", "raw": result.stdout}
    return {"error": result.stderr}


def find_child_node(space_id, parent_token, title):
    """查找子节点，返回匹配的节点信息"""
    result = run_feishu_wiki("nodes", space_id=space_id, parent_node_token=parent_token)
    
    if "error" in result:
        return None
    
    nodes = result.get("nodes", [])
    for node in nodes:
        if node.get("title") == title:
            return {
                "node_token": node.get("node_token"),
                "obj_token": node.get("obj_token"),
                "title": node.get("title")
            }
    
    return None


def create_node(space_id, parent_token, title, obj_type="docx"):
    """创建新节点"""
    result = run_feishu_wiki("create", 
                             space_id=space_id, 
                             parent_node_token=parent_token, 
                             title=title, 
                             obj_type=obj_type)
    
    if "error" in result:
        return None
    
    return {
        "node_token": result.get("node_token"),
        "obj_token": result.get("obj_token"),
        "title": result.get("title")
    }


def get_or_create_hierarchy(kb_key, year, month, day):
    """
    获取或创建层级节点
    策略: 先查询飞书 → 找到则复用 → 没找到则创建
    """
    if kb_key not in KB_CONFIG:
        return None
    
    config = KB_CONFIG[kb_key]
    space_id = config["space_id"]
    
    path = []
    
    # 1. 查找年份节点
    print(f"  🔍 查找年份节点: {year}年")
    year_node = find_child_node(space_id, config["root_token"], f"{year}年")
    
    if year_node:
        print(f"     ✅ 复用: {year_node['node_token'][:20]}...")
    else:
        print(f"     📝 创建新节点...")
        year_node = create_node(space_id, config["root_token"], f"{year}年")
        if not year_node:
            return None
        print(f"     ✅ 创建: {year_node['node_token'][:20]}...")
    
    path.append(("year", year_node))
    
    # 2. 查找月份节点
    month_title = f"{int(month)}月"
    print(f"  🔍 查找月份节点: {month_title}")
    month_node = find_child_node(space_id, year_node["node_token"], month_title)
    
    if month_node:
        print(f"     ✅ 复用: {month_node['node_token'][:20]}...")
    else:
        print(f"     📝 创建新节点...")
        month_node = create_node(space_id, year_node["node_token"], month_title)
        if not month_node:
            return None
        print(f"     ✅ 创建: {month_node['node_token'][:20]}...")
    
    path.append(("month", month_node))
    
    # 3. 查找日报节点
    doc_title = f"{int(month)}月{int(day)}日 日报"
    print(f"  🔍 查找日报节点: {doc_title}")
    doc_node = find_child_node(space_id, month_node["node_token"], doc_title)
    
    if doc_node:
        print(f"     ✅ 复用: {doc_node['node_token'][:20]}...")
    else:
        print(f"     📝 创建新节点...")
        doc_node = create_node(space_id, month_node["node_token"], doc_title)
        if not doc_node:
            return None
        print(f"     ✅ 创建: {doc_node['node_token'][:20]}...")
    
    path.append(("doc", doc_node))
    
    return {
        "year_node": year_node,
        "month_node": month_node,
        "doc_node": doc_node,
        "doc_token": doc_node["obj_token"]
    }


def sync_content(kb_key, content, date_str):
    """同步内容到飞书"""
    year = date_str[:4]
    month = date_str[5:7]
    day = date_str[8:10]
    
    config = KB_CONFIG[kb_key]
    print(f"\n  ☁️  同步到飞书: {config['name']}")
    
    # 获取层级节点
    hierarchy = get_or_create_hierarchy(kb_key, year, month, day)
    if not hierarchy:
        print(f"     ❌ 获取层级失败")
        return {"status": "error", "step": "hierarchy"}
    
    doc_token = hierarchy["doc_token"]
    
    # 读取现有内容
    print(f"  📖 读取文档内容...")
    result = subprocess.run(
        ["openclaw", "tool", "feishu_doc", "--action", "read", "--doc_token", doc_token],
        capture_output=True,
        text=True
    )
    
    existing = ""
    try:
        doc_data = json.loads(result.stdout)
        existing = doc_data.get("content", "")
    except:
        pass
    
    # 检查是否已存在
    title = content.split("[")[1].split("]")[0] if "[" in content else ""
    if title and title in existing:
        print(f"     ⏭️  内容已存在，跳过")
        return {"status": "skipped", "reason": "exists"}
    
    # 构建完整内容
    if not existing.strip():
        header = f"# {config['name']} - {date_str} 日报\n\n"
        full_content = header + content
    else:
        full_content = existing + "\n" + content
    
    # 写入文档
    print(f"  💾 写入文档...")
    import tempfile
    import os
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
        f.write(full_content)
        temp_file = f.name
    
    result = subprocess.run(
        ["openclaw", "tool", "feishu_doc", "--action", "write",
         "--doc_token", doc_token,
         "--file_path", temp_file],
        capture_output=True,
        text=True
    )
    
    os.unlink(temp_file)
    
    if result.returncode == 0:
        print(f"     ✅ 同步成功")
        return {"status": "success", "doc_token": doc_token}
    else:
        print(f"     ❌ 同步失败: {result.stderr[:100]}")
        return {"status": "error", "error": result.stderr}


if __name__ == "__main__":
    import sys
    
    # 测试
    test_content = """### 📺 [测试视频](https://b23.tv/test)
> 来源: Bilibili | 收集时间: 2026-03-20 08:00

---
"""
    
    result = sync_content("ai-latest-news", test_content, "2026-03-20")
    print("\n结果:", json.dumps(result, indent=2))
