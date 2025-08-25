import os
import sys

# 获取库目录并添加到Python路径
library_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if library_dir not in sys.path:
    sys.path.append(library_dir)

from .default_config import DefaultConfig


def ensure_config(module=None):
    """确保配置文件存在

    Args:
        module (str, optional): 模块名称，用于生成模块特定配置

    Returns:
        bool: 配置是否存在
    """
    # 导入所需模块
    from .config_manager import ConfigManager
    from lang_manager import LangManager
    
    config_manager = ConfigManager()
    
    # 确定配置定义和文件路径
    # 使用DefaultConfig获取配置定义（不需要本地化版本）
    config_definitions = DefaultConfig.get_config_definitions(module)
    if not config_definitions:
        raise ValueError(LangManager.get_lang('module_config_definition_not_found').format(module))

    if module is not None:
        # 使用get_ocr_module_dir获取模块路径
        module_dir , is_newly_created = config_manager.get_ocr_module_dir(module)
        config_path = os.path.join(module_dir, 'config.txt')
    else:
        # 从ConfigManager获取处理目录
        process_dir = config_manager.get_process_dir()
        config_path = os.path.join(process_dir, 'config.txt')

    # 检查配置文件是否存在
    if os.path.exists(config_path):
        return True
    else:
        # 配置文件不存在，生成默认配置
        from .config_generator import ConfigGenerator

        # 使用默认配置更新配置管理器
        for key, prop in config_definitions.items():
            ConfigManager.set(key, prop['default'])

        # 初始化配置生成器
        config_generator = ConfigGenerator()

        # 生成默认配置文件
        config_generator.generate_config(module=module)

        return False


if __name__ == '__main__':
    ensure_config()