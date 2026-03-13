#!/usr/bin/env python3
"""
OpenClaw 更新检查脚本
检查 OpenClaw 的最新版本和更新信息
"""

import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

# 配置
MEMORY_DIR = Path("/workspace/projects/workspace/memory")
UPDATE_LOG_FILE = MEMORY_DIR / "openclaw-updates.json"

def get_current_version():
    """获取当前安装的 OpenClaw 版本"""
    try:
        result = subprocess.run(
            ["openclaw", "--version"],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except Exception as e:
        print(f"获取当前版本失败: {e}")
    return None

def get_latest_version_from_npm():
    """从 npm 获取最新版本"""
    try:
        result = subprocess.run(
            ["npm", "view", "openclaw", "version"],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except Exception as e:
        print(f"从 npm 获取最新版本失败: {e}")
    return None

def get_gateway_status():
    """获取 Gateway 状态"""
    try:
        result = subprocess.run(
            ["openclaw", "gateway", "status"],
            capture_output=True,
            text=True,
            timeout=10
        )
        return result.returncode == 0, result.stdout
    except Exception as e:
        return False, str(e)

def load_update_log():
    """加载更新日志"""
    if UPDATE_LOG_FILE.exists():
        try:
            with open(UPDATE_LOG_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"加载更新日志失败: {e}")
    return {
        "lastCheck": None,
        "currentVersion": None,
        "latestVersion": None,
        "updates": []
    }

def save_update_log(log_data):
    """保存更新日志"""
    MEMORY_DIR.mkdir(parents=True, exist_ok=True)
    try:
        with open(UPDATE_LOG_FILE, 'w', encoding='utf-8') as f:
            json.dump(log_data, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"保存更新日志失败: {e}")
        return False

def check_updates():
    """主检查函数"""
    print("=" * 60)
    print("OpenClaw 更新检查")
    print("=" * 60)
    print()
    
    # 加载历史记录
    log_data = load_update_log()
    
    # 获取当前版本
    current_version = get_current_version()
    print(f"当前版本: {current_version or '无法获取'}")
    
    # 获取最新版本
    latest_version = get_latest_version_from_npm()
    print(f"最新版本: {latest_version or '无法获取'}")
    
    # 检查 Gateway 状态
    gateway_ok, gateway_output = get_gateway_status()
    print(f"Gateway 状态: {'运行中' if gateway_ok else '未运行'}")
    
    print()
    
    # 比较版本
    if current_version and latest_version:
        if current_version != latest_version:
            print(f"⚠️  发现新版本: {latest_version}")
            print(f"   当前版本: {current_version}")
            print()
            print("建议操作:")
            print("1. 查看更新日志: https://github.com/openclaw/openclaw/releases")
            print("2. 备份配置文件: cp ~/.config/openclaw/config.yaml ~/.config/openclaw/config.yaml.backup")
            print("3. 执行更新: npm update -g openclaw")
            print()
            
            # 记录更新信息
            update_entry = {
                "date": datetime.now().isoformat(),
                "version": latest_version,
                "type": "version_check",
                "description": f"发现新版本 {latest_version}，当前版本 {current_version}",
                "actionRequired": True
            }
            log_data["updates"].insert(0, update_entry)
        else:
            print(f"✅ 已是最新版本: {current_version}")
    else:
        print("⚠️  无法获取版本信息，请检查 OpenClaw 安装")
    
    # 更新日志
    log_data["lastCheck"] = datetime.now().isoformat()
    log_data["currentVersion"] = current_version
    log_data["latestVersion"] = latest_version
    
    if save_update_log(log_data):
        print(f"\n更新日志已保存: {UPDATE_LOG_FILE}")
    
    print()
    print("=" * 60)
    print("检查完成")
    print("=" * 60)
    
    return log_data

if __name__ == "__main__":
    try:
        check_updates()
    except KeyboardInterrupt:
        print("\n已取消")
        sys.exit(1)
    except Exception as e:
        print(f"检查失败: {e}")
        sys.exit(1)