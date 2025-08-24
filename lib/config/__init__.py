# 配置包初始化文件

from .default_config import CONFIG_DEFINITIONS
from .config_manager import ConfigManager
from .config_ensure import ensure_config
from .config_loader import ConfigLoader
from .config_generator import ConfigGenerator

# 创建全局配置管理器实例
config_manager = ConfigManager()

__all__ = [
    'config_manager',
    'CONFIG_DEFINITIONS',
    'ensure_config',
    'ConfigLoader',
    'ConfigGenerator',
]