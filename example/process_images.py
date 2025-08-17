import os
import sys
import time
import json

# 获取当前脚本所在目录
current_dir = os.path.dirname(os.path.abspath(__file__))
# 获取父级目录
parent_dir = os.path.dirname(current_dir)

# 语言优先级顺序: 简体中文 -> 英语 -> 繁体中文 -> 日语
LANGUAGE_PRIORITY = [
    ('zh-cn.json', '简体中文'),
    ('en.json', 'English'),
    ('zh-tw.json', '繁体中文'),
    ('ja-jp.json', '日本語')
]

# 加载语言文件
def load_language_file(parent_dir):
    lang_dir = os.path.join(parent_dir, 'lang')
    
    # 获取lang目录下的所有json文件
    lang_files = [f for f in os.listdir(lang_dir) if f.lower().endswith('.json')]
    
    # 如果只有一个语言文件，直接加载
    if len(lang_files) == 1:
        lang_file = os.path.join(lang_dir, lang_files[0])
        with open(lang_file, 'r', encoding='utf-8') as f:
            lang_data = json.load(f)
            lang_data['current_language'] = lang_files[0]
            return lang_data
    
    # 多个语言文件，按照优先级顺序加载
    for file_name, display_name in LANGUAGE_PRIORITY:
        if file_name in lang_files:
            lang_file = os.path.join(lang_dir, file_name)
            with open(lang_file, 'r', encoding='utf-8') as f:
                lang_data = json.load(f)
                lang_data['current_language'] = file_name
                return lang_data
    
    # 如果没有找到优先级列表中的语言文件
    print('Error: Multiple localization files detected. Please keep only one language file.')
    print('Priority supported language files: zh-cn.json, en.json, zh-tw.json, ja-jp.json')
    sys.exit(1)

# 加载语言数据
lang_data = load_language_file(parent_dir)

# 添加父级目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 导入字体增强检测函数
from lib.font_enhancement import detect_font_enhancement

# 检测字体增强
use_custom_font, font_path, ocr_language, found_fonts = detect_font_enhancement(parent_dir, lang_data)

# 检查必要的库是否安装
from lib.dependency_check import check_dependencies
check_dependencies(lang_data)

# 导入必要的库
from PIL import Image
from aip import AipOcr
import requests

# 读取配置文件函数
from lib.config import read_config

# 读取配置
config = read_config(lang_data)
APP_ID = config['APP_ID']
API_KEY = config['API_KEY']
SECRET_KEY = config['SECRET_KEY']

# 从配置中获取OCR文本提取标记
# 开始标记: 当检测到这些文本时开始记录
START_MARKERS = config.get('START_MARKERS', '剧情梗概').split(',')

# 结束标记: 当检测到这些文本时停止记录
STOP_MARKERS = config.get('STOP_MARKERS', 'i,存在分支剧情选项,取消,×').split(',')

# 初始化百度OCR客户端
client = AipOcr(APP_ID, API_KEY, SECRET_KEY)

# 配置可选参数，优化识别精度
options = {
    'language_type': ocr_language,  # 根据字体和语言文件设置OCR语言
    'detect_direction': 'true',      # 检测方向
    'detect_language': 'true',       # 检测语言
    'probability': 'true',           # 返回置信度
    'paragraph': 'true'              # 段落合并
}

# 根据是否使用自定义字体设置OCR参数
if use_custom_font:
    options['accuracy'] = 'high'  # 高精度模式
    options['font_type'] = 'custom'
    options['custom_font_path'] = font_path
else:
    options['font_type'] = 'simhei'  # 设置为常见中文字体(黑体)

# 目录名称（用于结果文件命名）
dir_name = os.path.basename(current_dir)
# 结果文件路径
output_file = os.path.join(parent_dir, f'{dir_name}.txt')

# 是否输出OCR调试信息
output_ocr_debug = config.get('OUTPUT_OCR_DEBUG', 'false').lower() == 'true'

# 调试信息输出文件路径
debug_output_file = os.path.join(parent_dir, f'{dir_name}_ocr_debug.txt')
# 初始化调试信息列表
ocr_debug_info = []

output = []
success_count = 0
error_count = 0
suspected_dash_files = []  # 存储包含疑似破折号的图片文件名

