#!/usr/bin/env python3
"""
链接归档 + 即时飞书同步
确保复用已有节点，避免重复创建
"""

import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

WORKSPACE = Path("/workspace/projects/workspace")
STATE_DIR = WORKSPACE / "memory" / "state"
STATE_FILE = STATE_DIR / "feishu-nodes.json"

KB_CONFIG = {
    "ai-latest-news": {
        "name": "🤖 AI最新资讯",
        "space_id": "7616519632920251572",
        "parent_token": "PhL6wlstzissQ1kKPwMc18xbngg"
    },
    "game-development": {
        "name": "🎮 游戏开发",
        "space_id": "7616735513310924004",
        "parent_token": "U9EWwwL8ui16IEkrN8vcIRISnFg"
    },
    "healthy-living": {
        "name": "🌱 健康生活",
        "space_id": "7616737910330510558",
        "parent_token": "XD2PwwJukiD8a8koNAAc4Fedn5t"
    }
}


def load_state():
    """加载状态"""
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text())
    return {kb: {"nodes": {}} for kb in KB_CONFIG}


def save_state(state):
    """保存状态"""
    STATE_FILE.write_text(json.dumps(state, indent=2))


def get_or_create_node(space_id, parent_token, title, kb_key, path_key):
    """获取或创建节点，优先从缓存读取"""
    state = load_state()
    
    # 检查缓存
    if path_key in state.get(kb_key, {}).get("nodes", {}):
        print(f"  [缓存] 复用节点: {title}")
        return state[kb_key]["nodes"][path_key]
    
    # 创建新节点
    print(f"  [创建] 新节点: {title}")
    result = subprocess.run(
        ["openclaw", "tool", "feishu_wiki", "--action", "create",
         "--space_id", space_id,
         "--parent_node_token", parent_token,
         "--title", title,
         "--obj_type", "docx"],
        capture_output=True,
        text=True
    )
    
    try:
        node_data = json.loads(result.stdout)
        node_info = {
            "node_token": node_data.get("node_token"),
            "obj_token": node_data.get("obj_token")
        }
        
        # 保存到缓存
        if kb_key not in state:
            state[kb_key] = {"nodes": {}}
        state[kb_key]["nodes"][path_key] = node_info
        save_state(state)
        
        return node_info
    except:
        print(f"  [错误] 创建节点失败: {result.stderr}")
        return None


def sync_to_feishu(kb, content_entry, date_str):
    """同步到飞书"""
    year = date_str[:4]
    month = date_str[5:7]
    day = date_str[8:10]
    
    kb_config = KB_CONFIG[kb]
    space_id = kb_config["space_id"]
    parent_token = kb_config["parent_token"]
    
    print(f"\n  ☁️  同步到飞书: {kb_config['name']}")
    
    # 1. 获取/创建年份节点
    year_node = get_or_create_node(space_id, parent_token, f"{year}年", kb, f"{year}年")
    if not year_node:
        return {"status": "error", "step": "year"}
    
    # 2. 获取/创建月份节点
    month_node = get_or_create_node(space_id, year_node["node_token"], f"{int(month)}月", kb, f"{year}年/{int(month)}月")
    if not month_node:
        return {"status": "error", "step": "month"}
    
    # 3. 获取/创建日报节点
    doc_title = f"{int(month)}月{int(day)}日 日报"
    doc_node = get_or_create_node(space_id, month_node["node_token"], doc_title, kb, f"{year}年/{int(month)}月/{doc_title}")
    if not doc_node:
        return {"status": "error", "step": "doc"}
    
    print(f"     📄 文档: {doc_title}")
    
    # 4. 写入内容
    doc_token = doc_node["obj_token"]
    
    # 读取现有内容
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
    if content_entry.split("](")[0].split("[")[-1] in existing:
        print(f"     ⏭️  内容已存在，跳过")
        return {"status": "skipped", "reason": "exists"}
    
    # 构建完整内容
    if not existing.strip():
        header = f"# {kb_config['name']} - {date_str} 日报\n\n"
        full_content = header + content_entry
    else:
        full_content = existing + "\n" + content_entry
    
    # 写入临时文件
    import tempfile
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
        f.write(full_content)
        temp_file = f.name
    
    # 写入文档
    result = subprocess.run(
        ["openclaw", "tool", "feishu_doc", "--action", "write",
         "--doc_token", doc_token,
         "--file_path", temp_file],
        capture_output=True,
        text=True
    )
    
    import os
    os.unlink(temp_file)
    
    if result.returncode == 0:
        print(f"     ✅ 已同步")
        return {"status": "success", "doc_token": doc_token}
    else:
        print(f"     ⚠️  同步失败: {result.stderr}")
        return {"status": "error", "error": result.stderr}


if __name__ == "__main__":
    # 测试
    if len(sys.argv) > 1:
        entry = sys.argv[1]
    else:
        entry = """### 📺 [Claude Code 2.0 测试](https://b23.tv/test)
> 来源: Bilibili | 收集时间: 2026-03-20 07:30

---
"""
    
    result = sync_to_feishu("ai-latest-news", entry, "2026-03-20")
    print(json.dumps(result, indent=2))
