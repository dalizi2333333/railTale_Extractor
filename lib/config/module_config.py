from .default_config import DefaultConfig
from lib.lang_manager import LangManager


def register_module_config(module_name, config_definitions, config_path=None):
    """注册模块配置定义

    Args:
        module_name (str): 模块名称
        config_definitions (dict): 配置定义字典
        config_path (str, optional): 模块配置文件路径
    """
    lang_data = LangManager.get_lang_data()

    # 使用DefaultConfig注册模块配置
    DefaultConfig.register_module_config(module_name, config_definitions)
    print(lang_data.get("module_config_registered").format(module_name))

# 保持向后兼容性
MODULE_CONFIG_REGISTRY = DefaultConfig.MODULE_CONFIG_REGISTRY