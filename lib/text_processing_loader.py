import os
import sys
import time
import json
from PIL import Image
from lib.lang_manager import LocalizationManager

from lib.ocr_module_loader import OCRModuleLoader
from lib.text_processing.text_processor import TextProcessor

# 获取本地化管理器实例
loc_manager = LocalizationManager.get_instance()

class TextProcessingLoader:
    """文本处理加载器，负责协调整个图片处理流程"""

    def __init__(self, config=None):
        """
        初始化文本处理加载器

        参数:        
            config: 配置字典，如果为None则使用默认配置
        """
        self.config = config or {}
        # 获取当前文件的绝对路径
        current_file_path = os.path.abspath(__file__)
        # 构建到项目根目录的路径 (lib/text_processing/text_processing_loader.py -> .. -> .. -> root)
        self.parent_dir = os.path.abspath(os.path.join(current_file_path, '..', '..', '..'))
        self.current_dir = self.config.get('current_dir', os.getcwd())
        self.lib_dir = os.path.join(self.parent_dir, 'lib')
        
        # 设置默认配置
        self.output_file = self.config.get('output_file', os.path.join(self.parent_dir, 'example.txt'))
        self.debug_output_file = self.config.get('debug_output_file', os.path.join(self.parent_dir, 'example_ocr_debug.txt'))
        # OCR识别语言，从配置中获取，默认为None（使用OCR模块默认语言）
        # 允许在加载特定语言数据和字体的情况下，使用不同的OCR识别语言
        self.ocr_language = self.config.get('ocr_language', 'default')
        self.output_ocr_debug = self.config.get('output_ocr_debug', True)
        # 从配置中获取纵向拼接的最大图片数量，默认为4
        self.max_vertical_images = int(self.config.get('max_vertical_images', 4))
        # 临时目录，用于存储拼接后的图片
        self.temp_dir = os.path.join(self.parent_dir, 'temp')
        os.makedirs(self.temp_dir, exist_ok=True)

        # 初始化OCR模块加载器
        self.loader = OCRModuleLoader(self.parent_dir)
        # 设置OCR识别语言（如果配置中提供）
        if self.ocr_language is not None:
            self.loader.ocr_language = self.ocr_language
        self.ocr_module = None
        self.options = None
        self.use_custom_font = False
        self.font_path = None
        self.found_fonts = []
        
        # 文本标记
        self.START_MARKERS = self.config.get('start_markers', ['剧情梗概'])
        self.STOP_MARKERS = self.config.get('stop_markers', ['×', '取消', '确认'])
        
        # 初始化文本处理器
        self.text_processor = TextProcessor(self.START_MARKERS, self.STOP_MARKERS)

    def initialize(self):
        """初始化OCR模块和相关配置"""
        try:
            # 初始化字体增强
            self.loader.initialize_font_enhancement(self.ocr_language)
            self.use_custom_font, self.font_path, self.ocr_language, self.found_fonts = self.loader.get_font_enhancement_status()
            
            # 初始化OCR模块
            self.ocr_module = self.loader.initialize_ocr_module()
            
            # 获取OCR选项
            self.options = self.loader.get_options()
            
            return True
        except Exception as e:
            print(loc_manager.get_lang_data()['init_fail'].format(str(e)))
            return False

    def find_image_files(self):
        """查找当前目录下的所有图片文件"""
        image_files = [f for f in os.listdir(self.current_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif'))]
        
        # 按文件名排序
        try:
            image_files.sort(key=lambda x: int(os.path.splitext(x)[0]))
        except ValueError:
            image_files.sort()
        
        return image_files

    def stitch_images_vertically(self, image_paths):
        """
        将多张图片纵向拼接成一张
        
        参数:
            image_paths: 图片路径列表
        
        返回:
            拼接后的图片路径
        """
        try:
            # 打开所有图片
            images = [Image.open(img_path) for img_path in image_paths]
            
            # 获取每张图片的宽度和高度
            widths, heights = zip(*(img.size for img in images))
            
            # 计算拼接后图片的总宽度和总高度
            total_width = max(widths)
            total_height = sum(heights)
            
            # 创建一个新的空白图片
            new_image = Image.new('RGB', (total_width, total_height), color='white')
            
            # 拼接图片
            y_offset = 0
            for img in images:
                new_image.paste(img, (0, y_offset))
                y_offset += img.size[1]
            
            # 保存拼接后的图片
            stitch_file_name = f"stitched_{os.path.basename(image_paths[0]).split('.')[0]}_{os.path.basename(image_paths[-1]).split('.')[0]}.png"
            stitch_file_path = os.path.join(self.temp_dir, stitch_file_name)
            new_image.save(stitch_file_path)
            
            return stitch_file_path
        except Exception as e:
            error_msg = loc_manager.get_lang_data()['image_stitch_error'].format(str(e))
            print(error_msg)
            return None

    def check_image_size(self, image_path):
        """检查图片尺寸是否超过OCR模块的最大支持尺寸"""
        try:
            # 打开图片获取尺寸
            with Image.open(image_path) as img:
                width, height = img.size

            # 获取OCR模块的最大支持尺寸
            max_width = None
            max_height = None

            if self.ocr_module:
                if hasattr(self.ocr_module, 'get_max_width'):
                    max_width = self.ocr_module.get_max_width()
                if hasattr(self.ocr_module, 'get_max_height'):
                    max_height = self.ocr_module.get_max_height()

            # 使用默认值如果获取失败
            max_width = max_width if max_width is not None else 8192
            max_height = max_height if max_height is not None else 8192

            # 检查尺寸是否超过限制
            if width > max_width or height > max_height:
                error_msg = loc_manager.get_lang_data()['image_size_exceeded'].format(
                    image_path, width, height, max_width, max_height
                )
                print(error_msg)
                return False, error_msg

            return True, None
        except Exception as e:
            error_msg = loc_manager.get_lang_data()['image_size_check_error'].format(image_path, str(e))
            print(error_msg)
            return False, error_msg

    def process_images(self):
        """处理所有图片文件"""
        try:
            # 查找图片文件
            image_files = self.find_image_files()
            
            if not image_files:
                warning_msg = loc_manager.get_lang_data()['no_image_files_warning'].format(self.current_dir)
                print(warning_msg)
                self.text_processor.output.append(f'{warning_msg}\n')
                return False
            
            # 按max_vertical_images分组图片
            for i in range(0, len(image_files), self.max_vertical_images):
                group_files = image_files[i:i + self.max_vertical_images]
                group_file_paths = [os.path.join(self.current_dir, file_name) for file_name in group_files]
                
                # 如果分组中只有一张图片，直接处理
                if len(group_files) == 1:
                    file_name = group_files[0]
                    file_path = group_file_paths[0]
                    
                    try:
                        # 检查图片尺寸
                        is_valid_size, error_msg = self.check_image_size(file_path)
                        if not is_valid_size:
                            self.text_processor.output.append(f'{error_msg}\n')
                            self.text_processor.error_count += 1
                            continue

                        # 使用OCR模块识别图片
                        text = self.loader.recognize_image(file_path)
                        
                        # 使用文本处理器处理识别结果
                        self.text_processor.process_text(
                            file_name=file_name,
                            text=text,
                            use_custom_font=self.use_custom_font,
                            output_ocr_debug=self.output_ocr_debug,
                            ocr_module=self.ocr_module
                        )
                    except Exception as e:
                        error_msg = loc_manager.get_lang_data()['image_process_error'].format(file_path, str(e))
                        print(error_msg)
                        self.text_processor.output.append(f'{error_msg}\n')
                        self.text_processor.error_count += 1
                else:
                    # 拼接多张图片
                    stitch_file_path = self.stitch_images_vertically(group_file_paths)
                    
                    if stitch_file_path:
                        # 为拼接后的图片创建一个虚拟文件名
                        stitch_file_name = f"stitched_{group_files[0]}_{group_files[-1]}"
                        
                        try:
                            # 检查拼接后图片的尺寸
                            is_valid_size, error_msg = self.check_image_size(stitch_file_path)
                            if not is_valid_size:
                                self.text_processor.output.append(f'{error_msg}\n')
                                self.text_processor.error_count += 1
                                continue

                            # 使用OCR模块识别拼接后的图片
                            text = self.loader.recognize_image(stitch_file_path)
                                 
                            # 使用文本处理器处理识别结果
                            self.text_processor.process_text(
                                file_name=stitch_file_name,
                                text=text,
                                use_custom_font=self.use_custom_font,
                                output_ocr_debug=self.output_ocr_debug,
                                ocr_module=self.ocr_module
                            )
                        except Exception as e:
                            error_msg = loc_manager.get_lang_data()['image_process_error'].format(stitch_file_path, str(e))
                            print(error_msg)
                            self.text_processor.output.append(f'{error_msg}\n')
                            self.text_processor.error_count += 1
            
            # 写入结果文件
            self.text_processor.write_results(
                output_file=self.output_file,
                font_path=self.font_path,
                use_custom_font=self.use_custom_font,
                found_fonts=self.found_fonts
            )
            
            # 写入OCR调试信息文件
            if self.output_ocr_debug:
                self.text_processor.write_debug_info(
                    debug_output_file=self.debug_output_file,
                    image_files=image_files,
                    use_custom_font=self.use_custom_font,
                    font_path=self.font_path
                )
            
            return True
        except Exception as e:
            print(loc_manager.get_lang_data()['script_execution_error'].format(str(e)))
            return False

    def run(self):
        """运行整个处理流程"""
        try:
            # 初始化
            if not self.initialize():
                return False
            
            # 处理图片
            return self.process_images()
        except Exception as e:
            print(loc_manager.get_lang_data()['script_execution_error'].format(str(e)))
            return False

from .text_processing.text_processor import TextProcessor
__all__ = ['TextProcessingLoader', 'TextProcessor']