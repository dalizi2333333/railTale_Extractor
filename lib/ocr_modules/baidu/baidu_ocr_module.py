import os
import json
from lib.ocr_core.ocr_module_interface import OCRModuleInterface
from .debug_utils import BaiduOCRDebugUtils
from .lang_utils import BaiduOCRLangUtils

class BaiduOCRConfig:
    """百度OCR的配置类"""

    def __init__(self, app_id, api_key, secret_key, test_mode=False, simulated_ocr_text=''):
        self.app_id = app_id
        self.api_key = api_key
        self.secret_key = secret_key
        self.test_mode = test_mode
        self.simulated_ocr_text = simulated_ocr_text
        self.api_delay = 1.5  # API调用之间的延迟时间(秒) - 固定值
        self.max_width = 8192  # 最大支持的图片宽度(像素) - 固定值
        self.max_height = 8192  # 最大支持的图片高度(像素) - 固定值

    def get_config(self):
        return {
            'app_id': self.app_id,
            'api_key': self.api_key,
            'secret_key': self.secret_key,
            'test_mode': self.test_mode,
            'simulated_ocr_text': self.simulated_ocr_text
        }

    def is_valid(self):
        # 如果是测试模式，配置视为有效
        if self.test_mode:
            return True
        return all([
            self.app_id and self.app_id != 'your_app_id',
            self.api_key and self.api_key != 'your_api_key',
            self.secret_key and self.secret_key != 'your_secret_key'
        ])


class BaiduOCRModule(OCRModuleInterface):
    """百度OCR模块实现"""

    def __init__(self):
        self.config = None
        self.ocr_client = None
        self.lang_data = {}
        self.last_recognition_debug_info = {}

    def load_config(self, config_path=None):
        """加载百度OCR配置"""
        try:
            from lib.config.config_manager import ConfigManager

            # 使用ConfigManager获取模块配置
            config_manager = ConfigManager()
            module_config = config_manager.get_module_config('baidu')

            # 从模块配置中获取必要的API凭证和测试模式配置
            self.config = BaiduOCRConfig(
                app_id=module_config.get('baidu_app_id', ''),
                api_key=module_config.get('baidu_api_key', ''),
                secret_key=module_config.get('baidu_secret_key', ''),
                test_mode=module_config.get('test_mode', False),
                simulated_ocr_text=module_config.get('simulated_ocr_text', '这是模拟的OCR识别结果文本')
            )
            return self.config is not None
        except Exception as e:
            print(f"{self.lang_data.get('baidu_config_load_fail', '加载百度OCR配置失败')}: {str(e)}")
            return False

    def init_ocr_client(self):
        """初始化百度OCR客户端"""
        try:
            from aip import AipOcr

            if self.config is None:
                if not self.load_config():
                    return False

            if not self.config.is_valid():
                print(f"{self.lang_data.get('baidu_config_invalid', '百度OCR配置无效')}: {self.lang_data.get('check_config_file', '请检查配置文件中的APP_ID、API_KEY和SECRET_KEY')}")
                return False

            config_dict = self.config.get_config()
            self.ocr_client = AipOcr(config_dict['app_id'], config_dict['api_key'], config_dict['secret_key'])
            return True
        except ImportError:
            print(f"{self.lang_data.get('aip_module_not_found', '未找到aip模块')}: {self.lang_data.get('install_baidu_aip', '请安装: pip install baidu-aip')}")
            return False
        except Exception as e:
            print(f"{self.lang_data.get('baidu_client_init_fail', '初始化百度OCR客户端失败')}: {str(e)}")
            return False

    def load_language_data(self, lang_file_path=None):
        """加载百度OCR语言数据"""
        try:
            self.lang_data = BaiduOCRLangUtils.load_language_data(lang_file_path)
            return bool(self.lang_data)
        except Exception as e:
            print(f"{self.lang_data.get('baidu_lang_file_load_fail', '加载百度OCR语言文件失败')}: {str(e)}")
            return False

    def recognize_text(self, image_path, options=None):
        """使用百度OCR识别图片中的文本"""
        if self.ocr_client is None:
            if not self.init_ocr_client():
                return None

        try:
            # 如果是测试模式，直接返回模拟文本
            if self.config.test_mode:
                print(f"百度OCR模块(测试模式): 正在处理图片 {os.path.basename(image_path)}")
                # 收集调试信息
                self.last_recognition_debug_info = {
                    'options': options or {},
                    'result': {'words_result': [{'words': self.config.simulated_ocr_text}]},
                    'image_path': image_path,
                    'test_mode': True
                }
                return self.config.simulated_ocr_text

            with open(image_path, 'rb') as f:
                image_data = f.read()

            # 默认选项
            from lib.lang_manager import LocalizationManager
            loc_manager = LocalizationManager.get_instance()
            default_options = {
                'language_type': loc_manager.get_ocr_language(),
                'detect_direction': 'true',
                'detect_language': 'true',
                'probability': 'true',
                'paragraph': 'true'
            }

            # 合并用户提供的选项
            if options:
                default_options.update(options)

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

            # 处理识别结果
            if 'words_result' in result:
                text = '\n'.join([item['words'] for item in result['words_result']])
                return text
            else:
                error_msg = result.get('error_msg', '识别失败')
                print(f"{self.lang_data.get('ocr_recognition_fail', 'OCR识别失败')}: {error_msg}")
                return None
        except Exception as e:
            print(f"{self.lang_data.get('ocr_recognition_error', 'OCR识别过程中出错')}: {str(e)}")
            return None

    def get_config(self):
        """获取百度OCR配置"""
        return self.config

    def is_config_valid(self):
        """检查百度OCR配置是否有效"""
        return self.config is not None and self.config.is_valid()

    def get_recognition_debug_info(self):
        """获取OCR识别的调试信息，包括原始结果和字块详情"""
        return BaiduOCRDebugUtils.get_recognition_debug_info(self.last_recognition_debug_info)

    def get_max_width(self):
        """获取OCR模块支持的最大图片宽度(像素)"""

        return 8192

    def get_max_height(self):
        """获取OCR模块支持的最大图片高度(像素)"""

        return 8192

    def get_api_delay(self):
        """获取API调用之间的延迟时间(秒)"""

        return 1.5

    def generate_debug_entry(self, file_name, use_custom_font, text):
        """生成完整的OCR调试信息条目"""
        debug_info = self.get_recognition_debug_info()
        return BaiduOCRDebugUtils.generate_debug_entry(
            file_name, use_custom_font, text, self.lang_data, debug_info
        )