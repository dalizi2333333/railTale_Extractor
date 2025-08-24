import os
import json
import datetime
from ocr_core.ocr_module_interface import OCRModuleInterface
from config.config_manager import ConfigManager
from lang_manager import LangManager

class OCRTestModule(OCRModuleInterface):
    """测试OCR模块实现，用于调试主系统"""

    def __init__(self):
        self.last_image_path = None
        self.last_recognized_text = "这是固定的测试文本\n用于调试OCR模块\n无论输入什么图片都会返回这段文字"
        self.last_recognition_debug_info = {}

    def init_ocr_client(self):
        """初始化测试OCR客户端"""
        # 模拟初始化过程
        print("初始化测试OCR客户端成功")
        return True

    def recognize_text(self, image_path):
        """模拟识别图片中的文本，同时获取和打印实际配置项

        Args:
            image_path (str): 图片文件路径

        Returns:
            str: 固定的测试文本
        """
        self.last_image_path = image_path
        
        # 获取实际配置项
        test_mode = ConfigManager.get('TEST_MODE', False)
        use_custom_font = ConfigManager.get('USE_CUSTOM_FONT', False)
        custom_font_path = ConfigManager.get('CUSTOM_FONT_PATH', None)
        ocr_language = ConfigManager.get('OCR_LANGUAGE', 'zh-cn')
        find_fonts = ConfigManager.get('FIND_FONTS', [])
        
        # 尝试获取default_config.py中的配置项
        try:
            from config.default_config import DefaultConfig
            app_config = DefaultConfig.APP_CONFIG_DEFINITIONS
        except ImportError:
            app_config = {'error': '无法导入DefaultConfig'}
        except AttributeError:
            app_config = {'error': 'DefaultConfig中未找到APP_CONFIG_DEFINITIONS'}
        
        # 检测语言文件中的'test_mode_desc'键
        test_mode_desc = LangManager.get_module_lang_data().get('test_mode_desc', '未找到test_mode_desc描述')
        
        # 获取当前时间
        current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # 收集调试信息
        self.last_recognition_debug_info = {
            'options': {
                'language_type': ocr_language,
                'font_type': 'custom' if use_custom_font else 'simhei',
                'detect_direction': 'true',
                'detect_language': 'true',
                'probability': 'true',
                'paragraph': 'true',
                'accuracy': 'high'
            },
            'result': {
                'words_result': [
                    {'words': '这是固定的测试文本'},
                    {'words': '用于调试OCR模块'},
                    {'words': '无论输入什么图片都会返回这段文字'}
                ],
                'log_id': 123456789,
                'words_result_num': 3
            },
            'image_path': image_path,
            'config': {
                'TEST_MODE': test_mode,
                'TEST_MODE_DESC': test_mode_desc,
                'USE_CUSTOM_FONT': use_custom_font,
                'CUSTOM_FONT_PATH': custom_font_path,
                'OCR_LANGUAGE': ocr_language,
                'FIND_FONTS': find_fonts,
                'APP_CONFIG_DEFINITIONS': app_config,
                'timestamp': current_time
            }
        }
        
        # 打印配置项结果
        print("=== 测试模块配置项结果 ===")
        print(f"TEST_MODE: {test_mode}")
        print(f"TEST_MODE_DESC: {test_mode_desc}")
        print(f"USE_CUSTOM_FONT: {use_custom_font}")
        print(f"CUSTOM_FONT_PATH: {custom_font_path}")
        print(f"OCR_LANGUAGE: {ocr_language}")
        print(f"FIND_FONTS: {find_fonts}")
        print(f"时间戳: {current_time}")
        print("===========================")
        
        return self.last_recognized_text

    def get_recognition_debug_info(self):
        """获取上一次OCR识别的完整调试信息条目

        Returns:
            str: 格式化的调试信息字符串
        """
        if not self.last_recognition_debug_info:
            return "无调试信息可用"

        # 提取文件名
        file_name = os.path.basename(self.last_image_path) if self.last_image_path else "未知文件"

        # 生成调试信息
        debug_info = self.last_recognition_debug_info
        config_str = json.dumps(debug_info['config'], ensure_ascii=False, indent=2)
        options_str = json.dumps(debug_info['options'], ensure_ascii=False, indent=2)
        result_str = json.dumps(debug_info['result'], ensure_ascii=False, indent=2)

        debug_message = (
            f"=== 测试OCR模块调试信息 ===\n"
            f"文件名: {file_name}\n"
            f"识别文本: {self.last_recognized_text}\n\n"
            f"完整配置表:\n{config_str}\n\n"
            f"OCR选项:\n{options_str}\n\n"
            f"识别结果:\n{result_str}\n"
            f"=========================="
        )

        return debug_message

    def get_api_delay(self):
        """获取API调用之间的延迟时间(秒)

        Returns:
            float: 0秒
        """
        return 0.0

    def get_max_width(self):
        """获取OCR模块支持的最大图片宽度(像素)

        Returns:
            int: 8192像素
        """
        return 8192

    def get_max_height(self):
        """获取OCR模块支持的最大图片高度(像素)

        Returns:
            int: 8192像素
        """
        return 8192