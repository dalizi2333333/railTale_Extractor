import os
import json
from ocr_core.ocr_module_interface import OCRModuleInterface
from ocr_modules.baidu.debug_utils import BaiduOCRDebugUtils
from config.config_manager import ConfigManager
from aip import AipOcr
from lang_manager import LangManager

class BaiduOCRModule(OCRModuleInterface):
    """百度OCR模块实现"""

    # 通用语言代码到百度OCR API语言类型的映射
    LANGUAGE_MAP = {
        'zh-cn': 'CHN_ENG',  # 中文简体+英文
        'zh-tw': 'CHN_ENG',  # 中文繁体+英文
        'en': 'ENG',         # 英文
        'ja': 'JAP',         # 日语
        'ko': 'KOR',         # 韩语
        'fr': 'FRE',         # 法语
        'es': 'SPA',         # 西班牙语
        'pt': 'POR',         # 葡萄牙语
        'de': 'GER',         # 德语
        'it': 'ITA',         # 意大利语
        'ru': 'RUS'          # 俄语
    }

    def __init__(self):
        self.app_id = None
        self.api_key = None
        self.secret_key = None
        self.ocr_client = None
        self.last_recognition_debug_info = {}
        self.last_recognized_text = None
        self.last_image_path = None
        self.ocr_options = None

    def init_ocr_client(self):
        """初始化百度OCR客户端和特有选项"""
        try:
            if self.app_id is None or self.api_key is None or self.secret_key is None:
                self.app_id = ConfigManager.get('BAIDU_APP_ID', '')
                self.api_key = ConfigManager.get('BAIDU_API_KEY', '')
                self.secret_key = ConfigManager.get('BAIDU_SECRET_KEY', '')

            # 创建OCR客户端
            self.ocr_client = AipOcr(self.app_id, self.api_key, self.secret_key)

            # 初始化OCR选项
            self._init_ocr_options()

            return True
        except Exception as e:
            print(f"初始化百度OCR客户端失败: {str(e)}")
            return False

    def _init_ocr_options(self):
        """初始化百度OCR特有选项"""
        # 获取字体增强相关配置
        use_custom_font = ConfigManager.get('USE_CUSTOM_FONT', False)
        font_path = ConfigManager.get('CUSTOM_FONT_PATH', None)
        ocr_language = ConfigManager.get('OCR_LANGUAGE', 'zh-cn')

        # 设置基础OCR选项
        options = {
            'language_type': ocr_language
        }

        # 处理字体类型相关设置
        if use_custom_font:
            options['font_type'] = 'custom'
            options['custom_font_path'] = font_path
        else:
            options['font_type'] = 'simhei'  # 设置为常见中文字体(黑体)

        # 添加百度API特有参数
        default_options = {
            'detect_direction': 'true',      # 检测方向
            'detect_language': 'true',       # 检测语言
            'probability': 'true',           # 返回置信度
            'paragraph': 'true',             # 段落合并
            'accuracy': 'high'               # 默认使用高精度模式
        }

        # 合并选项
        default_options.update(options)

        # 转换语言代码
        language_type = default_options.get('language_type', 'zh-cn')
        baidu_language = self.LANGUAGE_MAP.get(language_type, 'CHN_ENG')
        default_options['language_type'] = baidu_language

        # 存储到实例属性
        self.ocr_options = default_options

    def recognize_text(self, image_path):
        """使用百度OCR识别图片中的文本

        Args:
            image_path (str): 图片文件路径

        Returns:
            str: 识别出的文本，失败时返回None
        """
        from config.config_manager import ConfigManager
        if self.ocr_client is None:
            if not self.init_ocr_client():
                return None

        try:
            with open(image_path, 'rb') as f:
                image_data = f.read()

            # 使用实例属性中的OCR选项
            default_options = self.ocr_options.copy()

            # 调用百度OCR API识别文本
            if default_options.get('accuracy') == 'high':
                # 高精度模式
                result = self.ocr_client.basicAccurate(image_data, default_options)
            else:
                # 通用模式
                result = self.ocr_client.basicGeneral(image_data, default_options)

            # 收集调试信息
            self.last_recognition_debug_info = {
                'options': default_options,
                'result': result,
                'image_path': image_path
            }
            self.last_image_path = image_path

            # 处理识别结果
            if 'words_result' in result:
                text = '\n'.join([item['words'] for item in result['words_result']])
                self.last_recognized_text = text
                return text
            else:
                error_msg = result.get('error_msg', '识别失败')
                print(LangManager.get_module_lang_data()['recognize_fail'].format(error_msg))
                self.last_recognized_text = None
                return None
        except Exception as e:
            print(LangManager.get_module_lang_data()['recognize_error'].format(str(e)))
            self.last_recognized_text = None
            return None

    def get_recognition_debug_info(self):
        """获取上一次OCR识别的完整调试信息条目

        Returns:
            str: 格式化的调试信息字符串，包含文件名、识别模式、识别文本和详细调试信息
        """
        from config.config_manager import ConfigManager
        if not self.last_recognition_debug_info or not self.last_recognized_text:
            return ""

        # 获取配置
        use_custom_font = ConfigManager.get('USE_CUSTOM_FONT', False)

        # 提取文件名
        file_name = os.path.basename(self.last_image_path)

        # 生成调试信息条目
        debug_info = self.last_recognition_debug_info
        return BaiduOCRDebugUtils.generate_debug_entry(
            file_name, use_custom_font, self.last_recognized_text, debug_info
        )

    # generate_debug_entry方法已移除，调试信息生成逻辑已整合到get_recognition_debug_info中
    def get_api_delay(self):
        """获取API调用之间的延迟时间(秒)

        Returns:
            float: API调用之间的延迟时间，固定为1.5秒
        """
        return 1.5  # 固定值

    def get_max_width(self):
        """获取OCR模块支持的最大图片宽度(像素)

        Returns:
            int: 支持的最大图片宽度，固定为8192像素
        """
        return 8192  # 固定值

    def get_max_height(self):
        """获取OCR模块支持的最大图片高度(像素)

        Returns:
            int: 支持的最大图片高度，固定为8192像素
        """
        return 8192  # 固定值