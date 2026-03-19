#!/usr/bin/env python3
"""
周报推送脚本 - 推送周报到飞书知识库
"""

import json
import subprocess
from datetime import datetime, timedelta
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


def sync_to_feishu(kb: str, content: str, monday: datetime, sunday: datetime) -> bool:
    """同步到飞书知识库"""
    config = KB_CONFIG[kb]
    year = monday.strftime("%Y")
    month = str(int(monday.strftime("%m")))
    week_num = monday.isocalendar()[1]
    date_range = f"{monday.strftime('%m.%d')}-{sunday.strftime('%m.%d')}"
    
    doc_title = f"第{week_num}期 - {date_range} 周报"
    
    print(f"\n  📤 同步 {config['name']} 到飞书...")
    
    try:
        # 获取知识库首页
        result = subprocess.run(
            ["feishu_wiki", "--action", "nodes", "--space_id", config['space_id']],
            capture_output=True, text=True
        )
        nodes = json.loads(result.stdout)
        home_node = nodes["nodes"][0]["node_token"]
        
        # 创建年度节点
        year_result = subprocess.run(
            ["feishu_wiki", "--action", "create",
             "--space_id", config['space_id'],
             "--parent_node_token", home_node,
             "--title", f"{year}年",
             "--obj_type", "docx"],
            capture_output=True, text=True
        )
        try:
            year_node = json.loads(year_result.stdout)["node_token"]
        except:
            year_node = None
            for node in json.loads(result.stdout).get("nodes", []):
                if node["title"] == f"{year}年":
                    year_node = node["node_token"]
                    break
        
        if not year_node:
            print(f"    ⚠️ 无法获取年度节点")
            return False
        
        # 创建月度节点
        month_result = subprocess.run(
            ["feishu_wiki", "--action", "create",
             "--space_id", config['space_id'],
             "--parent_node_token", year_node,
             "--title", f"{month}月",
             "--obj_type", "docx"],
            capture_output=True, text=True
        )
        try:
            month_node = json.loads(month_result.stdout)["node_token"]
        except:
            month_node = None
        
        if not month_node:
            print(f"    ℹ️ 使用已有月度节点")
            return False
        
        # 创建周报文档
        doc_result = subprocess.run(
            ["feishu_wiki", "--action", "create",
             "--space_id", config['space_id'],
             "--parent_node_token", month_node,
             "--title", doc_title,
             "--obj_type", "docx"],
            capture_output=True, text=True
        )
        
        try:
            doc_data = json.loads(doc_result.stdout)
            doc_token = doc_data["obj_token"]
            
            # 写入内容
            subprocess.run(
                ["feishu_doc", "--action", "write",
                 "--doc_token", doc_token,
                 "--content", content],
                capture_output=True, text=True
            )
            
            print(f"    ✅ 已同步: {doc_title}")
            return True
            
        except Exception as e:
            print(f"    ⚠️ 同步失败: {e}")
            return False
            
    except Exception as e:
        print(f"    ⚠️ 异常: {e}")
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
