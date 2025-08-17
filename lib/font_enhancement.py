import os
import json

def load_font_config():
    """加载字体配置文件"""
    config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ocr_language_mapping.json')
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def detect_font_enhancement(parent_dir, lang_data):
    """检测字体增强并返回相关信息"""
    # 加载字体配置
    ocr_language_mapping = load_font_config()
    supported_fonts = ocr_language_mapping['supported_fonts']
    default_ocr_language = ocr_language_mapping['default_ocr_language']

    use_custom_font = False
    font_path = None
    ocr_language = default_ocr_language

    # 获取当前语言文件的语言代码
    current_lang_file = lang_data.get('current_language', 'en-us.json')

    # 从字体配置中获取语言映射
    language_mapping = ocr_language_mapping.get('language_mapping', {})

    # 检查父目录中存在的字体文件数量
    found_fonts = []
    for font_info in supported_fonts:
        font_file = font_info['file_name']
        current_font_path = os.path.join(parent_dir, font_file)
        if os.path.exists(current_font_path):
            found_fonts.append((font_info, current_font_path))

    # 如果只找到一个字体文件，则使用它
    if len(found_fonts) == 1:
        font_info, current_font_path = found_fonts[0]
        use_custom_font = True
        font_path = current_font_path
        ocr_language = font_info['ocr_language']  # 使用字体语言类型作为OCR语言类型
        # 使用语言文件中的单字体检测提示
        single_font_msg = lang_data['single_font_detected']
        print(single_font_msg.format(font_path))
    elif len(found_fonts) > 1:
        # 使用语言文件中的多字体警告信息
        warning_msg = lang_data['multiple_fonts_warning']
        font_list = ', '.join([font_info['file_name'] for font_info, _ in found_fonts])
        print(warning_msg.format(font_list))
        # 多字体文件时，OCR语言跟随语言文件
        ocr_language = language_mapping.get(current_lang_file, 'ENG')
    else:
        # 没有找到字体文件，OCR语言跟随语言文件
        # 使用语言文件中的无字体检测提示
        no_font_msg = lang_data['no_font_detected_simple']
        print(no_font_msg)
        ocr_language = language_mapping.get(current_lang_file, 'ENG')

    # 确保返回有效的OCR语言类型
    valid_languages = ['auto_detect', 'CHN_ENG', 'ENG', 'JAP', 'KOR', 'FRE', 'SPA', 'POR', 'GER', 'ITA', 'RUS']
    if ocr_language not in valid_languages:
        ocr_language = 'CHN_ENG'  # 默认使用中英文混合
    
    return use_custom_font, font_path, ocr_language, found_fonts