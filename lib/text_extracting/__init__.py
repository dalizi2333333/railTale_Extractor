# 文本提取模块初始化文件

from .text_extractor import TextExtractor
from .ocr_module_loader import load_ocr_module
from .font_enhancement_detector import detect_font_enhancement

__all__ = ['TextExtractor', 'load_ocr_module', 'detect_font_enhancement']