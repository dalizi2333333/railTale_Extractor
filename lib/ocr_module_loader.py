import sys
from lib.config.config_manager import ConfigManager
from lib.font_enhancement import detect_font_enhancement
from lib.ocr_core.ocr_module import create_ocr_module, DEFAULT_MODULE_NAME
from lib.bootstrap import LocalizationManager

# 获取本地化管理器实例
loc_manager = LocalizationManager.get_instance()

class OCRModuleLoader:
    """OCR模块加载器，负责OCR模块的加载和初始化"""

    def __init__(self, parent_dir):
        self.parent_dir = parent_dir
        self.ocr_module = None
        self.use_custom_font = False
        self.font_path = None
        self.ocr_language = None
        self.found_fonts = None
        self.module_name = None
        self.config = None
        
    def pre_register_module_dependencies(self):
        """预注册OCR模块依赖，在依赖检查前调用"""
        from lib.dependency_check import dependency_checker
        
        # 加载配置以确定使用哪个OCR模块
        if self.config is None:
            self.config = self.load_config()
            
        self.module_name = self.config.get('ocr_module', DEFAULT_MODULE_NAME)
        
        # 为baidu模块注册依赖
        # 动态导入模块依赖注册函数
        try:
            # 构建模块路径和注册函数名称
            module_path = f'lib.ocr_modules.{self.module_name}'
            register_func_name = f'register_{self.module_name}_dependencies'
            
            # 尝试导入模块
            module = __import__(module_path, fromlist=[register_func_name])
            register_func = getattr(module, register_func_name, None)
            
            # 如果找到注册函数，则调用
            if register_func:
                register_func(dependency_checker)
        except ImportError:
            # 模块不存在，ocr_core会处理自动下载
            pass
            
        return True

    def initialize_font_enhancement(self, ocr_language='default'):
        """初始化字体增强设置"""
        self.use_custom_font, self.font_path, self.ocr_language, self.found_fonts = \
            detect_font_enhancement(self.parent_dir, ocr_language)

    def get_font_enhancement_status(self):
        """获取字体增强状态"""
        return self.use_custom_font, self.font_path, self.ocr_language, self.found_fonts

    def load_config(self):
        """加载配置"""
        config_manager = ConfigManager()
        return config_manager.get_config()

    def initialize_ocr_module(self, config=None):
        """初始化OCR模块"""
        if config is None:
            config = self.load_config()

        try:
            # 创建OCR模块实例
            self.ocr_module = create_ocr_module(config.get('OCR_MODULE', DEFAULT_MODULE_NAME))

            if not self.ocr_module:
                print(loc_manager.get_lang_data().get('ocr_module_init_fail', 'OCR模块初始化失败'))
                sys.exit(1)

            # 初始化OCR客户端
            if not self.ocr_module.init_ocr_client():
                print(loc_manager.get_lang_data().get('ocr_client_init_fail', 'OCR客户端初始化失败'))
                sys.exit(1)

            # 检查OCR配置是否完整
            ocr_config = self.ocr_module.get_config()
            if not ocr_config or not self.ocr_module.is_config_valid():
                print(loc_manager.get_lang_data().get('ocr_api_config_prompt', 'OCR API配置不完整，请检查配置文件'))
                sys.exit(1)

            return self.ocr_module

        except Exception as e:
            print(f"{loc_manager.get_lang_data().get('ocr_module_load_error', '加载OCR模块时出错')}: {str(e)}")
            sys.exit(1)

    def get_ocr_module(self):
        """获取OCR模块实例"""
        if self.ocr_module is None:
            self.initialize_ocr_module()
        return self.ocr_module

    def get_options(self):
        """获取OCR识别选项"""
        # 确定OCR语言类型
        # 1. 检查是否同时加载了en.json和zh-cn.ttf
        current_lang_file = loc_manager.get_current_language_file()
        has_en_json = current_lang_file == 'en.json'
        has_zh_cn_ttf = any(font_info['file_name'] == 'zh-cn.ttf' for font_info, _ in self.found_fonts or [])
        
        if has_en_json and has_zh_cn_ttf:
            ocr_language_type = 'ENG'
        elif self.ocr_language:
            ocr_language_type = self.ocr_language
        else:
            # 默认使用本地化管理器提供的OCR语言
            ocr_language_type = loc_manager.get_ocr_language()

        options = {
            'language_type': ocr_language_type,
            'detect_direction': 'true',      # 检测方向
            'detect_language': 'true',       # 检测语言
            'probability': 'true',           # 返回置信度
            'paragraph': 'true'              # 段落合并
        }

        # 根据是否使用自定义字体设置OCR参数
        if self.use_custom_font:
            options['accuracy'] = 'high'  # 高精度模式
            options['font_type'] = 'custom'
            options['custom_font_path'] = self.font_path
        else:
            options['font_type'] = 'simhei'  # 设置为常见中文字体(黑体)

        return options

    def recognize_image(self, image_path):
        """识别图片中的文本并添加必要的延迟"""
        if self.ocr_module is None:
            self.initialize_ocr_module()

        # 使用OCR模块识别文本
        text = self.ocr_module.recognize_text(image_path, self.get_options())

        # 添加延迟以避免QPS限制
        delay = self.ocr_module.get_api_delay()
        print(loc_manager.get_lang_data()['ocr_module_delay_info'].format(delay))
        import time
        time.sleep(delay)

        return text


def load_ocr_module(parent_dir):
    """加载OCR模块的便捷函数"""
    loader = OCRModuleLoader(parent_dir)
    loader.initialize_font_enhancement()
    use_custom_font, font_path, ocr_language, found_fonts = loader.get_font_enhancement_status()
    ocr_module = loader.initialize_ocr_module()
    options = loader.get_options()
    return ocr_module, options, use_custom_font, font_path, found_fonts