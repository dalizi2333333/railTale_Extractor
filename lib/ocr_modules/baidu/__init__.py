import os
import sys
from lib.bootstrap import LocalizationManager
from lib.ocr_core.ocr_module import create_ocr_module
from .baidu_ocr_module import BaiduOCRModule, BaiduOCRConfig
from lib.dependency_check import dependency_checker
from lib.config import register_module_config

# 百度OCR模块配置定义
BAIDU_OCR_CONFIG_DEFINITIONS = {
    'BAIDU_APP_ID': {
        'type': 'string',
        'default': 'your_app_id',
        'description': '百度OCR的APP ID',
        'required': True
    },
    'BAIDU_API_KEY': {
        'type': 'string',
        'default': 'your_api_key',
        'description': '百度OCR的API KEY',
        'required': True
    },
    'BAIDU_SECRET_KEY': {
        'type': 'string',
        'default': 'your_secret_key',
        'description': '百度OCR的SECRET KEY',
        'required': True
    },

}

# 注册百度OCR模块配置
module_dir = os.path.dirname(os.path.abspath(__file__))
config_path = os.path.join(module_dir, 'config.txt')
register_module_config('baidu', BAIDU_OCR_CONFIG_DEFINITIONS, config_path)

# 获取本地化管理器实例
loc_manager = LocalizationManager.get_instance()

# 供外部调用的依赖注册函数
def register_baidu_dependencies(dependency_checker):
    """注册百度OCR模块的依赖"""
    dependency_checker.register_module_dependencies('baidu_ocr', [('aip', 'baidu-aip')])
    dependency_checker.register_special_dependency('baidu-aip', 'aip')

# 加载百度OCR配置
def load_baidu_config(config_path=None):
    module = BaiduOCRModule()
    module.load_config(config_path)
    return module.get_config()

# 初始化百度OCR模块
def init_ocr_module(parent_dir):
    # 创建OCR模块实例
    ocr_module = create_ocr_module('baidu')
    
    # 检查百度OCR模块依赖
    if not dependency_checker.check_module_dependencies('baidu_ocr', exit_on_error=True):
        return None
    
    # 初始化OCR客户端
    if not ocr_module.init_ocr_client():
        return None
    
    return ocr_module

# 创建OCR客户端
def create_ocr_client(config):
    module = BaiduOCRModule()
    module.config = config
    return module.init_ocr_client()

# 当直接运行此模块时
if __name__ == '__main__':
    # 加载语言数据
    from .baidu_ocr_module import BaiduOCRModule
    module = BaiduOCRModule()
    module.load_language_data()
    lang_data = module.lang_data
    
    # 初始化
    if 'init_baidu_ocr' in locals():
        init_baidu_ocr(lang_data)
    else:
        print(f"{lang_data.get('function_not_defined', '函数未定义')}: init_baidu_ocr")