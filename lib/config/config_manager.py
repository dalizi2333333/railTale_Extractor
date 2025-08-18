import os
import sys

# 尝试导入bootstrap模块
library_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if library_dir not in sys.path:
    sys.path.append(library_dir)

from .config_loader import ConfigLoader
from .config_generator import ConfigGenerator

class ConfigManager:
    """配置管理器类，作为配置系统的门面，协调配置加载和生成"""
    _instance = None

    def __new__(cls, process_dir=None):
        if cls._instance is None:
            cls._instance = super(ConfigManager, cls).__new__(cls)
            cls._instance._initialize(process_dir)
        return cls._instance

    def _initialize(self, process_dir=None):
        """初始化配置管理器"""
        self._config_loader = ConfigLoader(process_dir=process_dir)
        self._config_generator = ConfigGenerator(process_dir=process_dir)

    def get_config(self):
        """获取配置

        Returns:
            dict: 配置字典

        Raises:
            Exception: 配置读取或生成失败时抛出异常
        """
        return self._config_loader.get_config()

    def get_module_config(self, module_name):
        """获取模块配置

        Args:
            module_name (str): 模块名称

        Returns:
            dict: 模块配置字典
        """
        return self._config_loader.get_module_config(module_name)

    def generate_config(self):
        """生成配置文件

        Raises:
            Exception: 生成配置文件失败时抛出异常
        """
        return self._config_generator.generate_config()

    def generate_module_config(self, module_name):
        """生成模块配置文件

        Args:
            module_name (str): 模块名称

        Raises:
            Exception: 生成模块配置文件失败时抛出异常
        """
        return self._config_generator.generate_module_config(module_name)

    def load_config(self):
        """加载配置文件

        Returns:
            dict: 加载的配置字典

        Raises:
            Exception: 配置读取或生成失败时抛出异常
        """
        return self._config_loader.load_config()

    def load_module_config(self, module_name):
        """加载模块配置

        Args:
            module_name (str): 模块名称

        Returns:
            dict: 模块配置字典
        """
        return self._config_loader.load_module_config(module_name)