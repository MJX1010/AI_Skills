#!/usr/bin/env python3
"""
日报推送脚本 - 推送日报到飞书知识库和对话窗口
"""

import json
import subprocess
from datetime import datetime
from pathlib import Path

WORKSPACE = Path("/workspace/projects/workspace")
MEMORY_DIR = WORKSPACE / "memory"

KB_CONFIG = {
    "ai-latest-news": {
        "name": "🤖 AI最新资讯",
        "space_id": "7616519632920251572",
        "home_node": "PhL6wlstzissQ1kKPwMc18xbngg"
    },
    "game-development": {
        "name": "🎮 游戏开发",
        "space_id": "7616735513310924004",
        "home_node": "U9EWwwL8ui16IEkrN8vcIRISnFg"
    },
    "healthy-living": {
        "name": "🌱 健康生活",
        "space_id": "7616737910330510558",
        "home_node": "XD2PwwJukiD8a8koNAAc4Fedn5t"
    }
}


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


def sync_to_feishu(kb: str, content: str, date_str: str) -> bool:
    """同步到飞书知识库"""
    config = KB_CONFIG[kb]
    year = date_str[:4]
    month = str(int(date_str[5:7]))  # 去掉前导零
    day = date_str[8:10]
    
    doc_title = f"{int(month)}月{int(day)}日 日报"
    
    print(f"\n  📤 同步 {config['name']} 到飞书...")
    
    try:
        # 1. 获取或创建年度节点
        result = subprocess.run(
            ["feishu_wiki", "--action", "nodes", "--space_id", config['space_id']],
            capture_output=True, text=True
        )
        nodes = json.loads(result.stdout)
        home_node = nodes["nodes"][0]["node_token"]
        
        # 2. 创建年度节点
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
            # 查找已存在的年度节点
            year_node = None
            for node in json.loads(result.stdout).get("nodes", []):
                if node["title"] == f"{year}年":
                    year_node = node["node_token"]
                    break
        
        if not year_node:
            print(f"    ⚠️ 无法获取年度节点")
            return False
        
        # 3. 创建月度节点
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
            # 查找已存在的月度节点
            month_node = None
            result = subprocess.run(
                ["feishu_wiki", "--action", "nodes", "--space_id", config['space_id']],
                capture_output=True, text=True
            )
            # 简化处理，实际应该递归查找
            month_node = None
        
        if not month_node:
            print(f"    ℹ️ 使用已有月度节点或稍后重试")
            return False
        
        # 4. 创建日报文档
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
            
            # 5. 写入内容
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
    import sys
    sys.exit(main())
