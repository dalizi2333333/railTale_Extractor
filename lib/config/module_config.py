from .base_config import MODULE_CONFIG_REGISTRY


def register_module_config(module_name, config_definitions, config_path=None):
    """注册模块配置定义

    Args:
        module_name (str): 模块名称
        config_definitions (dict): 配置定义字典
        config_path (str, optional): 模块配置文件路径
    """
    # 创建一次ConfigLoader实例
    from .config_loader import ConfigLoader
    loader = ConfigLoader()
    lang_data = loader._lang_data

    if module_name not in MODULE_CONFIG_REGISTRY:
        MODULE_CONFIG_REGISTRY[module_name] = {
            'definitions': config_definitions,
            'path': config_path
        }
        print(lang_data.get("module_config_registered").format(module_name))
    else:
        print(lang_data.get("module_config_overwritten").format(module_name))
        MODULE_CONFIG_REGISTRY[module_name] = {
            'definitions': config_definitions,
            'path': config_path
        }