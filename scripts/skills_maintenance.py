#!/usr/bin/env python3
"""
Skills维护检查脚本
每周日早上10点执行，检查各Skill的更新情况、功能状态等
"""

import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple

# Skills目录
SKILLS_DIR = Path("/workspace/projects/workspace/skills")

# 维护检查项
CHECK_ITEMS = {
    "file_integrity": "文件完整性检查",
    "git_status": "Git状态检查",
    "config_valid": "配置文件检查",
    "script_executable": "脚本可执行权限",
    "documentation": "文档完整性"
}


def run_command(cmd: List[str], timeout: int = 60) -> Tuple[bool, str]:
    """运行命令并返回结果"""
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        return result.returncode == 0, result.stdout + result.stderr
    except subprocess.TimeoutExpired:
        return False, "Timeout"
    except Exception as e:
        return False, str(e)


def check_skill_structure(skill_path: Path) -> Dict:
    """检查Skill目录结构"""
    checks = {
        "has_skill_md": (skill_path / "SKILL.md").exists(),
        "has_scripts": len(list(skill_path.rglob("*.py"))) > 0,
        "has_config": len(list(skill_path.rglob("*.yaml"))) > 0 or len(list(skill_path.rglob("*.json"))) > 0,
    }
    return checks


def check_scripts_executable(skill_path: Path) -> List[str]:
    """检查脚本是否有执行权限"""
    non_executable = []
    for script in skill_path.rglob("*.py"):
        if not script.stat().st_mode & 0o111:  # 没有执行权限
            non_executable.append(str(script.relative_to(SKILLS_DIR)))
    return non_executable


def check_skill_updates(skill_name: str) -> Dict:
    """检查Skill是否有更新（如果有Git源）"""
    # 这里可以扩展为检查GitHub等远程源
    # 目前仅做占位
    return {
        "has_update": False,
        "latest_version": None,
        "current_version": None
    }


def check_openclaw_version() -> Dict:
    """检查OpenClaw版本"""
    success, output = run_command(["openclaw", "--version"], timeout=10)
    
    if success:
        return {
            "status": "ok",
            "version": output.strip()
        }
    else:
        return {
            "status": "error",
            "error": output
        }


def check_system_health() -> Dict:
    """检查系统健康状态"""
    health = {}
    
    # 磁盘空间
    success, output = run_command(["df", "-h", "/workspace"], timeout=10)
    if success:
        lines = output.strip().split("\n")
        if len(lines) >= 2:
            parts = lines[1].split()
            if len(parts) >= 5:
                health["disk"] = {
                    "usage": parts[4],
                    "available": parts[3],
                    "status": "warning" if int(parts[4].rstrip("%")) > 80 else "ok"
                }
    
    # 内存使用
    success, output = run_command(["free", "-h"], timeout=10)
    if success:
        health["memory"] = "checked"
    
    # Cron服务
    success, output = run_command(["pgrep", "-x", "cron"], timeout=5)
    health["cron_running"] = success
    
    return health


def check_git_status() -> Dict:
    """检查Git状态"""
    success, output = run_command(
        ["git", "-C", "/workspace/projects/workspace", "status", "--short"],
        timeout=10
    )
    
    if success:
        uncommitted = [line for line in output.strip().split("\n") if line.strip()]
        return {
            "has_uncommitted": len(uncommitted) > 0,
            "uncommitted_files": uncommitted,
            "status": "warning" if uncommitted else "ok"
        }
    else:
        return {
            "status": "error",
            "error": output
        }


def scan_skills() -> List[Dict]:
    """扫描所有Skills并检查状态"""
    skills = []
    
    if not SKILLS_DIR.exists():
        return skills
    
    for skill_path in SKILLS_DIR.iterdir():
        if not skill_path.is_dir():
            continue
        
        skill_name = skill_path.name
        
        # 跳过隐藏目录
        if skill_name.startswith("."):
            continue
        
        print(f"  🔍 检查: {skill_name}...")
        
        # 基础检查
        structure = check_skill_structure(skill_path)
        non_exec_scripts = check_scripts_executable(skill_path)
        
        # 统计脚本数量
        script_count = len(list(skill_path.rglob("*.py")))
        
        skill_info = {
            "name": skill_name,
            "path": str(skill_path),
            "script_count": script_count,
            "structure": structure,
            "non_executable_scripts": non_exec_scripts,
            "status": "ok"
        }
        
        # 判断状态
        if not structure["has_skill_md"]:
            skill_info["status"] = "warning"
            skill_info["warning"] = "缺少SKILL.md"
        elif non_exec_scripts:
            skill_info["status"] = "warning"
            skill_info["warning"] = f"{len(non_exec_scripts)}个脚本无执行权限"
        
        skills.append(skill_info)
    
    return skills


