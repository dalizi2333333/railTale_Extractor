import importlib
import os
import sys
from lib.lang_manager import LocalizationManager
from lib.ocr_core.ocr_module_interface import OCRModuleInterface

class OCRModuleRegistry:
    """OCR模块注册器，用于管理和加载不同的OCR模块实现"""

    _registry = {}

    @classmethod
    def register_module(cls, module_name, module_class):
        """注册OCR模块实现"""
        cls._registry[module_name] = module_class

    @classmethod
    def _check_module_directory(cls, module_name):
        """检查模块目录是否存在，不存在则创建"""
        loc_manager = LocalizationManager()
        lang_data = loc_manager.get_lang_data()
        
        # 获取模块目录路径
        lib_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        module_dir = os.path.join(lib_dir, 'ocr_modules', module_name)
        
        # 检查目录是否存在
        if not os.path.exists(module_dir):
            print(lang_data['dir_not_found'].format(module_dir))
            os.makedirs(module_dir, exist_ok=True)
            print(lang_data['dir_created'].format(module_dir))
        
        return module_dir

    @classmethod
    def get_module(cls, module_name):
        """获取OCR模块实现，如果模块不存在则尝试创建和初始化"""
        if module_name not in cls._registry:
            # 检查并创建模块目录
            module_dir = cls._check_module_directory(module_name)
            
            # 尝试导入模块的__init__.py
            try:
                # 首先尝试导入模块包
                module_package = importlib.import_module(f'lib.ocr_modules.{module_name}')
                
                # 调用模块的initialize_module方法初始化模块结构
                if hasattr(module_package, 'initialize_module'):
                    print(f"初始化模块 '{module_name}'...")
                    module_package.initialize_module()
                else:
                    print(f"警告: OCR模块 '{module_name}' 没有定义initialize_module方法，可能无法自动补全依赖")
                
                # 尝试导入模块实现类
                module_class_name = f'{module_name.capitalize()}OCRModule'
                module_class = getattr(module_package, module_class_name, None)
                
                # 如果在__init__.py中找不到，尝试从单独的模块文件导入
                if not module_class:
                    module_path = f'lib.ocr_modules.{module_name}.{module_name}_ocr_module'
                    try:
                        module = importlib.import_module(module_path)
                        module_class = getattr(module, module_class_name)
                    except (ImportError, AttributeError):
                        pass
                
                if module_class and issubclass(module_class, OCRModuleInterface):
                    cls.register_module(module_name, module_class)
                else:
                    raise ValueError(f"未找到有效的OCR模块实现类: {module_class_name}")
            except Exception as e:
                loc_manager = LocalizationManager()
                lang_data = loc_manager.get_lang_data()
                error_msg = lang_data.get('ocr_module_not_found', '未找到OCR模块: {}，错误: {}')
                raise ValueError(error_msg.format(module_name, str(e)))
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