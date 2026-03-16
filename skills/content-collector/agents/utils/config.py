#!/usr/bin/env python3
"""
配置管理器 - 加载和管理用户自定义来源
"""

import yaml
from pathlib import Path
from typing import Dict, List, Any


class ConfigManager:
    """配置管理器"""
    
    def __init__(self, config_path=None):
        if config_path is None:
            self.config_path = Path("/workspace/projects/workspace/skills/content-collector/config/sources.yaml")
        else:
            self.config_path = Path(config_path)
        
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """加载YAML配置"""
        if not self.config_path.exists():
            print(f"⚠️ 配置文件不存在: {self.config_path}")
            return {}
        
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f) or {}
        except Exception as e:
            print(f"❌ 加载配置失败: {e}")
            return {}
    
    def get_search_queries(self, kb_key: str) -> List[str]:
        """获取搜索关键词"""
        kb_config = self.config.get(kb_key, {})
        queries = kb_config.get("search_queries", [])
        
        # 如果没有配置，返回默认值
        if not queries:
            defaults = {
                "ai-latest-news": ["AI artificial intelligence latest news"],
                "game-development": ["game development Unity Unreal"],
                "healthy-living": ["health fitness nutrition tips"]
            }
            return defaults.get(kb_key, [])
        
        return queries
    
    def get_authoritative_sources(self, kb_key: str) -> List[str]:
        """获取权威来源列表"""
        kb_config = self.config.get(kb_key, {})
        return kb_config.get("authoritative_sources", [])
    
    def get_rss_feeds(self, kb_key: str) -> List[Dict[str, str]]:
        """获取RSS订阅源"""
        kb_config = self.config.get(kb_key, {})
        return kb_config.get("rss_feeds", [])
    
    def get_settings(self) -> Dict[str, Any]:
        """获取通用设置"""
        return self.config.get("settings", {})
    
    def get_setting(self, key: str, default=None):
        """获取特定设置"""
        settings = self.get_settings()
        return settings.get(key, default)
    
    def get_quality_threshold(self, threshold_name: str, default=0.5):
        """获取质量阈值"""
        thresholds = self.get_settings().get("quality_thresholds", {})
        return thresholds.get(threshold_name, default)
    
    def is_authoritative_source(self, kb_key: str, source: str) -> bool:
        """检查是否为权威来源"""
        auth_sources = self.get_authoritative_sources(kb_key)
        source_lower = source.lower()
        
        for auth in auth_sources:
            if auth.lower() in source_lower:
                return True
        
        return False
    
    def get_source_weight(self, kb_key: str, source: str) -> float:
        """获取来源质量权重"""
        if self.is_authoritative_source(kb_key, source):
            return self.get_quality_threshold("authoritative_bonus", 0.2)
        return 0.0


# 全局配置实例
_config_instance = None


def get_config() -> ConfigManager:
    """获取全局配置实例"""
    global _config_instance
    if _config_instance is None:
        _config_instance = ConfigManager()
    return _config_instance


def reload_config():
    """重新加载配置"""
    global _config_instance
    _config_instance = ConfigManager()
    return _config_instance


if __name__ == "__main__":
    # 测试配置加载
    config = get_config()
    
    print("AI搜索关键词:")
    for q in config.get_search_queries("ai-latest-news"):
        print(f"  - {q}")
    
    print("\n游戏权威来源:")
    for s in config.get_authoritative_sources("game-development")[:5]:
        print(f"  - {s}")
    
    print(f"\n最低质量阈值: {config.get_quality_threshold('min_confidence')}")
