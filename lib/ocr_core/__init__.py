# OCR核心模块包
from .ocr_module import OCRModule, create_ocr_module
from .ocr_module_interface import OCRModuleInterface
from .ocr_module_registry import OCRModuleRegistry, register_ocr_module

__all__ = [
    'OCRModule',
    'create_ocr_module',
    'OCRModuleInterface',
    'OCRModuleRegistry',
    'register_ocr_module'
]