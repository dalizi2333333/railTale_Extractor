import os
import time
from lib.bootstrap import LocalizationManager

class TextProcessor:
    """文本处理器，负责处理OCR识别后的文本"""

    def __init__(self, start_markers, stop_markers):
        """
        初始化文本处理器

        参数:
            start_markers: 开始记录文本的标记列表
            stop_markers: 停止记录文本的标记列表
        """
        self.start_markers = start_markers
        self.stop_markers = stop_markers
        self.loc_manager = LocalizationManager.get_instance()
        self.output = []
        self.success_count = 0
        self.error_count = 0
        self.suspected_dash_files = []
        self.ocr_debug_info = []

    def process_text(self, file_name, text, use_custom_font, output_ocr_debug=False, ocr_module=None):
        """
        处理单张图片的OCR文本

        参数:
            file_name: 图片文件名
            text: OCR识别的文本
            use_custom_font: 是否使用自定义字体
            output_ocr_debug: 是否输出OCR调试信息
            ocr_module: OCR模块实例

        返回:
            处理后的文本
        """
        if not text:
            error_msg = self.loc_manager.get_lang_data().get('ocr_recognition_failed', '识别失败，无结果返回')
            print(error_msg)
            self.output.append(f'{error_msg}\n')
            self.error_count += 1
            return None

        # 收集OCR调试信息
        if output_ocr_debug and ocr_module:
            debug_entry = ocr_module.generate_debug_entry(file_name, use_custom_font, text)
            self.ocr_debug_info.append(debug_entry + '\n')

        # 分析文本内容
        start_recording = False
        filtered_text = []
        lines = text.split('\n')
        current_paragraph = []

        for line in lines:
            # 打印行内容
            print(self.loc_manager.get_lang_data()['image_line_content'].format(file_name, line))

            # 检查是否到达新的开始记录点
            if any(marker in line for marker in self.start_markers) and not start_recording:
                start_recording = True
                # 找出实际匹配的标记
                matched_marker = next(marker for marker in self.start_markers if marker in line)
                print(self.loc_manager.get_lang_data()['start_recording_text'].format(matched_marker, file_name))
                current_paragraph = []  # 重置当前段落
                continue  # 不记录开始标记本身

            # 检查是否到达停止记录点
            if start_recording:
                if line.strip() in self.stop_markers:
                    start_recording = False  # 重置以便下一次检测
                    print(self.loc_manager.get_lang_data()['stop_recording_text'].format(line, file_name))
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
            print(self.loc_manager.get_lang_data()['suspected_dash_detected'].format(file_name))
            self.suspected_dash_files.append(file_name)

        self.output.append(f'{processed_text}\n')  # 不同图片的内容输出到不同行
        self.success_count += 1
        print(self.loc_manager.get_lang_data()['process_success'].format(file_name))

        return processed_text

    def write_results(self, output_file, font_path, use_custom_font, found_fonts):
        """
        写入处理结果到文件

        参数:
            output_file: 输出文件路径
            font_path: 字体文件路径
            use_custom_font: 是否使用自定义字体
            found_fonts: 找到的字体列表
        """
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(''.join(self.output))
            f.write(f"\n{self.loc_manager.get_lang_data()['process_stats'].format(self.success_count, self.error_count)}\n")

            # 写入疑似破折号信息
            if len(self.suspected_dash_files) > 0:
                f.write(self.loc_manager.get_lang_data()['suspected_dash_summary'].format(len(self.suspected_dash_files)))
                for file in self.suspected_dash_files:
                    f.write(f'      - {file}\n')
                f.write(self.loc_manager.get_lang_data()['manual_screening_prompt'] + '\n')

            # 写入字体提示信息
            if use_custom_font:
                # 检测使用的字体类型并提示
                if font_path.endswith('ja-jp.ttf'):
                    f.write('\n' + self.loc_manager.get_lang_data()['font_detected'].format('ja-jp.ttf', self.loc_manager.get_lang_data()['font_ja_jp_name']) + '\n')
                elif font_path.endswith('zh-cn.ttf'):
                    f.write('\n' + self.loc_manager.get_lang_data()['font_detected'].format('zh-cn.ttf', self.loc_manager.get_lang_data()['font_zh_cn_name']) + '\n')
                elif font_path.endswith('zh-tw.ttf'):
                    f.write('\n' + self.loc_manager.get_lang_data()['font_detected'].format('zh-tw.ttf', self.loc_manager.get_lang_data()['font_zh_tw_name']) + '\n')
            else:
                # 区分没有字体文件和存在多个字体文件的情况
                if len(found_fonts) == 0:
                    # 使用语言文件中的提示
                    f.write('\n' + self.loc_manager.get_lang_data()['font_not_detected'] + '\n')
                elif len(found_fonts) > 1:
                    # 使用语言文件中的警告
                    f.write('\n' + self.loc_manager.get_lang_data()['multiple_fonts_warning'].format(', '.join([font[0]['file_name'] for font in found_fonts])) + '\n')

        print(self.loc_manager.get_lang_data()['results_saved'].format(output_file))
        print(self.loc_manager.get_lang_data()['process_stats'].format(self.success_count, self.error_count))

        # 检查是否有疑似破折号情况
        suspected_dash_count = len(self.suspected_dash_files)
        if suspected_dash_count > 0:
            print(self.loc_manager.get_lang_data()['suspected_dash_summary'].format(suspected_dash_count))
            for file in self.suspected_dash_files:
                print(f'      - {file}')
            print(self.loc_manager.get_lang_data()['manual_screening_prompt'])

        # 输出字体提示信息
        if use_custom_font:
            # 检测使用的字体类型并提示
            if font_path.endswith('ja-jp.ttf'):
                print('\n' + self.loc_manager.get_lang_data()['font_detected'].format('ja-jp.ttf', self.loc_manager.get_lang_data()['font_ja_jp_name']))
            elif font_path.endswith('zh-cn.ttf'):
                print('\n' + self.loc_manager.get_lang_data()['font_detected'].format('zh-cn.ttf', self.loc_manager.get_lang_data()['font_zh_cn_name']))
            elif font_path.endswith('zh-tw.ttf'):
                print('\n' + self.loc_manager.get_lang_data()['font_detected'].format('zh-tw.ttf', self.loc_manager.get_lang_data()['font_zh_tw_name']))
        else:
            # 区分没有字体文件和存在多个字体文件的情况
            if len(found_fonts) == 0:
                # 使用语言文件中的提示
                print('\n' + self.loc_manager.get_lang_data()['font_not_detected'])
            elif len(found_fonts) > 1:
                # 使用语言文件中的警告
                print('\n' + self.loc_manager.get_lang_data()['multiple_fonts_warning'].format(', '.join([font[0]['file_name'] for font in found_fonts])))

    def write_debug_info(self, debug_output_file, image_files, use_custom_font, font_path=None):
        """
        写入OCR调试信息到文件

        参数:
            debug_output_file: 调试信息输出文件路径
            image_files: 处理的图片文件列表
            use_custom_font: 是否使用自定义字体
            font_path: 字体文件路径
        """
        with open(debug_output_file, 'w', encoding='utf-8') as f:
            f.write(self.loc_manager.get_lang_data()['debug_info_header'].format(
                time.strftime("%Y-%m-%d %H:%M:%S"),
                len(image_files),
                self.success_count,
                self.error_count,
                "是" if use_custom_font else "否"
            ))
            if use_custom_font and font_path:
                f.write(self.loc_manager.get_lang_data()['debug_font_path'].format(font_path))
            f.write('\n')
            f.write(''.join(self.ocr_debug_info))
        print(self.loc_manager.get_lang_data()['ocr_debug_info_saved'].format(debug_output_file))

    def get_statistics(self):
        """
        获取处理统计信息

        返回:
            包含成功和失败数量的字典
        """
        return {
            'success_count': self.success_count,
            'error_count': self.error_count,
            'suspected_dash_count': len(self.suspected_dash_files)
        }