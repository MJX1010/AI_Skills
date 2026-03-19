#!/usr/bin/env python3
"""
Skills 维护脚本 - 检查并更新 Skills
"""

import json
import subprocess
from datetime import datetime
from pathlib import Path

WORKSPACE = Path("/workspace/projects/workspace")
SKILLS_DIR = WORKSPACE / "skills"
MEMORY_DIR = WORKSPACE / "memory"


def get_all_skills():
    """获取所有已安装的 skills"""
    skills = []
    if SKILLS_DIR.exists():
        for skill_dir in SKILLS_DIR.iterdir():
            if skill_dir.is_dir() and (skill_dir / "SKILL.md").exists():
                skills.append(skill_dir.name)
    return skills


def check_skill_updates():
    """检查 skill 更新"""
    print("🔍 检查 Skills 更新...\n")
    
    skills = get_all_skills()
    print(f"📦 已安装 {len(skills)} 个 Skills:\n")
    
    for skill in sorted(skills):
        print(f"  • {skill}")
    
    print("\n" + "="*60)
    print("⚠️  自动更新检查需要配置远程源")
    print("="*60)
    print("""
目前 Skills 更新需要手动管理：

1. **检查 GitHub 更新**
   - 访问 https://github.com/openclaw/openclaw
   - 查看 releases 页面

2. **查看本地 Skills**
   - 直接查看 skills/ 目录
   - 检查 SKILL.md 更新

3. **手动更新 Skill**
   - 编辑 SKILL.md
   - 更新脚本文件

建议配置:
- 为每个 skill 添加版本信息到 SKILL.md
- 记录上次检查时间到 memory/skills-state.json

已安装 Skills:
""")
    
    for skill in sorted(skills):
        print(f"  ✅ {skill}")
    
    # 记录检查日志
    state_file = MEMORY_DIR / "skills-state.json"
    state = {}
    if state_file.exists():
        state = json.loads(state_file.read_text())
    
    state["last_check"] = datetime.now().isoformat()
    state["skills_count"] = len(skills)
    state["skills_list"] = sorted(skills)
    
    state_file.write_text(json.dumps(state, indent=2))
    
    print(f"\n✅ 检查完成，已记录到 {state_file}")
    return True


def cleanup_old_logs():
    """清理旧日志"""
    print("\n🧹 清理旧日志...")
    
    log_dirs = [
        MEMORY_DIR / "task-automation" / "logs",
    ]
    
    cleaned = 0
    for log_dir in log_dirs:
        if log_dir.exists():
            # 清理超过30天的日志
            # 简化处理，暂时只打印
            files = list(log_dir.glob("*.log"))
            print(f"  {log_dir}: {len(files)} 个日志文件")
            cleaned += len(files)
    
    print(f"  共发现 {cleaned} 个日志文件")


def verify_skill_integrity():
    """验证 skill 完整性"""
    print("\n🔍 验证 Skill 完整性...\n")
    
    skills = get_all_skills()
    issues = []
    
    for skill in skills:
        skill_dir = SKILLS_DIR / skill
        skill_md = skill_dir / "SKILL.md"
        
        # 检查 SKILL.md
        if not skill_md.exists():
            issues.append(f"{skill}: 缺少 SKILL.md")
            continue
        
        # 读取 SKILL.md 检查关键信息
        try:
            content = skill_md.read_text()
            if "name:" not in content:
                issues.append(f"{skill}: SKILL.md 缺少 name 字段")
            if "description:" not in content:
                issues.append(f"{skill}: SKILL.md 缺少 description 字段")
        except Exception as e:
            issues.append(f"{skill}: 读取失败 - {e}")
    
    if issues:
        print("⚠️  发现问题:")
        for issue in issues:
            print(f"  • {issue}")
    else:
        print("✅ 所有 Skills 完整性正常")
    
    return len(issues) == 0


def main():
    print("🛠️  Skills 维护\n")
    print("="*60 + "\n")
    
    # 1. 检查更新
    check_skill_updates()
    
    # 2. 验证完整性
    verify_skill_integrity()
    
    # 3. 清理日志
    cleanup_old_logs()
    
    print("\n" + "="*60)
    print("✅ Skills 维护完成!")
    print("="*60)
    
    return True


if __name__ == "__main__":
    main()
