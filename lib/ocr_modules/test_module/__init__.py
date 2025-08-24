# 测试OCR模块初始化文件

# 从ocr_test_module导入主要类
from .ocr_test_module import OCRTestModule

# 定义模块的公开API
__all__ = [
    'OCRTestModule'
]

# 简单的模块版本信息
__version__ = '0.0.1'

# 模块描述
__description__ = '测试OCR模块，用于调试主系统，无论输入什么图片都返回固定文本'