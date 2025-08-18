import importlib
from lib.bootstrap import LocalizationManager

class OCRModuleRegistry:
    """OCR模块注册器，用于管理和加载不同的OCR模块实现"""

    _registry = {}

    @classmethod
    def register_module(cls, module_name, module_class):
        """注册OCR模块实现"""
        cls._registry[module_name] = module_class

    @classmethod
    def get_module(cls, module_name):
        """获取OCR模块实现"""
        if module_name not in cls._registry:
            # 尝试动态导入模块
            try:
                module_path = f'lib.ocr_modules.{module_name}.{module_name}_ocr_module'
                module = importlib.import_module(module_path)
                module_class = getattr(module, f'{module_name.capitalize()}OCRModule')
                cls.register_module(module_name, module_class)
            except (ImportError, AttributeError) as e:
                loc_manager = LocalizationManager()
                raise ValueError(loc_manager.get_lang_data()['ocr_module_not_found'].format(module_name, str(e)))
        return cls._registry[module_name]

    @classmethod
    def list_modules(cls):
        """列出所有已注册的OCR模块"""
        return list(cls._registry.keys())


def register_ocr_module(module_name):
    """装饰器，用于注册OCR模块实现"""
    def decorator(module_class):
        OCRModuleRegistry.register_module(module_name, module_class)
        return module_class
    return decorator