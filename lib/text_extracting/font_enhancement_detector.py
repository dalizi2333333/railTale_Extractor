import os
import json
from lib.config.config_manager import ConfigManager
from lib.lang_manager import LangManager

class FontEnhancementDetector:
    """字体增强检测器，负责检测字体文件并提供相应的OCR语言设置

    该类负责检测系统中的字体文件，根据字体类型确定最佳的OCR语言设置，
    以提高特定语言文本的识别准确率。支持多种语言的字体检测和自动切换。

    类变量:
        VALID_OCR_LANGUAGES: 有效的OCR语言类型集合
        DEFAULT_OCR_LANGUAGE: 默认的OCR语言类型
    """
    # 有效的OCR语言类型
    VALID_OCR_LANGUAGES = {
        'auto_detect', 'zh-cn', 'zh-tw', 'en', 'ja-jp', 'ko', 
        'fr', 'es', 'pt', 'de', 'it', 'ru'
    }
    DEFAULT_OCR_LANGUAGE = 'zh-cn'

    def __init__(self):
        """初始化字体增强检测器

        属性初始化:
            loc_manager: 语言管理器实例
            ocr_language_mapping: OCR语言映射表
            font_to_language: 字体到语言的映射
            language_to_fonts: 语言到字体的映射
        """
        # 获取本地化管理器实例
        self.loc_manager = LangManager.get_instance()
        # 缓存语言数据和OCR语言映射
        self.ocr_language_mapping = None
        self.font_to_language = None
        self.language_to_fonts = None
        # 初始化缓存
        self._initialize_cache()

    def _initialize_cache(self):
        """初始化缓存数据

        加载语言数据和字体映射信息，为字体检测做准备。
        如果加载失败，会初始化空的映射表并打印错误信息。
        """
        try:
            self.ocr_language_mapping = LangManager.get_lang_data()['language_mapping']
            try:
                font_file_path = os.path.join(os.path.dirname(__file__), 'font_to_language.json')
                with open(font_file_path, 'r', encoding='utf-8') as f:
                    font_data = json.load(f)
                    self.font_to_language = font_data.get('font_to_language', {})
                    self.language_to_fonts = font_data.get('language_to_font', {})
            except Exception as e:
                error_msg = LangManager.get_lang_data()['font_file_load_error']
                print(error_msg.format(str(e)))
                self.font_to_language = {}
                self.language_to_fonts = {}
        except Exception as e:
            error_msg = LangManager.get_lang_data()['cache_initialization_error']
            print(error_msg.format(str(e)))
            self.ocr_language_mapping = {}
            self.font_to_language = {}

    def detect_font_enhancement(self):
        """检测字体增强并存入配置系统

        该方法是字体检测的主流程，执行以下操作:
        1. 确定当前OCR语言设置
        2. 根据OCR语言查找匹配的字体
        3. 处理默认语言模式下的字体查找
        4. 根据找到的字体设置相关配置

        存入配置系统的选项:
            - USE_CUSTOM_FONT (bool): 是否使用自定义字体
            - CUSTOM_FONT_PATH (str): 字体文件路径，如果未找到则为None
            - OCR_LANGUAGE (str): 确定的OCR语言
            - FIND_FONTS (list): 找到的字体信息列表
        """
        use_custom_font = False
        font_path = None
        original_ocr_language = ConfigManager.get('OCR_LANGUAGE', 'default')
        found_fonts = []

        # 如果ocr_language为default，则使用LangManager获取的语言
        if original_ocr_language == 'default':
            try:
                ocr_language = LangManager.get_lang_data()['language_mapping']
            except Exception as e:
                error_msg = LangManager.get_lang_data()['ocr_language_fetch_error']
                print(error_msg.format(str(e)))
                ocr_language = self.DEFAULT_OCR_LANGUAGE
        else:
            ocr_language = original_ocr_language

        # 1. 对于非default的OCR语言，只查找该语言对应的字体
        if original_ocr_language != 'default':
            matched_font = self._find_font_by_language(ocr_language)
            if matched_font:
                font_file, font_path = matched_font
                use_custom_font = True
                found_fonts.append(({'file_name': font_file, 'ocr_language': self.font_to_language[font_file]}, font_path))
                print(LangManager.get_lang_data()['single_font_detected'].format(font_path))
            # 非default模式下，如果找不到匹配字体，则不启用字体增强
            else:
                print(LangManager.get_lang_data()['no_font_detected_simple'])
        else:
            # 2. 对于default模式，先尝试查找当前语言对应的字体
            matched_font = self._find_font_by_language(ocr_language)
            if matched_font:
                font_file, font_path = matched_font
                use_custom_font = True
                found_fonts.append(({'file_name': font_file, 'ocr_language': self.font_to_language[font_file]}, font_path))
                print(LangManager.get_lang_data()['single_font_detected'].format(font_path))
            else:
                # 3. 如果找不到对应语言的字体，查找所有支持的字体
                found_fonts = self._find_fonts_in_directory()
                
                if len(found_fonts) == 1:
                    font_info, current_font_path = found_fonts[0]
                    use_custom_font = True
                    font_path = current_font_path
                    # 使用找到的字体对应的语言
                    ocr_language = font_info['ocr_language']
                    print(LangManager.get_lang_data()['single_font_detected'].format(font_path))
                elif len(found_fonts) > 1:
                    # 打印多字体警告信息
                    print(LangManager.get_lang_data()['multiple_fonts_warning'])
                else:
                    # 打印无字体检测提示
                    print(LangManager.get_lang_data()['no_font_detected_simple'])
        # 将结果保存到配置系统
        ConfigManager.set('USE_CUSTOM_FONT', use_custom_font)
        ConfigManager.set('CUSTOM_FONT_PATH', font_path)
        ConfigManager.set('OCR_LANGUAGE', ocr_language)
        ConfigManager.set('FIND_FONTS', found_fonts)



    def _find_fonts_in_directory(self):
        """在指定目录中查找支持的字体文件

        Returns:
            list: 找到的字体文件列表，每个元素为(font_info, font_path)元组
        """
        process_dir = ConfigManager.get_process_dir()
        found_fonts = []
        # 遍历支持的字体字典（文件名为键，OCR语言为值）
        for font_file, ocr_language in self.font_to_language.items():
            current_font_path = os.path.join(process_dir, font_file)
            if os.path.exists(current_font_path):
                # 直接使用字体文件名和OCR语言创建font_info
                font_info = {'file_name': font_file, 'ocr_language': ocr_language}
                found_fonts.append((font_info, current_font_path))
        return found_fonts

    def _find_all_fonts_by_language(self, language):
        """根据OCR语言查找所有匹配的字体文件

        Args:
            language (str): OCR语言类型

        Returns:
            list: 找到的字体文件列表，每个元素为(font_info, font_path)元组
        """
        process_dir = ConfigManager.get_process_dir()
        found_fonts = []
        
        # 利用language_to_font进行高效查找
        if language in self.language_to_fonts:
            font_file = self.language_to_fonts[language]
            font_path = os.path.join(process_dir, font_file)
            if os.path.exists(font_path):
                ocr_language = self.font_to_language.get(font_file, '')
                font_info = {'file_name': font_file, 'ocr_language': ocr_language}
                found_fonts.append((font_info, font_path))
        
        return found_fonts

    def _find_font_by_language(self, language):
        """根据OCR语言查找匹配的字体文件

        Args:
            language (str): OCR语言类型

        Returns:
            tuple or None: (font_file, font_path)如果找到匹配的字体，否则None
        """
        process_dir = ConfigManager.get_process_dir()
        # 利用language_to_font进行高效查找
        if language in self.language_to_fonts:
            font_file = self.language_to_fonts[language]
            font_path = os.path.join(process_dir, font_file)
            if os.path.exists(font_path):
                    return (font_file, font_path)
        # 如果language_mapping中没有找到，回退到遍历所有字体
        for font_file, ocr_language in self.font_to_language.items():
            if ocr_language == language:
                font_path = os.path.join(process_dir, font_file)
                if os.path.exists(font_path):
                    return (font_file, font_path)
        return None

# 创建单例实例
font_enhancement_detector = FontEnhancementDetector()

def detect_font_enhancement():
    """检测字体增强并返回相关信息的便捷函数"""
    return font_enhancement_detector.detect_font_enhancement()