def generate_report(skills: List[Dict], system_health: Dict, git_status: Dict, openclaw_info: Dict) -> Dict:
    """生成维护报告"""
    now = datetime.now()
    
    report = {
        "check_time": now.strftime("%Y-%m-%d %H:%M:%S"),
        "summary": {
            "total_skills": len(skills),
            "ok_skills": sum(1 for s in skills if s["status"] == "ok"),
            "warning_skills": sum(1 for s in skills if s["status"] == "warning"),
            "error_skills": sum(1 for s in skills if s["status"] == "error"),
        },
        "system_health": system_health,
        "git_status": git_status,
        "openclaw": openclaw_info,
        "skills": skills,
        "recommendations": []
    }
    
    # 生成建议
    recommendations = []
    
    # Git未提交文件
    if git_status.get("has_uncommitted"):
        recommendations.append({
            "priority": "high",
            "message": f"有 {len(git_status['uncommitted_files'])} 个文件未提交，建议执行: git add -A && git commit"
        })
    
    # 磁盘空间警告
    if system_health.get("disk", {}).get("status") == "warning":
        recommendations.append({
            "priority": "high",
            "message": f"磁盘使用率超过80% ({system_health['disk']['usage']})，建议清理空间"
        })
    
    # Cron未运行
    if not system_health.get("cron_running", False):
        recommendations.append({
            "priority": "high",
            "message": "Cron服务未运行，建议执行: sh scripts/start_cron.sh"
        })
    
    # 脚本权限问题
    for skill in skills:
        if skill.get("non_executable_scripts"):
            recommendations.append({
                "priority": "medium",
                "message": f"[{skill['name']}] {len(skill['non_executable_scripts'])} 个脚本缺少执行权限"
            })
    
    # 缺少文档
    for skill in skills:
        if not skill["structure"].get("has_skill_md"):
            recommendations.append({
                "priority": "low",
                "message": f"[{skill['name']}] 缺少 SKILL.md 文档"
            })
    
    report["recommendations"] = recommendations
    
    return report


def generate_text_report(report: Dict) -> str:
    """生成文本格式的维护报告"""
    lines = []
    
    lines.append("=" * 70)
    lines.append("🔧 Skills 维护检查报告")
    lines.append(f"检查时间: {report['check_time']}")
    lines.append("=" * 70)
    lines.append("")
    
    # 汇总
    summary = report["summary"]
    lines.append("📊 检查汇总")
    lines.append("-" * 70)
    lines.append(f"   Skills总数: {summary['total_skills']}")
    lines.append(f"   ✅ 正常: {summary['ok_skills']}")
    lines.append(f"   ⚠️  警告: {summary['warning_skills']}")
    lines.append(f"   ❌ 错误: {summary['error_skills']}")
    lines.append("")
    
    # 系统健康
    lines.append("💻 系统健康")
    lines.append("-" * 70)
    
    if "disk" in report["system_health"]:
        disk = report["system_health"]["disk"]
        status_emoji = "⚠️" if disk["status"] == "warning" else "✅"
        lines.append(f"   {status_emoji} 磁盘使用: {disk['usage']} (可用: {disk['available']})")
    
    if "cron_running" in report["system_health"]:
        cron_status = "✅ 运行中" if report["system_health"]["cron_running"] else "❌ 未运行"
        lines.append(f"   {cron_status} Cron服务")
    
    lines.append("")
    
    # Git状态
    lines.append("📦 Git状态")
    lines.append("-" * 70)
    if report["git_status"].get("has_uncommitted"):
        lines.append(f"   ⚠️  有 {len(report['git_status']['uncommitted_files'])} 个未提交文件:")
        for f in report["git_status"]["uncommitted_files"][:5]:
            lines.append(f"      - {f}")
        if len(report["git_status"]["uncommitted_files"]) > 5:
            lines.append(f"      ... 还有 {len(report['git_status']['uncommitted_files']) - 5} 个")
    else:
        lines.append("   ✅ 工作区干净")
    lines.append("")
    
    # OpenClaw版本
    lines.append("🦾 OpenClaw")
    lines.append("-" * 70)
    if report["openclaw"].get("status") == "ok":
        lines.append(f"   ✅ {report['openclaw']['version']}")
    else:
        lines.append(f"   ❌ {report['openclaw'].get('error', '未知错误')}")
    lines.append("")
    
    # Skills详情
    lines.append("📁 Skills 详情")
    lines.append("-" * 70)
    for skill in report["skills"]:
        status_emoji = "✅" if skill["status"] == "ok" else "⚠️"
        lines.append(f"   {status_emoji} {skill['name']}")
        lines.append(f"      脚本: {skill['script_count']}个")
        if skill.get("warning"):
            lines.append(f"      警告: {skill['warning']}")
    lines.append("")
    
    # 维护建议
    if report["recommendations"]:
        lines.append("💡 维护建议")
        lines.append("-" * 70)
        for rec in sorted(report["recommendations"], key=lambda x: x["priority"], reverse=True):
            priority_emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(rec["priority"], "⚪")
            lines.append(f"   {priority_emoji} [{rec['priority'].upper()}] {rec['message']}")
    else:
        lines.append("✨ 所有检查通过，暂无维护建议")
    
    lines.append("")
    lines.append("=" * 70)
    lines.append("💡 每周日早上10点自动检查 | 手动执行: python3 scripts/skills_maintenance.py")
    
    return "\n".join(lines)


