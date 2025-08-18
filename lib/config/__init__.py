# 配置包初始化文件

from .base_config import APP_CONFIG_DEFINITIONS, MODULE_CONFIG_REGISTRY, CONFIG_DEFINITIONS
from .config_manager import ConfigManager
from .module_config import register_module_config

# 创建全局配置管理器实例
config_manager = ConfigManager()

def get_config():
    """获取配置的便捷函数

    Returns:
        dict: 配置字典
    """
    return config_manager.get_config()

def get_module_config(module_name):
    """获取模块配置的便捷函数

    Args:
        module_name (str): 模块名称

    Returns:
        dict: 模块配置字典
    """
    return config_manager.get_module_config(module_name)