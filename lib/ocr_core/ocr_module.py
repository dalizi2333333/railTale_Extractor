import os

from lang_manager import LangManager
from config.config_manager import ConfigManager
from .ocr_module_interface import OCRModuleInterface

# 默认OCR模块名称
DEFAULT_MODULE_NAME = 'baidu'

class OCRModule:
    # 单例实例
    _instance = None
    # 模块注册表，合并自OCRModuleRegistry
    _registry = {}

    def __new__(cls, module_name=DEFAULT_MODULE_NAME):
        if cls._instance is None:
            cls._instance = super(OCRModule, cls).__new__(cls)
            # 初始化实例属性
            cls._instance.module_name = module_name
            cls._instance.module_impl = None
            cls._instance._load_module_impl()
        return cls._instance

    @classmethod
    def get_instance(cls, module_name=DEFAULT_MODULE_NAME):
        """获取OCR模块单例实例

        Args:
            module_name (str, optional): 模块名称，默认为DEFAULT_MODULE_NAME

        Returns:
            OCRModule: 单例实例
        """
        if cls._instance is None:
            return cls(module_name)
        return cls._instance

    @classmethod
    def register_module(cls, module_name, module_class):
        """注册OCR模块实现

        Args:
            module_name (str): 模块名称
            module_class (class): 实现OCRModuleInterface接口的模块类

        Raises:
            TypeError: 如果module_class不是OCRModuleInterface的子类
        """
        cls._registry[module_name] = module_class

    @classmethod
    def get_module(cls, module_name):
        """获取OCR模块实现

        Args:
            module_name (str): 模块名称

        Returns:
            class: 注册的模块类

        Raises:
            ValueError: 如果模块未注册
        """
        if module_name not in cls._registry:
            raise ValueError(f"OCR模块 '{module_name}' 未注册，请先通过ModuleBootstraper引导模块")
        return cls._registry[module_name]

    @classmethod
    def list_modules(cls):
        """列出所有已注册的OCR模块

        Returns:
            list: 已注册模块名称的列表
        """
        return list(cls._registry.keys())

    @classmethod
    def register_ocr_module(cls, module_name):
        """装饰器，用于注册OCR模块实现

        Args:
            module_name (str): 模块名称

        Returns:
            function: 装饰器函数，用于注册模块类
        """
        def decorator(module_class):
            cls.register_module(module_name, module_class)
            return module_class
        return decorator

    
    """OCR模块的主类，负责加载和管理不同的OCR实现"""

    def __init__(self, module_name=DEFAULT_MODULE_NAME):
        # 防止直接实例化，确保通过get_instance获取
        pass

    def _load_module_impl(self):
        """加载OCR模块实现

        从_registry中获取模块类，创建实例并初始化

        Returns:
            bool: 加载成功返回True，失败返回False
        """
        try:
            module_class = self.get_module(ConfigManager.get('OCR_MODULE', DEFAULT_MODULE_NAME))
            self.module_impl = module_class()
        except ValueError as e:
            print(LangManager.get_lang('ocr_module_load_fail').format(ConfigManager.get('OCR_MODULE', DEFAULT_MODULE_NAME), str(e)))
            self.module_impl = None

    def init_ocr_client(self):
        """初始化OCR客户端

        Returns:
            bool: 初始化成功返回True，模块未加载或初始化失败返回False
        """
        if self.module_impl is None:
            return False
        return self.module_impl.init_ocr_client()

    def recognize_text(self, image_path):
        """识别图片中的文本

        Args:
            image_path (str): 图片文件路径

        Returns:
            str: 识别出的文本，模块未加载或识别失败时返回None
        """
        if self.module_impl is None:
            return None
        return self.module_impl.recognize_text(image_path)

    def get_recognition_debug_info(self):
        """获取上一次OCR识别的完整调试信息条目

        Returns:
            str: 格式化的调试信息字符串，包含文件名、识别模式、识别文本和详细调试信息
                模块未加载时返回空字符串
        """
        if self.module_impl is None:
            return ""
        return self.module_impl.get_recognition_debug_info()

    # generate_debug_entry方法已移除，调试信息获取方式已整合到get_recognition_debug_info中

    def get_api_delay(self):
        """获取API调用之间的延迟时间(秒)

        Returns:
            float: API调用之间的延迟时间(秒)，模块未加载时返回默认值1.5秒
        """
        if self.module_impl is None:
            return 1.5  # 默认返回1.5秒
        return self.module_impl.get_api_delay()

    def get_max_width(self):
        """获取OCR模块支持的最大图片宽度(像素)

        Returns:
            int: 支持的最大图片宽度(像素)，模块未加载时返回默认值8192像素
        """
        if self.module_impl is None:
            return 8192  # 默认返回8192像素
        return self.module_impl.get_max_width()

    def get_max_height(self):
        """获取OCR模块支持的最大图片高度(像素)

        Returns:
            int: 支持的最大图片高度(像素)，模块未加载时返回默认值8192像素
        """
        if self.module_impl is None:
            return 8192  # 默认返回8192像素
        return self.module_impl.get_max_height()