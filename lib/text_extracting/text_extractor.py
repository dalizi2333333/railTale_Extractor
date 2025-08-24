import os
import time
from lang_manager import LangManager
from ocr_core.ocr_module import OCRModule
from config.config_manager import ConfigManager
from PIL import Image


class TextExtractor:
    """文本提取器，负责处理OCR识别后的文本

    该类负责接收OCR模块识别的文本，进行过滤、分段和后处理，
    提取有价值的信息，并收集处理过程中的统计数据和调试信息。
    """

    def __init__(self):
        """
        初始化文本提取器

        属性初始化:
            start_markers: 开始记录文本的标记列表
            stop_markers: 停止记录文本的标记列表
            output: 存储处理后的文本输出
            success_count: 成功处理的图片数量
            error_count: 处理失败的图片数量
            suspected_dash_files: 疑似包含破折号问题的文件列表
            ocr_debug_info: 存储OCR调试信息
        """
        self.start_markers = ConfigManager.get('START_MARKERS', [])
        self.stop_markers = ConfigManager.get('STOP_MARKERS', [])
        self.output = []
        self.success_count = 0
        self.error_count = 0
        self.suspected_dash_files = []
        self.ocr_debug_info = []

    def process_text(self, file_name, text):
        """
        处理单张图片的OCR文本

        参数:
            file_name: 图片文件名
            text: OCR识别的文本

        返回:
            str: 处理后的文本，如果处理失败则返回None

        该方法执行以下操作:
        1. 检查文本是否为空
        2. 收集OCR调试信息
        3. 根据开始和停止标记过滤文本
        4. 检测疑似破折号问题
        5. 更新处理统计信息
        """
        if not text:
            error_msg = LangManager.get_lang_data()['ocr_recognition_failed']
            print(error_msg)
            self.output.append(f'{error_msg}\n')
            self.error_count += 1
            return None

        # 获取配置
        use_custom_font = ConfigManager.get('USE_CUSTOM_FONT', False)
        output_ocr_debug = ConfigManager.get('OUTPUT_OCR_DEBUG', False).lower() == 'true'

        # 收集OCR调试信息
        if output_ocr_debug:
            # 获取OCR模块单例实例
            ocr_module = OCRModule.get_instance()
            debug_entry = ocr_module.get_recognition_debug_info()
            if debug_entry:
                self.ocr_debug_info.append(debug_entry + '\n')

        # 分析文本内容
        start_recording = False
        filtered_text = []
        lines = text.split('\n')
        current_paragraph = []

        for line in lines:
            # 打印行内容
            print(LangManager.get_lang_data()['image_line_content'].format(file_name, line))

            # 检查是否到达新的开始记录点
            if any(marker in line for marker in self.start_markers) and not start_recording:
                start_recording = True
                # 找出实际匹配的标记
                matched_marker = next(marker for marker in self.start_markers if marker in line)
                print(LangManager.get_lang_data()['start_recording_text'].format(matched_marker, file_name))
                current_paragraph = []  # 重置当前段落
                continue  # 不记录开始标记本身

            # 检查是否到达停止记录点
            if start_recording:
                if line.strip() in self.stop_markers:
                    start_recording = False  # 重置以便下一次检测
                    print(LangManager.get_lang_data()['stop_recording_text'].format(line, file_name))
                    # 将当前段落添加到过滤文本中（如果不为空且不重复）
                    paragraph_text = ''.join(current_paragraph)
                    if paragraph_text and paragraph_text not in filtered_text:
                        filtered_text.append(paragraph_text)
                else:
                    current_paragraph.append(line)

        # 确保最后一个段落被添加（如果没有遇到停止标记且不为空且不重复）
        paragraph_text = ''.join(current_paragraph)
        if paragraph_text and paragraph_text not in filtered_text:
            filtered_text.append(paragraph_text)

        # 将过滤后的文本块连接
        processed_text = '\n'.join(filtered_text)  # 使用换行符分隔不同段落

        # 去除首尾空白
        processed_text = processed_text.strip()

        # 文本后处理：检测疑似破折号的情况
        if not use_custom_font and '一一' in processed_text:
            print(LangManager.get_lang_data()['suspected_dash_detected'].format(file_name))
            self.suspected_dash_files.append(file_name)

        self.output.append(f'{processed_text}\n')  # 不同图片的内容输出到不同行
        self.success_count += 1
        print(LangManager.get_lang_data()['process_success'].format(file_name))

        return processed_text

    def process_image(self, file_path):
        """
        处理单个图片路径，执行OCR识别和文本处理

        参数:
            file_path: 图片文件路径

        返回:
            dict: 包含处理结果或错误信息的字典
                - 如果成功: {'text': 处理后的文本}
                - 如果失败: {'error': 错误信息}

        该方法执行以下操作:
        1. 检查图片尺寸是否符合要求
        2. 获取OCR模块单例
        3. 使用OCR模块识别文本
        4. 添加延迟以避免API QPS限制
        5. 调用process_text处理识别的文本
        6. 捕获并处理可能的异常
        """
        try:
            # 检查图片尺寸
            with Image.open(file_path) as img:
                width, height = img.size
                
            # 获取OCR模块单例
            ocr_module = OCRModule.get_instance()
            
            # 检查图片尺寸是否超过OCR模块的最大支持尺寸
            max_width = ocr_module.get_max_width()
            max_height = ocr_module.get_max_height()
            
            if width > max_width or height > max_height:
                error_msg = LangManager.get_lang_data()['image_size_exceeded'].format(
                    file_path, width, height, max_width, max_height
                )
                print(error_msg)
                self.output.append(f'{error_msg}\n')
                self.error_count += 1
                return {'error': error_msg}
            
            # 使用OCR模块识别文本
            text = ocr_module.recognize_text(file_path)
            
            # 添加延迟以避免QPS限制
            delay = ocr_module.get_api_delay()
            print(LangManager.get_lang_data()['ocr_module_delay_info'].format(delay))
            time.sleep(delay)
            
            # 处理识别的文本
            file_name = os.path.basename(file_path)
            processed_text = self.process_text(
                file_name=file_name,
                text=text
            )
            
            if processed_text:
                # 调试信息已存储在self.ocr_debug_info中，无需返回
                return {
                    'text': processed_text
                }
            else:
                error_msg = LangManager.get_lang_data()['text_processing_failed'].format(file_path)
                return {'error': error_msg}
        except Exception as e:
            error_msg = LangManager.get_lang_data()['ocr_processing_failed'].format(file_path, str(e))
            print(error_msg)
            self.output.append(f'{error_msg}\n')
            self.error_count += 1
            return {'error': error_msg}

    def get_statistics(self):
        """
        获取处理统计信息

        返回:
            dict: 包含以下统计数据的字典
                - success_count: 成功处理的图片数量
                - error_count: 处理失败的图片数量
                - suspected_dash_count: 疑似包含破折号问题的文件数量
        """
        return {
            'success_count': self.success_count,
            'error_count': self.error_count,
            'suspected_dash_count': len(self.suspected_dash_files)
        }