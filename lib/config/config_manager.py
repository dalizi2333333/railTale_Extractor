import os
import sys
from lang_manager import LangManager

# 尝试导入bootstrap模块
library_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if library_dir not in sys.path:
    sys.path.append(library_dir)

class ConfigManager:
    """配置管理器类，单例模式，封装配置管理"""
    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ConfigManager, cls).__new__(cls)
            cls._instance._paths = {}
            cls._instance._config = {}
            cls._instance._ocr_module_dir_cache = {}
        return cls._instance

    @classmethod
    def get_instance(cls):
        """获取配置管理器单例实例

        Returns:
            ConfigManager: 配置管理器实例
        """
        return cls()

    @classmethod
    def initialize(cls, paths=None):
        """初始化配置管理器

        Args:
            paths (dict, optional): 路径配置字典. Defaults to None.
        """
        instance = cls.get_instance()
        if not cls._initialized:
            # 存储路径配置
            instance._paths = paths or {}
            cls._initialized = True
        return instance

    @classmethod
    def get(cls, key, default=None):
        """获取配置项

        Args:
            key (str): 配置项键名
            default: 默认值

        Returns:
            配置项值或默认值
        """
        return cls()._config.get(key, default)

    @classmethod
    def set(cls, key, value):
        """设置配置项

        Args:
            key (str): 配置项键名
            value: 配置项值
        """
        cls()._config[key] = value

    @classmethod
    def get_config(cls):
        """获取完整配置

        Returns:
            dict: 配置字典
        """
        return cls()._config

    @classmethod
    def get_process_dir(cls):
        """获取处理目录路径

        Returns:
            str: 处理目录路径
        """
        return cls()._paths.get('process_dir')

    @classmethod
    def get_parent_dir(cls):
        """获取父目录路径

        Returns:
            str: 父目录路径
        """
        return cls()._paths.get('parent_dir')

    @classmethod
    def get_project_download_url(cls):
        """获取项目下载URL

        Returns:
            str: 项目下载URL
        """
        return cls()._paths.get('project_download_url')

    @classmethod
    def get_ocr_module_dir(cls, module_name):
        """获取OCR模块目录路径

        Args:
            module_name (str): OCR模块名称

        Returns:
            tuple: (模块目录路径, 是否为新创建的目录)
        """
        instance = cls.get_instance()
        # 检查缓存
        if module_name in instance._ocr_module_dir_cache:
            module_dir, _ = instance._ocr_module_dir_cache[module_name]
            return module_dir, False  # 第二次调用时is_newly_created始终为False
        
        # 确保模块名称有效
        if not module_name or not isinstance(module_name, str):
            raise ValueError(LangManager.get_lang('module_name_not_valid'))
            
        # 检查并创建ocr_modules目录
        lib_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        ocr_modules_dir = os.path.join(lib_dir, 'ocr_modules')
        is_newly_created = False
        
        if not os.path.exists(ocr_modules_dir):
            try:
                os.makedirs(ocr_modules_dir)
                is_newly_created = True
            except Exception as e:
                raise Exception(LangManager.get_lang('cannot_create_ocr_modules_dir').format(str(e)))
                
        # 检查并创建模块目录
        module_dir = os.path.join(ocr_modules_dir, module_name)
        if not os.path.exists(module_dir):
            try:
                os.makedirs(module_dir)
                is_newly_created = True
            except Exception as e:
                raise Exception(LangManager.get_lang('cannot_create_module_dir').format(module_name, str(e)))
                
        # 存入缓存
        instance._ocr_module_dir_cache[module_name] = (module_dir, is_newly_created)
            
        return module_dir, is_newly_created

# 全局配置实例，将在bootstrap中初始化
config_manager = None