import os
import json
from lib.lang_manager import LocalizationManager
from lib.config.config_manager import ConfigManager

# 百度OCR模块的bootstrap.py
# 此文件由ModuleBootstraper加载和使用，负责模块的依赖管理、配置和初始化


def get_required_dependencies():
    """
    返回模块需要的额外依赖
    这些依赖不会被自动安装，需要用户手动安装或通过依赖管理工具安装
    
    Returns:
        dict: 包含依赖名称和版本要求的字典
    """
    return {
        'baidu-aip': '>=4.0.0'
    }


def get_required_config_items():
    """
    返回模块需要的配置项
    这些配置项将被添加到配置文件中
    
    Returns:
        dict: 包含配置项名称、类型、默认值和描述的字典
    """
    # 获取语言数据
    loc_manager = LocalizationManager.get_instance()
    lang_data = loc_manager.get_lang_data()
    
    return {
        'baidu_app_id': {
            'type': 'str',
            'default': 'your_app_id',
            'description': lang_data.get('baidu_app_id_desc', '百度OCR应用的APP ID')
        },
        'baidu_api_key': {
            'type': 'str',
            'default': 'your_api_key',
            'description': lang_data.get('baidu_api_key_desc', '百度OCR应用的API Key')
        },
        'baidu_secret_key': {
            'type': 'str',
            'default': 'your_secret_key',
            'description': lang_data.get('baidu_secret_key_desc', '百度OCR应用的Secret Key')
        },
        'test_mode': {
            'type': 'bool',
            'default': False,
            'description': lang_data.get('test_mode_desc', '是否启用测试模式，测试模式下不会真正调用百度API')
        },
        'simulated_ocr_text': {
            'type': 'str',
            'default': '这是模拟的OCR识别结果文本',
            'description': lang_data.get('simulated_ocr_text_desc', '测试模式下返回的模拟OCR文本')
        }
    }


def has_mandatory_config():
    """
    返回模块是否有不可为默认值的配置项
    如果返回True，当根据complete_module方法补全模块后，程序会退出并提醒用户修改配置
    
    Returns:
        bool: 是否有不可为默认值的配置项
    """
    return True


def complete_module():
    """
    补全模块的方式
    负责初始化模块所需的语言文件和其他资源
    
    Returns:
        bool: 是否补全成功
    """
    try:
        # 获取模块目录
        config_manager = ConfigManager.get_instance()
        module_dir, _ = config_manager.get_ocr_module_dir('baidu')
        
        # 检查并创建lang目录
        lang_dir = os.path.join(module_dir, 'lang')
        if not os.path.exists(lang_dir):
            os.makedirs(lang_dir, exist_ok=True)
            print(f'创建语言目录: {lang_dir}')
        
        # 检查语言文件是否存在，如果不存在则创建默认语言文件
        languages = ['zh-cn', 'en']
        for lang in languages:
            lang_file = os.path.join(lang_dir, f'{lang}.json')
            if not os.path.exists(lang_file):
                # 创建默认语言文件
                default_lang_data = {
                    'baidu_config_load_fail': '加载百度OCR配置失败',
                    'baidu_config_invalid': '百度OCR配置无效',
                    'check_config_file': '请检查配置文件中的APP_ID、API_KEY和SECRET_KEY',
                    'aip_module_not_found': '未找到aip模块',
                    'install_baidu_aip': '请安装: pip install baidu-aip',
                    'baidu_client_init_fail': '初始化百度OCR客户端失败',
                    'baidu_lang_file_load_fail': '加载百度OCR语言文件失败',
                    'ocr_recognition_fail': 'OCR识别失败',
                    'ocr_recognition_error': 'OCR识别过程中出错',
                    'baidu_app_id_desc': '百度OCR应用的APP ID',
                    'baidu_api_key_desc': '百度OCR应用的API Key',
                    'baidu_secret_key_desc': '百度OCR应用的Secret Key',
                    'test_mode_desc': '是否启用测试模式，测试模式下不会真正调用百度API',
                    'simulated_ocr_text_desc': '测试模式下返回的模拟OCR文本'
                }
                
                # 如果是英文，使用英文翻译
                if lang == 'en':
                    default_lang_data = {
                        'baidu_config_load_fail': 'Failed to load Baidu OCR configuration',
                        'baidu_config_invalid': 'Baidu OCR configuration is invalid',
                        'check_config_file': 'Please check APP_ID, API_KEY and SECRET_KEY in configuration file',
                        'aip_module_not_found': 'aip module not found',
                        'install_baidu_aip': 'Please install: pip install baidu-aip',
                        'baidu_client_init_fail': 'Failed to initialize Baidu OCR client',
                        'baidu_lang_file_load_fail': 'Failed to load Baidu OCR language file',
                        'ocr_recognition_fail': 'OCR recognition failed',
                        'ocr_recognition_error': 'Error during OCR recognition',
                        'baidu_app_id_desc': 'APP ID of Baidu OCR application',
                        'baidu_api_key_desc': 'API Key of Baidu OCR application',
                        'baidu_secret_key_desc': 'Secret Key of Baidu OCR application',
                        'test_mode_desc': 'Whether to enable test mode, which does not actually call Baidu API',
                        'simulated_ocr_text_desc': 'Simulated OCR text returned in test mode'
                    }
                
                with open(lang_file, 'w', encoding='utf-8') as f:
                    json.dump(default_lang_data, f, ensure_ascii=False, indent=2)
                print(f'创建默认语言文件: {lang_file}')
        
        return True
    except Exception as e:
        print(f'补全百度OCR模块失败: {str(e)}')
        return False


# 模块初始化代码
if __name__ == '__main__':
    # 当直接运行此文件时，可以用于测试模块补全功能
    complete_module()
    print('百度OCR模块bootstrap完成')