def save_report(report: Dict, text_content: str):
    """保存维护报告"""
    output_dir = Path("/workspace/projects/workspace/memory/maintenance")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    today_str = datetime.now().strftime("%Y%m%d")
    
    # 保存JSON
    json_file = output_dir / f"report-{today_str}.json"
    json_file.write_text(
        json.dumps(report, ensure_ascii=False, indent=2),
        encoding='utf-8'
    )
    
    # 保存文本报告
    text_file = output_dir / f"report-{today_str}.txt"
    text_file.write_text(text_content, encoding='utf-8')
    
    # 保存最新报告链接
    latest_link = output_dir / "latest.txt"
    if latest_link.exists():
        latest_link.unlink()
    latest_link.symlink_to(text_file.name)
    
    return json_file, text_file


def fix_issues(report: Dict):
    """自动修复一些问题"""
    fixed = []
    
    # 修复脚本权限
    for skill in report["skills"]:
        if skill.get("non_executable_scripts"):
            for script_rel in skill["non_executable_scripts"]:
                script_path = SKILLS_DIR / script_rel
                if script_path.exists():
                    # 添加执行权限
                    current_mode = script_path.stat().st_mode
                    script_path.chmod(current_mode | 0o111)
                    fixed.append(f"已添加执行权限: {script_rel}")
    
    return fixed


def main():
    """主函数"""
    print("=" * 70)
    print("🔧 Skills 维护检查")
    print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 70)
    print()
    
    # 1. 扫描Skills
    print("📁 扫描Skills...")
    skills = scan_skills()
    print(f"   发现 {len(skills)} 个Skills")
    print()
    
    # 2. 检查系统健康
    print("💻 检查系统健康...")
    system_health = check_system_health()
    print()
    
    # 3. 检查Git状态
    print("📦 检查Git状态...")
    git_status = check_git_status()
    print()
    
    # 4. 检查OpenClaw版本
    print("🦾 检查OpenClaw版本...")
    openclaw_info = check_openclaw_version()
    print()
    
    # 生成报告
    report = generate_report(skills, system_health, git_status, openclaw_info)
    
    # 生成文本报告
    text_report = generate_text_report(report)
    print(text_report)
    print()
    
    # 保存报告
    json_file, text_file = save_report(report, text_report)
    
    print(f"✅ 维护报告已保存:")
    print(f"   JSON: {json_file}")
    print(f"   文本: {text_file}")
    
    # 自动修复
    if any(s.get("non_executable_scripts") for s in skills):
        print()
        print("🔧 自动修复脚本权限...")
        fixed = fix_issues(report)
        for f in fixed[:5]:
            print(f"   ✅ {f}")
        if len(fixed) > 5:
            print(f"   ... 共修复 {len(fixed)} 项")
    
    # 返回状态码
    if report["summary"]["error_skills"] > 0 or len(report["recommendations"]) > 0:
        print()
        print("⚠️  检查发现问题，建议处理上述建议")
        return 1
    else:
        print()
        print("✨ 所有检查通过！")
        return 0


if __name__ == "__main__":
    sys.exit(main())
