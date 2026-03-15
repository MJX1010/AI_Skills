#!/usr/bin/env python3
"""
B站视频归档助手
一键抓取B站视频并归档到层级结构
"""

import argparse
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

# 导入归档管理器
sys.path.insert(0, str(Path(__file__).parent))
from archive_manager import LinkArchiveManager


def fetch_bilibili_video(url: str, method: str = "auto") -> dict:
    """
    调用 fetch_bilibili.py 抓取视频
    """
    fetch_script = Path(__file__).parent / "fetch_bilibili.py"
    
    output_file = f"/tmp/bilibili_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    try:
        result = subprocess.run(
            [
                "python3", str(fetch_script),
                url,
                "--method", method,
                "--format", "json",
                "--output", output_file
            ],
            capture_output=True,
            text=True,
            timeout=120
        )
        
        if result.returncode != 0:
            print(f"❌ 抓取失败: {result.stderr}")
            return None
        
        # 读取结果
        if Path(output_file).exists():
            data = json.loads(Path(output_file).read_text(encoding='utf-8'))
            return data
        
        return None
        
    except Exception as e:
        print(f"❌ 抓取异常: {e}")
        return None


def classify_video(video: dict) -> str:
    """
    根据视频内容自动分类
    """
    from classify_links import classify_link
    
    url = video.get('source_url', '')
    title = video.get('title', '')
    description = video.get('description', '')
    tags = ' '.join(video.get('tags', []))
    
    # 合并所有文本进行分类
    content = f"{title} {description} {tags}"
    
    kb_key, confidence, reason = classify_link(url, title, content)
    
    print(f"📊 分类结果: {kb_key} (置信度: {confidence:.2f})")
    print(f"   原因: {reason}")
    
    return kb_key


def format_duration(seconds):
    """格式化时长"""
    if not seconds:
        return "未知"
    minutes = int(seconds) // 60
    secs = int(seconds) % 60
    if minutes >= 60:
        hours = minutes // 60
        minutes = minutes % 60
        return f"{hours}:{minutes:02d}:{secs:02d}"
    return f"{minutes}:{secs:02d}"


def format_number(num):
    """格式化数字"""
    if not num:
        return "0"
    try:
        num = int(num)
        if num >= 10000:
            return f"{num/10000:.1f}万"
        return str(num)
    except:
        return str(num)


def archive_video(video: dict, category: str = None, 
                  auto_classify: bool = False, kb_key: str = None) -> Path:
    """
    归档B站视频
    
    Args:
        video: 视频数据
        category: 指定分类（如不提供则使用 auto_classify）
        auto_classify: 是否自动分类
        kb_key: 知识库key（用于归档到对应知识库）
    """
    manager = LinkArchiveManager()
    
    # 确定分类
    if auto_classify or (category is None and kb_key is None):
        kb_key = classify_video(video)
    
    # 映射到链接分类
    category_map = {
        'ai-latest-news': 'bilibili-videos',
        'game-dev': 'bilibili-videos',
        'healthy-living': 'bilibili-videos',
        'link-collection': 'bilibili-videos'
    }
    category = category_map.get(kb_key, 'bilibili-videos')
    
    # 提取信息
    url = video.get('source_url', '')
    title = video.get('title', '无标题')
    author = video.get('owner', {}).get('name', '')
    publish_time = video.get('publish_time_formatted', '')
    description = video.get('description', '')[:300]  # 摘要长度
    duration = format_duration(video.get('duration', 0))
    view_count = format_number(video.get('view_count', 0))
    
    # 构建摘要
    summary = f"【{author} · {duration} · {view_count}播放】{description}..."
    
    # 构建来源信息
    source = f"Bilibili"
    if publish_time:
        source += f" · {publish_time}"
    
    # 构建标签
    tags = ['B站视频', 'bilibili']
    if video.get('tags'):
        tags.extend(video.get('tags', [])[:5])
    
    # 添加知识库标签
    kb_tag_map = {
        'ai-latest-news': 'AI',
        'game-dev': '游戏',
        'healthy-living': '健康',
    }
    if kb_key in kb_tag_map:
        tags.append(kb_tag_map[kb_key])
    
    # 添加到归档
    doc_path = manager.add_link(
        category=category,
        url=url,
        title=title,
        summary=summary,
        source=source,
        tags=tags
    )
    
    return doc_path, kb_key


