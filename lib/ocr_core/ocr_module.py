import os
from .ocr_module_registry import OCRModuleRegistry
from .ocr_module_interface import OCRModuleInterface

# 默认OCR模块名称
DEFAULT_MODULE_NAME = 'baidu'

class OCRModule:
    """OCR模块的主类，负责加载和管理不同的OCR实现"""

    def __init__(self, module_name=DEFAULT_MODULE_NAME):
        from bootstrap import LocalizationManager
        self.loc_manager = LocalizationManager.get_instance()
        self.module_name = module_name
        self.module_impl = self._load_module_impl()

    def _load_module_impl(self):
        """加载OCR模块实现"""
        try:
            module_class = OCRModuleRegistry.get_module(self.module_name)
            return module_class()
        except ValueError as e:
            print(self.loc_manager.get_lang_data()['ocr_module_load_fail'].format(self.module_name, str(e)))
            return None

    def load_config(self, config_path=None):
        """从配置文件加载OCR配置"""
        if self.module_impl is None:
            return False
        return self.module_impl.load_config(config_path)

    def init_ocr_client(self):
        """初始化OCR客户端"""
        if self.module_impl is None:
            return False
        return self.module_impl.init_ocr_client()

    def load_language_data(self, lang_file_path=None):
        """加载OCR模块的语言数据"""
        if self.module_impl is None:
            return False
        return self.module_impl.load_language_data(lang_file_path)

    def recognize_text(self, image_path, options=None):
        """识别图片中的文本"""
        if self.module_impl is None:
            return None
        return self.module_impl.recognize_text(image_path, options)

    def get_config(self):
        """获取OCR模块配置"""
        if self.module_impl is None:
            return None
        return self.module_impl.get_config()

    def is_config_valid(self):
        """检查OCR模块配置是否有效"""
        if self.module_impl is None:
            return False
        return self.module_impl.is_config_valid()

    def get_recognition_debug_info(self):
        """获取OCR识别的调试信息"""
        if self.module_impl is None:
            return {}
        return self.module_impl.get_recognition_debug_info()

    def generate_debug_entry(self, file_name, use_custom_font, text):
        """生成完整的OCR调试信息条目"""
        if self.module_impl is None:
            return self.loc_manager.get_lang_data()['ocr_debug_entry'].format(
                file_name,
                self.loc_manager.get_lang_data()['high_precision'] if use_custom_font else self.loc_manager.get_lang_data()['general'],
                text
            )
        return self.module_impl.generate_debug_entry(file_name, use_custom_font, text)

    def get_api_delay(self):
        """获取API调用之间的延迟时间(秒)"""
        if self.module_impl is None:
            return 1.5  # 默认返回1.5秒
        return self.module_impl.get_api_delay()

    def get_max_width(self):
        """获取OCR模块支持的最大图片宽度(像素)"""
        if self.module_impl is None:
            return 8192  # 默认返回8192像素
        return self.module_impl.get_max_width()

    def get_max_height(self):
        """获取OCR模块支持的最大图片高度(像素)"""
        if self.module_impl is None:
            return 8192  # 默认返回8192像素
        return self.module_impl.get_max_height()

def create_ocr_module(module_name=DEFAULT_MODULE_NAME):
    """创建OCR模块实例"""
    ocr_module = OCRModule(module_name)
    # 加载语言数据
    ocr_module.load_language_data()
    return ocr_module