# 百度OCR模块初始化文件

# 从baidu_ocr_module导入主要类
from .baidu_ocr_module import BaiduOCRModule

# 定义模块的公开API
__all__ = [
    'BaiduOCRModule'
]

# 简单的模块版本信息
__version__ = '0.1.0'

# 模块描述
__description__ = '百度OCR模块，提供基于百度云API的文字识别功能'