# 检查百度OCR配置是否完整
if not (APP_ID and API_KEY and SECRET_KEY) or APP_ID == '你的APP_ID':
    print(lang_data['ocr_api_config_prompt'])
    sys.exit(1)

try:
    # 获取当前目录下的所有图片文件
    image_files = [f for f in os.listdir(current_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif'))]
    
    # 按文件名排序（假设文件名是数字）
    try:
        image_files.sort(key=lambda x: int(os.path.splitext(x)[0]))
    except ValueError:
        # 如果文件名不是纯数字，则按字母顺序排序
        image_files.sort()
    
    if not image_files:
        print(f'警告: 在目录 {current_dir} 中未找到图片文件')
        output.append(f'警告: 在目录 {current_dir} 中未找到图片文件\n')
    
    for file_name in image_files:
        file_path = os.path.join(current_dir, file_name)
        
        try:
            img = Image.open(file_path)

            # 使用整张图片进行OCR，不裁剪
            image_path = file_path

            # 读取图像文件并进行OCR识别
            with open(image_path, 'rb') as fp:
                image_data = fp.read()

            # 使用不含位置信息的OCR接口
            if use_custom_font:
                # 高精度模式但不含位置信息
                result = client.basicAccurate(image_data, options)
            else:
                # 通用模式不含位置信息
                result = client.basicGeneral(image_data, options)

            # 添加延迟以避免QPS限制
            time.sleep(1.5)  # 延迟1.5秒

            # 提取识别结果
            if 'words_result' in result:
                # 存储过滤后的文本
                filtered_text = []
                has_branch_tag = False

                # 收集OCR调试信息
                if output_ocr_debug:
                    debug_entry = f"=== 图片 {file_name} OCR识别结果 ===\n"
                    debug_entry += f"识别模式: {'高精度' if use_custom_font else '通用'}\n"
                    debug_entry += f"识别类型: {ocr_language}\n"
                    debug_entry += f"原始识别结果: {json.dumps(result, ensure_ascii=False)}\n"
                    debug_entry += "字块详情:\n"

                # 分析每个文字块的内容
                start_recording = False
                stop_recording = False
                filtered_text = []

                for idx, item in enumerate(result['words_result']):
                    words = item['words']
                    confidence = item.get('probability', {}).get('average', '未知')

                    # 打印字块内容
                    print(f'图片 {file_name} 字块: 内容="{words}"')

                    # 收集字块调试信息
                    if output_ocr_debug:
                        debug_entry += f"  字块 {idx+1}: 内容=\"{words}\", 置信度={confidence}\n"

                    # 检查是否到达开始记录点
                    if any(marker in words for marker in START_MARKERS) and not start_recording:
                        start_recording = True
                        # 找出实际匹配的标记
                        matched_marker = next(marker for marker in START_MARKERS if marker in words)
                        print(f'开始记录文本: 检测到"{matched_marker}" (图片 {file_name})')
                        if output_ocr_debug:
                            debug_entry += f"  处理: 开始记录点\n"
                        continue  # 不记录'剧情梗概'本身

                    # 检查是否到达停止记录点
                    if start_recording and not stop_recording:
                        if words.strip() in STOP_MARKERS:
                            stop_recording = True
                            print(f'停止记录文本: 检测到停止标记\"{words}\" (图片 {file_name})')
                            if output_ocr_debug:
                                debug_entry += f"  处理: 停止记录点\n"
                        else:
                            filtered_text.append(words)
                            if output_ocr_debug:
                                debug_entry += f"  处理: 保留\n"
                    else:
                        if output_ocr_debug:
                            debug_entry += f"  处理: 跳过\n"

                # 保存调试信息
                if output_ocr_debug:
                    ocr_debug_info.append(debug_entry + '\n')

                # 将过滤后的文本块连接，删除换行符
                text = ''.join(filtered_text)
                
                # 文本后处理：检测疑似破折号的情况
                if not use_custom_font and '一一' in text:
                    print(f'图片 {file_name} 检测到疑似破折号(一一)，请后续人工筛查')
                    suspected_dash_files.append(file_name)
                
                output.append(f'{text}\n')  # 不同图片的内容输出到不同行
                success_count += 1
                print(f'成功处理: {file_path}')
            else:
                error_msg = f'识别失败，无结果返回: {result}'
                print(error_msg)
                output.append(f'{error_msg}\n')
                error_count += 1

        except Exception as e:
            error_msg = f'处理{file_path}时出错：{str(e)}'
            print(error_msg)
            output.append(f'{error_msg}\n')
            error_count += 1

    # 写入结果文件
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(''.join(output))
        f.write(f'\n处理统计: 成功{success_count}张, 失败{error_count}张\n')
        
        # 写入疑似破折号信息
        if len(suspected_dash_files) > 0:
            f.write(f'注意: 共检测到 {len(suspected_dash_files)} 处疑似破折号(一一)的情况，出现在以下图片中:\n')
            for file in suspected_dash_files:
                f.write(f'      - {file}\n')
            f.write('请人工筛查确认这些图片中的破折号识别情况。\n')
        
        # 写入字体提示信息
        if use_custom_font:
            # 检测使用的字体类型并提示
            if font_path.endswith('ja-jp.ttf'):
                f.write('\n提示：已检测到ja-jp.ttf字体文件，已启用日语文字识别增强。\n')
            elif font_path.endswith('zh-cn.ttf'):
                f.write('\n提示：已检测到zh-cn.ttf字体文件，已启用简体中文识别增强。\n')
            elif font_path.endswith('zh-tw.ttf'):
                f.write('\n提示：已检测到zh-tw.ttf字体文件，已启用繁体中文识别增强。\n')
        else:
            # 区分没有字体文件和存在多个字体文件的情况
            if len(found_fonts) == 0:
                # 使用语言文件中的提示
                f.write('\n' + lang_data['font_not_detected'] + '\n')
            elif len(found_fonts) > 1:
                # 使用语言文件中的警告
                f.write('\n' + lang_data['multiple_fonts_warning'].format(', '.join([font[0]['file_name'] for font in found_fonts])) + '\n')

    # 写入OCR调试信息文件
    if output_ocr_debug:
        with open(debug_output_file, 'w', encoding='utf-8') as f:
            f.write('=== OCR调试信息 ===\n')
            f.write(f'处理时间: {time.strftime("%Y-%m-%d %H:%M:%S")}\n')
            f.write(f'处理图片总数: {len(image_files)}\n')
            f.write(f'成功处理: {success_count}张\n')
            f.write(f'失败处理: {error_count}张\n')
            f.write(f'使用字体增强: {"是" if use_custom_font else "否"}\n')
            if use_custom_font:
                f.write(f'字体路径: {font_path}\n')
            f.write('\n')
            f.write(''.join(ocr_debug_info))
        print(f'OCR调试信息已保存到: {debug_output_file}')

    # 检查是否有疑似破折号情况
    suspected_dash_count = len(suspected_dash_files)
    print(f'处理完成! 结果已保存到 {output_file}')
    print(f'处理统计: 成功{success_count}张, 失败{error_count}张')
    if suspected_dash_count > 0:
        print(f'注意: 共检测到 {suspected_dash_count} 处疑似破折号(一一)的情况，出现在以下图片中:')
        for file in suspected_dash_files:
            print(f'      - {file}')
        print('请人工筛查确认这些图片中的破折号识别情况。')

    # 输出字体提示信息
    if use_custom_font:
        # 检测使用的字体类型并提示
        if font_path.endswith('ja-jp.ttf'):
            print('\n提示：已检测到ja-jp.ttf字体文件，已启用日语文字识别增强。')
        elif font_path.endswith('zh-cn.ttf'):
            print('\n提示：已检测到zh-cn.ttf字体文件，已启用简体中文识别增强。')
        elif font_path.endswith('zh-tw.ttf'):
            print('\n提示：已检测到zh-tw.ttf字体文件，已启用繁体中文识别增强。')
    else:
        # 区分没有字体文件和存在多个字体文件的情况
        if len(found_fonts) == 0:
            # 使用语言文件中的提示
            print('\n' + lang_data['font_not_detected'])
        elif len(found_fonts) > 1:
            # 使用语言文件中的警告
            print('\n' + lang_data['multiple_fonts_warning'].format(', '.join([font[0]['file_name'] for font in found_fonts])))

except Exception as e:
    print(lang_data['script_execution_error'].format(str(e)))
    sys.exit(1)