import os
import json
import datetime
from ocr_core.ocr_module_interface import OCRModuleInterface
from lang_manager import LangManager

class OCRTestModule(OCRModuleInterface):
    """测试OCR模块实现，用于调试主系统"""

    def __init__(self):
        self.last_image_path = None
        self.last_recognized_text = "剧情梗概\n这是固定的测试文本\n用于调试OCR模块\n无论输入什么图片都会返回这段文字\n取消"
        self.last_recognition_debug_info = {}
        self.ocr_OCR_MODULE = None

    def init_ocr_client(self):
        """初始化测试OCR客户端"""
        from config.config_manager import ConfigManager
        self.ocr_OCR_MODULE = ConfigManager.get('OCR_MODULE')
        
        # 获取并打印ConfigManager中的所有实际配置项
        from config.config_manager import ConfigManager
        all_config = ConfigManager.get_config()
        print("=== ConfigManager中的所有实际配置项 ===")
        print(json.dumps(all_config, ensure_ascii=False, indent=2))
        
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
        
        # 确保OCR客户端已初始化
        if not hasattr(self, '_client_initialized') or not self._client_initialized:
            self._client_initialized = self.init_ocr_client()

        # 获取ConfigManager中的所有实际配置项
        from config.config_manager import ConfigManager
        app_config = ConfigManager.get_config()
        
        # 检测语言文件中的'test_mode_desc'键
        test_mode_desc = LangManager.get_module_lang_data().get('test_mode_desc', '未找到test_mode_desc描述')
        
        # 获取当前时间
        current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # 收集调试信息
        self.last_recognition_debug_info = {
            'image_path': image_path,
            'config': app_config,
            'timestamp': current_time,
            'TEST_MODE_DESC': test_mode_desc
        }
        
        # 打印ConfigManager中的所有实际配置项
        print("=== 测试模块使用的所有实际配置项 ===")
        print(json.dumps(app_config, ensure_ascii=False, indent=2))
        
        # 打印关键配置项
        print("=== 测试模块关键配置项 ===")
        print(f"OCR_MODULE: {self.ocr_OCR_MODULE}")
        print(f"TEST_MODE_DESC: {test_mode_desc}")
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

        debug_message = (
            f"=== 测试OCR模块调试信息 ===\n"
            f"文件名: {file_name}\n"
            f"识别文本: {self.last_recognized_text}\n\n"
            f"完整配置表:\n{config_str}\n\n"
            f"测试模式描述: {debug_info.get('TEST_MODE_DESC', '未设置')}\n"
            f"时间戳: {debug_info.get('timestamp', '未知')}\n"
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