from lang_manager import LangManager
from config.config_manager import ConfigManager
from config.config_ensure import ensure_config
from config.config_loader import ConfigLoader
from ocr_core.ocr_module import OCRModule
from text_processor import TextProcessor
from text_extracting.text_extractor import TextExtractor

__all__ = [
    'LangManager',
    'ConfigManager',
    'ensure_config',
    'ConfigLoader',
    'OCRModule',
    'TextProcessor',
    'TextExtractor'
]

__version__ = '0.1.1'

__description__ = '基于崩坏星穹铁道游戏截图的剧情概要提取器'
