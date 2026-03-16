#!/usr/bin/env python3
"""
Skills 维护检查脚本
每周日 10:00 执行
功能：
1. 扫描所有Skills状态
2. 检查系统健康（磁盘、Cron）
3. 检查Git未提交文件
4. 检查OpenClaw版本
5. 自动修复脚本权限
"""

import os
import subprocess
import json
import datetime
from pathlib import Path

# 配置
WORKSPACE_DIR = "/workspace/projects/workspace"
MEMORY_DIR = os.path.join(WORKSPACE_DIR, "memory", "maintenance")
SKILLS_DIR = os.path.join(WORKSPACE_DIR, "skills")

def run_command(cmd, cwd=None):
    """运行shell命令并返回输出"""
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            cwd=cwd or WORKSPACE_DIR,
            capture_output=True,
            text=True,
            timeout=30
        )
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def check_disk_space():
    """检查磁盘空间"""
    success, stdout, stderr = run_command("df -h / | tail -1")
    if success:
        parts = stdout.split()
        if len(parts) >= 5:
            usage = parts[4].replace('%', '')
            return int(usage)
    return None

def check_cron_status():
    """检查Cron状态"""
    success, stdout, _ = run_command("pgrep -x cron")
    return success

def check_git_status():
    """检查Git未提交文件"""
    success, stdout, _ = run_command("git status --short", WORKSPACE_DIR)
    if success:
        files = [f.strip() for f in stdout.split('\n') if f.strip()]
        return files
    return []

def check_openclaw_version():
    """检查OpenClaw版本"""
    success, stdout, _ = run_command("openclaw version 2>/dev/null || openclaw --version 2>/dev/null || echo 'unknown'")
    return stdout.strip() if success else "unknown"

def list_skills():
    """列出所有Skills"""
    skills = []
    if os.path.exists(SKILLS_DIR):
        for item in os.listdir(SKILLS_DIR):
            skill_path = os.path.join(SKILLS_DIR, item)
            if os.path.isdir(skill_path):
                skill_file = os.path.join(skill_path, "SKILL.md")
                if os.path.exists(skill_file):
                    # 获取最后更新时间
                    mtime = os.path.getmtime(skill_file)
                    skills.append({
                        "name": item,
                        "path": skill_path,
                        "last_modified": datetime.datetime.fromtimestamp(mtime).strftime("%Y-%m-%d")
                    })
    return skills

def fix_script_permissions():
    """自动修复脚本权限"""
    fixed = []
    for root, dirs, files in os.walk(WORKSPACE_DIR):
        for file in files:
            if file.endswith('.py') or file.endswith('.sh'):
                file_path = os.path.join(root, file)
                # 检查是否可执行
                if not os.access(file_path, os.X_OK):
                    os.chmod(file_path, 0o755)
                    fixed.append(file_path.replace(WORKSPACE_DIR + "/", ""))
    return fixed

def generate_report():
    """生成维护报告"""
    report = {
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "checks": {}
    }
    
    # 1. 磁盘空间检查
    disk_usage = check_disk_space()
    report["checks"]["disk_space"] = {
        "status": "ok" if disk_usage and disk_usage < 80 else "warning" if disk_usage and disk_usage < 90 else "critical",
        "usage_percent": disk_usage
    }
    
    # 2. Cron状态检查
    cron_running = check_cron_status()
    report["checks"]["cron"] = {
        "status": "ok" if cron_running else "error",
        "running": cron_running
    }
    
    # 3. Git状态检查
    uncommitted = check_git_status()
    report["checks"]["git"] = {
        "status": "ok" if len(uncommitted) == 0 else "warning",
        "uncommitted_files": uncommitted,
        "uncommitted_count": len(uncommitted)
    }
    
    # 4. OpenClaw版本
    version = check_openclaw_version()
    report["checks"]["openclaw"] = {
        "status": "ok",
        "version": version
    }
    
    # 5. Skills列表
    skills = list_skills()
    report["checks"]["skills"] = {
        "status": "ok",
        "count": len(skills),
        "list": skills
    }
    
    # 6. 修复脚本权限
    fixed_scripts = fix_script_permissions()
    report["checks"]["permissions"] = {
        "status": "ok",
        "fixed_scripts": fixed_scripts,
        "fixed_count": len(fixed_scripts)
    }
    
    return report

