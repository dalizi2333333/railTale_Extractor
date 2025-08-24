import os
import json

# 测试OCR模块的bootstrap
# 此文件由ModuleBootstraper加载和使用，负责模块的依赖管理、配置和初始化


def get_required_dependencies():
    """
    返回模块需要的额外依赖
    这些依赖不会被自动安装，需要用户手动安装或通过依赖管理工具安装

    Returns:
        dict: 包含依赖信息的字典，格式为 {import_name: {'install_name': install_name, 'version': version}}
    """
    return {}


def get_required_config_items():
    """
    返回模块需要的配置项
    这些配置项将被添加到配置文件中

    Returns:
        dict: 包含配置项名称、类型、默认值和描述的字典
    """
    return {
        'TEST_MODE': {
            'type': 'bool',
            'default': True,
            'description_key': 'test_mode_desc'
        }
    }


def has_mandatory_config():
    """
    返回模块是否有不可为默认值的配置项
    如果返回True，当根据complete_module方法补全模块后，程序会退出并提醒用户修改配置

    Returns:
        bool: 是否有不可为默认值的配置项
    """
    return False


def complete_module():
    """
    补全模块的方式
    负责初始化模块所需的语言文件和其他资源

    Returns:
        bool: 是否补全成功
    """
    # 加载模块语言文件
    from lang_manager import LangManager
    import os
    # 获取当前模块路径
    module_path = os.path.dirname(os.path.abspath(__file__))
    # 调用LangManager加载模块语言文件
    LangManager.load_module_language_file(module_path)
    return True


def get_module_class():
    """
    返回模块的主类
    这个方法会被ModuleBootstraper调用，用于注册模块

    Returns:
        class: 模块的主类
    """
    from .ocr_test_module import OCRTestModule
    return OCRTestModule