import os
import sys
import time
import json
from PIL import Image
from lang_manager import LangManager
from config.config_manager import ConfigManager

from ocr_core.ocr_module import OCRModule
from text_extracting.text_extractor import TextExtractor

class TextProcessor:
    """文本处理加载器，负责协调整个图片处理流程

    该类是整个OCR文本提取系统的核心协调器，负责初始化配置、
    管理图片处理流程、协调OCR模块和文本提取器的工作，
    并最终生成处理结果和调试信息。
    """

    def __init__(self, config=None):
        """
        初始化文本处理器

        参数:
            config: 配置字典，如果为None则使用默认配置

        属性初始化:
            parent_dir: 项目根目录
            process_dir: 待处理图片所在目录
            dir_name: 处理目录名称
            output_file: 结果输出文件路径
            debug_output_file: OCR调试信息输出文件路径
            output_ocr_debug: 是否输出OCR调试信息的标志
            max_vertical_images: 最大纵向拼接图片数量
            temp_dir: 临时文件目录
            loc_manager: 语言管理器实例
            text_extractor: 文本提取器实例
            processed_results: 存储处理结果的字典
        """
        # 构建到项目根目录的路径
        self.parent_dir = ConfigManager.get_parent_dir()
        self.process_dir = ConfigManager.get_process_dir()
        self.dir_name = os.path.basename(self.process_dir)
        # 设置输出文件
        self.output_file = os.path.join(self.process_dir, f'{self.dir_name}.txt')
        self.debug_output_file = os.path.join(self.process_dir, f'{self.dir_name}_ocr_debug.txt')
        # 从配置中获取更多信息
        self.output_ocr_debug = ConfigManager.get('OUTPUT_OCR_DEBUG', 'True').lower() == 'true'
        self.max_vertical_images = int(ConfigManager.get('MAX_VERTICAL_IMAGES', 4))
        # 临时目录，用于存储拼接后的图片
        self.temp_dir = os.path.join(self.process_dir, 'temp')
        os.makedirs(self.temp_dir, exist_ok=True)

        # 初始化文本提取器
        self.text_extractor = TextExtractor()
        
        # 存储处理结果
        self.processed_results = {}

    def initialize(self):
        """初始化OCR模块和相关配置

        返回:
            bool: 初始化成功返回True，失败返回False
        """
        try:
            # 检测字体增强
            from text_extracting.font_enhancement_detector import detect_font_enhancement
            detect_font_enhancement()

            return True
        except Exception as e:
            print(LangManager.get_lang_data()['init_fail'].format(str(e)))
            return False

    def find_image_files(self):
        """查找当前目录下的所有图片文件

        返回:
            list: 按文件名排序的图片文件列表
        """
        image_files = [f for f in os.listdir(self.process_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif'))]
        
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
            str: 拼接后的图片路径，如果拼接失败则返回None
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
            error_msg = LangManager.get_lang_data()['image_stitch_error'].format(str(e))
            print(error_msg)
            return None

    def process_images(self):
        """处理所有图片文件

        该方法是图片处理的主流程，包括：
        1. 查找图片文件
        2. 按组处理图片（单张或拼接多张）
        3. 调用TextExtractor处理每张图片
        4. 存储处理结果
        5. 写入结果文件和调试信息

        返回:
            dict: 处理成功返回包含处理结果的字典，失败返回空字典
        """
        try:
            # 查找图片文件
            image_files = self.find_image_files()
            
            if not image_files:
                warning_msg = LangManager.get_lang_data()['no_image_files_warning'].format(self.process_dir)
                print(warning_msg)
                self.text_extractor.output.append(f'{warning_msg}\n')
                return False
            
            # 按max_vertical_images分组图片
            for i in range(0, len(image_files), self.max_vertical_images):
                group_files = image_files[i:i + self.max_vertical_images]
                group_file_paths = [os.path.join(self.process_dir, file_name) for file_name in group_files]
                
                # 如果分组中只有一张图片，直接处理
                if len(group_files) == 1:
                    file_path = group_file_paths[0]
                    
                    try:
                        # 使用TextExtractor处理图片
                        result = self.text_extractor.process_image(file_path)
                        
                        # 存储结果
                        if 'error' not in result:
                            self.processed_results[file_path] = {
                                'text': result['text']
                            }
                    except Exception as e:
                        error_msg = LangManager.get_lang_data()()['image_process_error'].format(file_path, str(e))
                        print(error_msg)
                        self.text_extractor.output.append(f'{error_msg}\n')
                        self.text_extractor.error_count += 1
                else:
                    # 拼接多张图片
                    stitch_file_path = self.stitch_images_vertically(group_file_paths)
                    
                    if stitch_file_path:
                        try:
                            # 使用TextExtractor处理拼接后的图片
                            result = self.text_extractor.process_image(stitch_file_path)
                            
                            # 存储结果
                            if 'error' not in result:
                                self.processed_results[stitch_file_path] = {
                                    'text': result['text']
                                }
                        except Exception as e:
                            error_msg = LangManager.get_lang_data()['image_process_error'].format(stitch_file_path, str(e))
                            print(error_msg)
                            self.text_extractor.output.append(f'{error_msg}\n')
                            self.text_extractor.error_count += 1
            
            # 写入结果文件
            self.write_results()
            # 写入OCR调试信息文件
            if self.output_ocr_debug:
                self.write_debug_info(image_files)
            
            return self.processed_results
        except Exception as e:
            print(LangManager.get_lang_data()['script_execution_error'].format(str(e)))
            return {}

    def write_results(self):
        """写入处理结果到文件

        将处理后的文本、统计信息、疑似破折号信息和字体提示信息
        写入到输出文件中，并在控制台打印相关信息。
        """
        # 从text_extractor获取输出内容
        output_content = ''.join(self.text_extractor.output)
        success_count = self.text_extractor.success_count
        error_count = self.text_extractor.error_count
        suspected_dash_files = self.text_extractor.suspected_dash_files

        # 获取配置
        use_custom_font = ConfigManager.get('USE_CUSTOM_FONT', False)
        font_path = ConfigManager.get('CUSTOM_FONT_PATH', None)
        found_fonts = ConfigManager.get('FIND_FONTS', [])

        with open(self.output_file, 'w', encoding='utf-8') as f:
            f.write(output_content)
            f.write(f"\n{LangManager.get_lang_data()['process_stats'].format(success_count, error_count)}\n")

            # 写入疑似破折号信息
            if len(suspected_dash_files) > 0:
                f.write(LangManager.get_lang_data()['suspected_dash_summary'].format(len(suspected_dash_files)))
                for file in suspected_dash_files:
                    f.write(f'      - {file}\n')
                f.write(LangManager.get_lang_data()['manual_screening_prompt'] + '\n')

            # 写入字体提示信息
            if use_custom_font:
                # 检测使用的字体类型并提示
                f.write('\n' + LangManager.get_lang_data()['single_font_detected'].format(font_path) + '\n')
            else:
                # 区分没有字体文件和存在多个字体文件的情况
                if len(found_fonts) == 0:
                    # 使用语言文件中的提示
                    f.write('\n' + LangManager.get_lang_data()['font_not_detected'] + '\n')
                elif len(found_fonts) > 1:
                    # 使用语言文件中的警告
                    f.write('\n' + LangManager.get_lang_data()['multiple_fonts_warning'].format(', '.join([font[0]['file_name'] for font in found_fonts])) + '\n')

        print(LangManager.get_lang_data()['results_saved'].format(self.output_file))
        print(LangManager.get_lang_data()['process_stats'].format(success_count, error_count))

        # 检查是否有疑似破折号情况
        suspected_dash_count = len(suspected_dash_files)
        if suspected_dash_count > 0:
            print(LangManager.get_lang_data()['suspected_dash_summary'].format(suspected_dash_count))
            for file in suspected_dash_files:
                print(f'      - {file}')
            print(LangManager.get_lang_data()['manual_screening_prompt'])

        # 输出字体提示信息
        if use_custom_font:
            # 检测使用的字体类型并提示
            print('\n' + LangManager.get_lang_data()['single_font_detected'].format(font_path))
        else:
            # 区分没有字体文件和存在多个字体文件的情况
            if len(found_fonts) == 0:
                # 使用语言文件中的提示
                print('\n' + LangManager.get_lang_data()['font_not_detected'])
            elif len(found_fonts) > 1:
                # 使用语言文件中的警告
                print('\n' + LangManager.get_lang_data()['multiple_fonts_warning'].format(', '.join([font[0]['file_name'] for font in found_fonts])))

    def write_debug_info(self, image_files):
        """写入OCR调试信息到文件

        参数:
            image_files: 处理的图片文件列表

        将OCR调试信息、处理统计数据和配置信息写入到调试输出文件。
        """
        # 从text_extractor获取调试信息
        ocr_debug_info = self.text_extractor.ocr_debug_info
        success_count = self.text_extractor.success_count
        error_count = self.text_extractor.error_count

        # 获取配置
        use_custom_font = ConfigManager.get('USE_CUSTOM_FONT', False)
        font_path = ConfigManager.get('CUSTOM_FONT_PATH', None)

        with open(self.debug_output_file, 'w', encoding='utf-8') as f:
            f.write(LangManager.get_lang_data()['debug_info_header'].format(
                time.strftime("%Y-%m-%d %H:%M:%S"),
                len(image_files),
                success_count,
                error_count,
                "是" if use_custom_font else "否"
            ))
            if use_custom_font and font_path:
                f.write(LangManager.get_lang_data()['debug_font_path'].format(font_path))
            f.write('\n')
            f.write(''.join(ocr_debug_info))
        print(LangManager.get_lang_data()['ocr_debug_info_saved'].format(self.debug_output_file))

    def run(self):
        """运行整个处理流程

        该方法是整个文本处理系统的入口点，依次执行：
        1. 初始化OCR模块
        2. 处理图片
        3. 捕获并处理可能的异常

        返回:
            dict: 处理成功返回包含处理结果的字典，失败返回空字典
        """
        try:
            # 初始化
            if not self.initialize():
                return {}
            # 处理图片
            return self.process_images()
        except Exception as e:
            print(LangManager.get_lang_data()['script_execution_error'].format(str(e)))
            return {}

__all__ = ['TextProcessor']