def save_report(report):
    """保存报告到文件"""
    # 确保目录存在
    os.makedirs(MEMORY_DIR, exist_ok=True)
    
    # 保存JSON报告
    date_str = datetime.datetime.now().strftime("%Y-%m-%d")
    report_file = os.path.join(MEMORY_DIR, f"maintenance-{date_str}.json")
    
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    # 生成Markdown摘要
    md_file = os.path.join(MEMORY_DIR, f"maintenance-{date_str}.md")
    with open(md_file, 'w', encoding='utf-8') as f:
        f.write(f"# Skills 维护报告\n\n")
        f.write(f"**时间**: {report['timestamp']}\n\n")
        
        f.write("## 检查结果\n\n")
        
        # 磁盘空间
        disk = report["checks"]["disk_space"]
        f.write(f"### 磁盘空间\n")
        f.write(f"- 使用率: {disk['usage_percent']}%\n")
        f.write(f"- 状态: {'✅' if disk['status'] == 'ok' else '⚠️' if disk['status'] == 'warning' else '❌'} {disk['status']}\n\n")
        
        # Cron
        cron = report["checks"]["cron"]
        f.write(f"### Cron服务\n")
        f.write(f"- 运行状态: {'✅ 运行中' if cron['running'] else '❌ 未运行'}\n\n")
        
        # Git
        git = report["checks"]["git"]
        f.write(f"### Git状态\n")
        f.write(f"- 未提交文件: {git['uncommitted_count']} 个\n")
        if git['uncommitted_files']:
            f.write("- 文件列表:\n")
            for file in git['uncommitted_files'][:10]:  # 最多显示10个
                f.write(f"  - `{file}`\n")
            if len(git['uncommitted_files']) > 10:
                f.write(f"  - ... 还有 {len(git['uncommitted_files']) - 10} 个文件\n")
        f.write("\n")
        
        # OpenClaw
        oc = report["checks"]["openclaw"]
        f.write(f"### OpenClaw版本\n")
        f.write(f"- 版本: {oc['version']}\n\n")
        
        # Skills
        skills = report["checks"]["skills"]
        f.write(f"### Skills 状态\n")
        f.write(f"- 总数: {skills['count']} 个\n")
        f.write("- 列表:\n")
        for skill in skills['list']:
            f.write(f"  - {skill['name']} (最后更新: {skill['last_modified']})\n")
        f.write("\n")
        
        # 权限修复
        perm = report["checks"]["permissions"]
        f.write(f"### 脚本权限修复\n")
        f.write(f"- 修复文件数: {perm['fixed_count']}\n")
        if perm['fixed_scripts']:
            f.write("- 修复的文件:\n")
            for script in perm['fixed_scripts']:
                f.write(f"  - `{script}`\n")
        f.write("\n")
    
    return report_file, md_file

def main():
    print("=" * 50)
    print("Skills 维护检查")
    print("=" * 50)
    
    # 生成报告
    report = generate_report()
    
    # 保存报告
    json_file, md_file = save_report(report)
    
    print(f"\n✅ 维护检查完成！")
    print(f"📄 JSON报告: {json_file}")
    print(f"📝 Markdown报告: {md_file}")
    
    # 打印摘要
    print("\n" + "=" * 50)
    print("检查摘要")
    print("=" * 50)
    
    disk = report["checks"]["disk_space"]
    print(f"磁盘空间: {disk['usage_percent']}% {'✅' if disk['status'] == 'ok' else '⚠️'}")
    
    cron = report["checks"]["cron"]
    print(f"Cron服务: {'✅ 运行中' if cron['running'] else '❌ 未运行'}")
    
    git = report["checks"]["git"]
    print(f"Git未提交: {git['uncommitted_count']} 个文件 {'✅' if git['uncommitted_count'] == 0 else '⚠️'}")
    
    skills = report["checks"]["skills"]
    print(f"Skills数量: {skills['count']} 个")
    
    perm = report["checks"]["permissions"]
    print(f"权限修复: {perm['fixed_count']} 个文件")
    
    print("=" * 50)

if __name__ == "__main__":
    main()
