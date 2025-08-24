from abc import ABC, abstractmethod

class OCRModuleInterface(ABC):
    """OCR模块接口基类，定义了所有OCR模块都需要实现的方法"""

    @abstractmethod
    def init_ocr_client(self):
        """初始化OCR客户端

        Returns:
            bool: 初始化成功返回True，失败返回False
        """
        pass

    @abstractmethod
    def recognize_text(self, image_path):
        """识别图片中的文本

        Args:
            image_path (str): 图片文件路径

        Returns:
            str: 识别出的文本，失败时返回None
        """
        pass

    @abstractmethod
    def get_recognition_debug_info(self):
        """获取上一次OCR识别的完整调试信息条目

        Returns:
            str: 格式化的调试信息字符串，包含文件名、识别模式、识别文本和详细调试信息
        """
        pass

    @abstractmethod
    def get_api_delay(self):
        """获取API调用之间的延迟时间(秒)

        Returns:
            float: API调用之间的延迟时间(秒)
        """
        pass

    @abstractmethod
    def get_max_width(self):
        """获取OCR模块支持的最大图片宽度(像素)

        Returns:
            int: 支持的最大图片宽度(像素)
        """
        pass

    @abstractmethod
    def get_max_height(self):
        """获取OCR模块支持的最大图片高度(像素)

        Returns:
            int: 支持的最大图片高度(像素)
        """
        pass