def add_to_weekly(video: dict, kb_key: str) -> bool:
    """
    将视频添加到对应知识库的周刊
    
    Args:
        video: 视频数据
        kb_key: 知识库key
    
    Returns:
        是否成功添加
    """
    try:
        # 确定周刊文件路径
        from datetime import datetime
        import os
        
        now = datetime.now()
        year = now.year
        week = now.isocalendar()[1]
        
        weekly_files = {
            'ai-latest-news': f'/workspace/projects/workspace/memory/ai-content/weekly/weekly-{year}-W{week:02d}.md',
            'game-dev': f'/workspace/projects/workspace/memory/game-content/weekly/game-weekly-{year}-W{week:02d}.md',
            'healthy-living': f'/workspace/projects/workspace/memory/health-content/weekly/health-weekly-{year}-W{week:02d}.md',
        }
        
        if kb_key not in weekly_files:
            return False
        
        weekly_file = weekly_files[kb_key]
        
        # 检查周刊文件是否存在
        if not os.path.exists(weekly_file):
            print(f"⚠️  周刊文件不存在: {weekly_file}")
            return False
        
        # 读取现有内容
        content = Path(weekly_file).read_text(encoding='utf-8')
        
        # 构建视频条目
        title = video.get('title', '无标题')
        url = video.get('source_url', '')
        author = video.get('owner', {}).get('name', '未知')
        description = video.get('description', '')[:200]
        duration = format_duration(video.get('duration', 0))
        view_count = format_number(video.get('view_count', 0))
        
        video_entry = f"""
### [{title}]({url})
> 🎬 B站视频 | UP主: {author} | 时长: {duration} | 播放量: {view_count}

{description}...

> 来源：[Bilibili]({url}) · {video.get('publish_time_formatted', '未知')}

"""
        
        # 查找合适的插入位置（在视频/案例相关模块）
        # 这里简化处理，添加到文件末尾链接引用之前
        if '## 🔗 链接引用' in content:
            parts = content.split('## 🔗 链接引用')
            new_content = parts[0] + video_entry + '\n## 🔗 链接引用' + parts[1]
        else:
            new_content = content + '\n' + video_entry
        
        # 写回文件
        Path(weekly_file).write_text(new_content, encoding='utf-8')
        
        print(f"✅ 已添加到周刊: {weekly_file}")
        return True
        
    except Exception as e:
        print(f"⚠️  添加到周刊失败: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description='B站视频归档助手')
    parser.add_argument('--url', '-u', help='B站视频URL')
    parser.add_argument('--file', '-f', help='已抓取的JSON文件路径')
    parser.add_argument('--method', '-m', default='auto', 
                        choices=['api', 'playwright', 'auto'],
                        help='抓取方法')
    parser.add_argument('--category', '-c', 
                        choices=['bilibili-videos', 'user-links', 'self-collected'],
                        help='指定分类（不指定则自动分类）')
    parser.add_argument('--auto-classify', '-a', action='store_true',
                        help='自动根据内容分类')
    parser.add_argument('--kb', choices=['ai-latest-news', 'game-dev', 'healthy-living'],
                        help='指定归档到哪个知识库')
    parser.add_argument('--add-to-weekly', '-w', action='store_true',
                        help='同时添加到当前周刊')
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("B站视频归档助手")
    print("=" * 60)
    print()
    
    # 获取视频数据
    video = None
    
    if args.file:
        # 从文件读取
        print(f"📂 从文件读取: {args.file}")
        video = json.loads(Path(args.file).read_text(encoding='utf-8'))
    
    elif args.url:
        # 抓取视频
        print(f"🔗 抓取视频: {args.url}")
        video = fetch_bilibili_video(args.url, args.method)
        
        if not video:
            print("❌ 抓取失败")
            sys.exit(1)
    
    else:
        print("❌ 请提供 --url 或 --file 参数")
        sys.exit(1)
    
    # 显示视频信息
    print(f"\n📹 视频信息:")
    print(f"   标题: {video.get('title', '无标题')}")
    print(f"   UP主: {video.get('owner', {}).get('name', '未知')}")
    print(f"   BV号: {video.get('bvid', '未知')}")
    print(f"   发布时间: {video.get('publish_time_formatted', '未知')}")
    print(f"   时长: {format_duration(video.get('duration', 0))}")
    print(f"   播放量: {format_number(video.get('view_count', 0))}")
    print(f"   标签: {', '.join(video.get('tags', [])[:5])}")
    print()
    
    # 归档
    print("📦 开始归档...")
    doc_path, kb_key = archive_video(
        video,
        category=args.category,
        auto_classify=args.auto_classify,
        kb_key=args.kb
    )
    
    print(f"\n✅ 归档完成!")
    print(f"   文档路径: {doc_path}")
    print(f"   知识库: 链接收藏 > B站视频")
    print(f"   分类: {kb_key}")
    
    # 添加到周刊
    if args.add_to_weekly:
        print()
        print("📰 添加到周刊...")
        add_to_weekly(video, kb_key)


if __name__ == "__main__":
    main()
