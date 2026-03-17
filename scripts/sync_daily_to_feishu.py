#!/usr/bin/env python3
"""
每日资讯同步到飞书知识库
Usage: python sync_daily_to_feishu.py --date YYYY-MM-DD
"""

import argparse
import subprocess
import sys
import json
from datetime import datetime, timedelta
from pathlib import Path

# 知识库配置
KB_CONFIG = {
    "ai-latest-news": {
        "name": "AI最新资讯",
        "space_id": "7616519632920251572",
        "parent_node": "DXDSw3upPinqWgkqN8XcXLCOnLh",  # 3月节点
        "folder": "ai-content"
    },
    "game-development": {
        "name": "游戏开发",
        "space_id": "7616735513310924004",
        "parent_node": "UAP0wSzI8iUFW5k0VxAcKIMBnjf",  # 3月节点
        "folder": "game-content"
    },
    "healthy-living": {
        "name": "健康生活",
        "space_id": "7616737910330510558",
        "parent_node": "DTY6wjIvNiW3gNkyf5ccI93Rnxd",  # 3月节点
        "folder": "health-content"
    }
}


def run_openclaw(tool, action, **kwargs):
    """使用openclaw运行工具"""
    cmd = ["openclaw", tool, "--action", action]
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
            return True, result.stdout
        else:
            return False, result.stderr
    except Exception as e:
        return False, str(e)


