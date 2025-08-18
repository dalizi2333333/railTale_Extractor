import os
import json

class BaiduOCRLangUtils:
    """百度OCR语言工具类"""

    @staticmethod
    def load_language_data(lang_file_path=None):
        """加载百度OCR语言数据"""
        try:
            if lang_file_path is None:
                # 使用LocalizationManager获取当前语言文件
                from lib.bootstrap import LocalizationManager
                loc_manager = LocalizationManager.get_instance()
                current_lang_file = loc_manager.get_current_language_file()
                # 默认语言文件路径
                lang_dir = os.path.join(os.path.dirname(__file__), 'lang')
                # 尝试加载当前语言对应的json文件
                lang_file_path = os.path.join(lang_dir, current_lang_file)

            with open(lang_file_path, 'r', encoding='utf-8') as f:
                lang_data = json.load(f)
            return lang_data
        except Exception as e:
            print(f"加载百度OCR语言文件失败: {str(e)}")
            return {}