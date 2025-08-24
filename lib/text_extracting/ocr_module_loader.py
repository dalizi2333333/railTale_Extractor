import sys
import time
from lib.config.config_manager import ConfigManager
from lib.ocr_core.ocr_module import OCRModule, DEFAULT_MODULE_NAME
from lib.text_extracting.font_enhancement_detector import detect_font_enhancement

def load_ocr_module():
    """加载OCR模块并初始化相关配置
    
    该方法会检测字体增强，设置OCR选项，并将选项OCR_OPTIONS存入配置系统。
    """
    # 检测字体增强
    detect_font_enhancement()
    
    # 获取字体增强相关配置
    use_custom_font = ConfigManager.get('USE_CUSTOM_FONT', False)
    font_path = ConfigManager.get('CUSTOM_FONT_PATH', None)
    ocr_language = ConfigManager.get('OCR_LANGUAGE', 'zh-cn')
    
    # 设置OCR选项
    options = {
        'language_type': ocr_language,
        'detect_direction': 'true',      # 检测方向
        'detect_language': 'true',       # 检测语言
        'probability': 'true',           # 返回置信度
        'paragraph': 'true'              # 段落合并
    }
    
    # 根据是否使用自定义字体设置OCR参数
    if use_custom_font:
        options['accuracy'] = 'high'  # 高精度模式
        options['font_type'] = 'custom'
        options['custom_font_path'] = font_path
    else:
        options['font_type'] = 'simhei'  # 设置为常见中文字体(黑体)
    
    # 将选项存入配置系统
    ConfigManager.set('OCR_OPTIONS', options)
    
    # 获取OCR模块单例实例
    ocr_module = OCRModule.get_instance()
    
    return ocr_module