def get_nodes(space_id, parent_node):
    """获取节点列表"""
    # 使用 feishu_wiki 工具
    cmd = [
        "python3", "-c",
        f"""
import sys
sys.path.insert(0, '/usr/lib/node_modules/openclaw/extensions/feishu')
from feishu_wiki import feishu_wiki
result = feishu_wiki(space_id='{space_id}', action='nodes', parent_node_token='{parent_node}')
print(result)
"""
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            # 提取JSON输出
            import re
            json_match = re.search(r'\{.*\}', result.stdout, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        return {"nodes": []}
    except Exception as e:
        print(f"  ⚠️ 获取节点失败: {e}")
        return {"nodes": []}


def create_node(space_id, parent_node, title, obj_type="docx"):
    """创建节点"""
    cmd = [
        "python3", "-c",
        f"""
import sys
sys.path.insert(0, '/usr/lib/node_modules/openclaw/extensions/feishu')
from feishu_wiki import feishu_wiki
result = feishu_wiki(space_id='{space_id}', action='create', parent_node_token='{parent_node}', title='{title}', obj_type='{obj_type}')
print(result)
"""
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            import re
            json_match = re.search(r'\{.*\}', result.stdout, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        return None
    except Exception as e:
        print(f"  ⚠️ 创建节点失败: {e}")
        return None


def write_doc(doc_token, content):
    """写入文档内容"""
    cmd = [
        "python3", "-c",
        f"""
import sys
sys.path.insert(0, '/usr/lib/node_modules/openclaw/extensions/feishu')
from feishu_doc import feishu_doc
result = feishu_doc(doc_token='{doc_token}', action='write', content='''{content}''')
print(result)
"""
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        return result.returncode == 0
    except Exception as e:
        print(f"  ⚠️ 写入文档失败: {e}")
        return False


def create_daily_folder(space_id, parent_node, date_str):
    """创建日报文件夹"""
    folder_name = f"📅 日报 {date_str[:7]}"  # 如: 📅 日报 2026-03
    
    # 检查是否已存在
    nodes = get_nodes(space_id, parent_node)
    for node in nodes.get("nodes", []):
        if node.get("title") == folder_name:
            print(f"  📁 使用已有文件夹: {folder_name}")
            return node.get("node_token")
    
    # 创建新文件夹
    print(f"  📁 创建文件夹: {folder_name}")
    result = create_node(space_id, parent_node, folder_name, "docx")
    if result:
        return result.get("node_token")
    
    return None


def create_daily_doc(space_id, parent_node, date_str, kb_name):
    """创建日报文档"""
    doc_title = f"{date_str} 日报"
    
    # 检查是否已存在
    nodes = get_nodes(space_id, parent_node)
    for node in nodes.get("nodes", []):
        if node.get("title") == doc_title:
            print(f"  📄 更新已有文档: {doc_title}")
            return node.get("obj_token"), node.get("node_token")
    
    # 创建新文档
    print(f"  📄 创建文档: {doc_title}")
    result = create_node(space_id, parent_node, doc_title, "docx")
    if result:
        return result.get("obj_token"), result.get("node_token")
    
    return None, None


def sync_content_to_doc(doc_token, md_content):
    """同步内容到飞书文档"""
    # 转义内容中的特殊字符
    md_content = md_content.replace("'", "'\"'\"'")
    
    cmd = [
        "python3", "-c",
        f"""
import sys
sys.path.insert(0, '/usr/lib/node_modules/openclaw/extensions/feishu')
from feishu_doc import feishu_doc
content = '''{md_content}'''
result = feishu_doc(doc_token='{doc_token}', action='write', content=content)
print(result)
"""
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        if result.returncode == 0:
            return True
        else:
            print(f"  ⚠️ 写入失败: {result.stderr[:200]}")
            return False
    except Exception as e:
        print(f"  ⚠️ 写入异常: {e}")
        return False


def sync_kb_daily(kb_key, date_str):
    """同步单个知识库的日报"""
    config = KB_CONFIG[kb_key]
    folder = config["folder"]
    
    # 读取本地日报文件
    daily_file = Path(f"/workspace/projects/workspace/memory/{folder}/daily/{date_str}.md")
    if not daily_file.exists():
        print(f"  ⚠️ 本地文件不存在: {daily_file}")
        return False, 0
    
    md_content = daily_file.read_text(encoding='utf-8')
    
    # 统计文章数
    article_count = md_content.count("### ")
    
    print(f"\n{'=' * 60}")
    print(f"📚 同步: {config['name']}")
    print(f"{'=' * 60}")
    print(f"  📄 本地文件: {daily_file}")
    print(f"  📊 文章数量: {article_count}篇")
    
    # 创建日报文件夹
    folder_token = create_daily_folder(
        config["space_id"],
        config["parent_node"],
        date_str
    )
    
    if not folder_token:
        print(f"  ❌ 无法创建或获取文件夹")
        return False, 0
    
    # 创建日报文档
    doc_token, node_token = create_daily_doc(
        config["space_id"],
        folder_token,
        date_str,
        config["name"]
    )
    
    if not doc_token:
        print(f"  ❌ 无法创建文档")
        return False, 0
    
    # 同步内容
    print(f"  📝 正在写入内容...")
    success = sync_content_to_doc(doc_token, md_content)
    
    if success:
        print(f"  ✅ 同步成功")
        print(f"  🔗 Wiki节点: {node_token}")
        return True, article_count
    else:
        print(f"  ❌ 同步失败")
        return False, 0


def main():
    parser = argparse.ArgumentParser(description="同步每日资讯到飞书知识库")
    parser.add_argument("--date", default=None,
                       help="日期 (YYYY-MM-DD，默认昨天)")
    
    args = parser.parse_args()
    
    # 获取日期
    if args.date:
        date_str = args.date
    else:
        date_str = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    
    print("=" * 60)
    print("🔄 同步每日资讯到飞书知识库")
    print("=" * 60)
    print(f"📅 日期: {date_str}")
    print()
    
    results = {}
    total_count = 0
    
    # 同步三个知识库
    for kb_key in KB_CONFIG.keys():
        success, count = sync_kb_daily(kb_key, date_str)
        results[kb_key] = {"success": success, "count": count}
        total_count += count
    
    # 汇总
    print("\n" + "=" * 60)
    print("📊 同步完成汇总")
    print("=" * 60)
    
    for kb_key, result in results.items():
        status = "✅" if result["success"] else "❌"
        print(f"{status} {KB_CONFIG[kb_key]['name']}: {result['count']}篇")
    
    print(f"\n📈 总计: {total_count}篇")
    print("=" * 60)
    
    return 0 if all(r["success"] for r in results.values()) else 1


if __name__ == "__main__":
    sys.exit(main())
