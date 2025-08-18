from abc import ABC, abstractmethod

class OCRModuleInterface(ABC):
    """OCR模块接口基类，定义了所有OCR模块都需要实现的方法"""

    @abstractmethod
    def load_config(self, config_path=None):
        """加载OCR模块配置"""
        pass

    @abstractmethod
    def init_ocr_client(self):
        """初始化OCR客户端"""
        pass

    @abstractmethod
    def load_language_data(self, lang_file_path=None):
        """加载OCR模块语言数据"""
        pass

    @abstractmethod
    def recognize_text(self, image_path, options=None):
        """识别图片中的文本"""
        pass

    @abstractmethod
    def get_config(self):
        """获取OCR模块配置"""
        pass

    @abstractmethod
    def is_config_valid(self):
        """检查配置是否有效"""
        pass

    @abstractmethod
    def get_recognition_debug_info(self):
        """获取OCR识别的调试信息"""
        pass

    @abstractmethod
    def get_api_delay(self):
        """获取API调用之间的延迟时间(秒)"""
        pass

    @abstractmethod
    def get_max_width(self):
        """获取OCR模块支持的最大图片宽度(像素)"""
        pass

    @abstractmethod
    def get_max_height(self):
        """获取OCR模块支持的最大图片高度(像素)"""
        pass