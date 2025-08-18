import os
from bootstrap import LocalizationManager

class FontEnhancementDetector:
    """字体增强检测器，负责检测字体文件并提供相应的OCR语言设置"""
    # 有效的OCR语言类型
    VALID_OCR_LANGUAGES = {
        'auto_detect', 'CHN_ENG', 'ENG', 'JAP', 'KOR', 
        'FRE', 'SPA', 'POR', 'GER', 'ITA', 'RUS'
    }
    DEFAULT_OCR_LANGUAGE = 'CHN_ENG'

    def __init__(self):
        """初始化字体增强检测器"""
        # 获取本地化管理器实例
        self.loc_manager = LocalizationManager.get_instance()
        # 缓存语言数据和OCR语言映射
        self.lang_data = None
        self.ocr_language_mapping = None
        self.supported_fonts = None
        # 初始化缓存
        self._initialize_cache()

    def _initialize_cache(self):
        """初始化缓存数据"""
        try:
            self.lang_data = self.loc_manager.get_lang_data()
            self.ocr_language_mapping = self.loc_manager.ocr_language_mapping
            self.supported_fonts = self.ocr_language_mapping.get('supported_fonts', [])
        except Exception as e:
            error_msg = self.lang_data.get('cache_initialization_error', "初始化字体增强检测器缓存时出错: {0}")
            print(error_msg.format(str(e)))
            self.lang_data = {}
            self.ocr_language_mapping = {}
            self.supported_fonts = []

    def detect_font_enhancement(self, parent_dir, ocr_language='default'):
        """检测字体增强并返回相关信息

        Args:
            parent_dir (str): 父目录路径
            ocr_language (str): OCR语言类型，默认为'default'

        Returns:
            tuple: (use_custom_font, font_path, ocr_language, found_fonts)
        """
        # 验证父目录是否存在
        if not os.path.exists(parent_dir):
            error_msg = self.lang_data.get('directory_not_exist_error', "错误: 目录 '{0}' 不存在")
            print(error_msg.format(parent_dir))
            return False, None, self.DEFAULT_OCR_LANGUAGE, []

        use_custom_font = False
        font_path = None
        original_ocr_language = ocr_language

        # 如果ocr_language为default，则使用loc_manager获取的语言
        if ocr_language == 'default':
            try:
                ocr_language = self.loc_manager.get_ocr_language()
            except Exception as e:
                error_msg = self.lang_data.get('ocr_language_fetch_error', "获取OCR语言时出错: {0}")
                print(error_msg.format(str(e)))
                ocr_language = self.DEFAULT_OCR_LANGUAGE

        # 检查父目录中存在的字体文件数量
        found_fonts = self._find_fonts_in_directory(parent_dir)

        # 根据找到的字体文件数量做出决策
        if len(found_fonts) == 1:
            font_info, current_font_path = found_fonts[0]
            use_custom_font = True
            font_path = current_font_path
            # 只有当原始ocr_language是default时，才使用字体语言
            if original_ocr_language == 'default':
                ocr_language = font_info['ocr_language']
            # 打印单字体检测提示
            self._print_single_font_message(font_path)
        elif len(found_fonts) > 1:
            # 打印多字体警告信息
            self._print_multiple_fonts_warning(found_fonts)
        else:
            # 打印无字体检测提示
            self._print_no_font_message()

        # 确保返回有效的OCR语言类型
        ocr_language = self._ensure_valid_ocr_language(ocr_language)

        return use_custom_font, font_path, ocr_language, found_fonts

    def _find_fonts_in_directory(self, parent_dir):
        """在指定目录中查找支持的字体文件

        Args:
            parent_dir (str): 要查找的目录

        Returns:
            list: 找到的字体文件列表，每个元素为(font_info, font_path)元组
        """
        found_fonts = []
        for font_info in self.supported_fonts:
            font_file = font_info['file_name']
            current_font_path = os.path.join(parent_dir, font_file)
            if os.path.exists(current_font_path):
                found_fonts.append((font_info, current_font_path))
        return found_fonts

    def _print_single_font_message(self, font_path):
        """打印单字体检测提示信息

        Args:
            font_path (str): 找到的字体文件路径
        """
        try:
            single_font_msg = self.lang_data.get('single_font_detected', '检测到字体文件: {0}')
            print(single_font_msg.format(font_path))
        except Exception as e:
            error_msg = self.lang_data.get('font_detection_print_error', "打印字体检测信息时出错: {0}")
            print(error_msg.format(str(e)))
            print(f"检测到字体文件: {font_path}")

    def _print_multiple_fonts_warning(self, found_fonts):
        """打印多字体警告信息

        Args:
            found_fonts (list): 找到的字体文件列表
        """
        try:
            warning_msg = self.lang_data.get('multiple_fonts_warning', '警告: 检测到多个字体文件: {0}')
            font_list = ', '.join([font_info['file_name'] for font_info, _ in found_fonts])
            print(warning_msg.format(font_list))
        except Exception as e:
            error_msg = self.lang_data.get('multiple_fonts_warning_print_error', "打印多字体警告信息时出错: {0}")
            print(error_msg.format(str(e)))
            font_list = ', '.join([font_info['file_name'] for font_info, _ in found_fonts])
            print(f"警告: 检测到多个字体文件: {font_list}")

    def _print_no_font_message(self):
        """打印无字体检测提示信息"""
        try:
            no_font_msg = self.lang_data.get('no_font_detected_simple', '未检测到字体文件')
            print(no_font_msg)
        except Exception as e:
            error_msg = self.lang_data.get('no_font_print_error', "打印无字体信息时出错: {0}")
            print(error_msg.format(str(e)))
            default_msg = self.lang_data.get('no_font_detected_default', "未检测到字体文件")
            print(default_msg)

    def _ensure_valid_ocr_language(self, ocr_language):
        """确保OCR语言类型有效

        Args:
            ocr_language (str): OCR语言类型

        Returns:
            str: 有效的OCR语言类型
        """
        if ocr_language in self.VALID_OCR_LANGUAGES:
            return ocr_language
        warning_msg = self.lang_data.get('invalid_ocr_language_warning', "警告: 无效的OCR语言类型 '{0}'，使用默认值 '{1}'")
        print(warning_msg.format(ocr_language, self.DEFAULT_OCR_LANGUAGE))
        return self.DEFAULT_OCR_LANGUAGE

# 创建单例实例
font_enhancement_detector = FontEnhancementDetector()

def detect_font_enhancement(parent_dir, ocr_language='default'):
    """检测字体增强并返回相关信息的便捷函数"""
    return font_enhancement_detector.detect_font_enhancement(parent_dir, ocr_language)