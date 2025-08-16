import os
import sys
import time

# 获取当前脚本所在目录
current_dir = os.path.dirname(os.path.abspath(__file__))
# 获取父级目录
parent_dir = os.path.dirname(current_dir)

# 检测父级目录中是否存在支持的字体文件
supported_fonts = [
    ('zh-cn.ttf', 'CHN_ENG'),  # 简体中文
    ('zh-tw.ttf', 'CHN_ENG'),  # 繁体中文
    ('ja-jp.ttf', 'JAP')       # 日语
]

use_custom_font = False
font_path = None
font_language = 'CHN_ENG'

# 检查父目录中存在的字体文件数量
found_fonts = []
for font_file, language in supported_fonts:
    current_font_path = os.path.join(parent_dir, font_file)
    if os.path.exists(current_font_path):
        found_fonts.append((font_file, language, current_font_path))

# 如果只找到一个字体文件，则使用它
if len(found_fonts) == 1:
    font_file, language, current_font_path = found_fonts[0]
    use_custom_font = True
    font_path = current_font_path
    font_language = language
elif len(found_fonts) > 1:
    print('警告: 父目录中存在多个字体文件，将不启用字体增强识别功能')
    print('      请确保父目录中只存在一种字体文件: zh-cn.ttf, zh-tw.ttf 或 ja-jp.ttf')

# 必要的库
required_libraries = [
    ('PIL', 'Pillow'),
    ('chardet', 'chardet'),
    ('aip', 'baidu-aip'),
]

# 根据是否使用自定义字体设置OCR参数
if use_custom_font:
    print(f'检测到字体文件: {font_path}，将使用该字体提高OCR识别精度')
else:
    print('未检测到支持的字体文件，使用默认字体设置')

# 检查必要的库是否安装
missing_libraries = []
for lib_name, pip_name in required_libraries:
    try:
        __import__(lib_name)
        # 验证导入是否成功
        module = sys.modules.get(lib_name)
        if module is None:
            raise ImportError(f"无法加载模块 {lib_name}")
        print(f"成功导入 {lib_name}")  # 调试信息
    except ImportError as e:
        missing_libraries.append((lib_name, pip_name))
        print(f"导入失败 {lib_name}: {str(e)}")  # 调试信息

if missing_libraries:
    print('错误: 缺少必要的Python库')
    # 打印Python环境信息
    print(f'当前Python解释器路径: {sys.executable}')
    print(f'Python版本: {sys.version}')
    print('Python路径:')
    for path in sys.path:
        print(f'  - {path}')
    
    for lib_name, pip_name in missing_libraries:
        print(f'  - {lib_name} (推荐使用命令安装: pip install {pip_name})')
    print('\n安装提示:')
    print('1. 首先必须更新pip到最新版本(安装opencv-python必需):')
    print('   python -m pip install --upgrade pip')
    print('2. 如果安装失败，可能是网络问题，建议使用国内镜像源:')
    for _, pip_name in missing_libraries:
        if pip_name == 'opencv-python':
            print(f'   pip install -i https://mirrors.aliyun.com/pypi/simple/ {pip_name} --no-binary :all:')
        else:
            print(f'   pip install -i https://mirrors.aliyun.com/pypi/simple/ {pip_name}')
    print('3. 安装opencv-python时如果遇到编码错误，尝试设置环境变量:')
    print('   set PYTHONUTF8=1')
    print('   或者在命令前添加:')
    print('   $env:PYTHONUTF8=1  (PowerShell)')
    print('4. Windows用户如果遇到权限问题，请以管理员身份运行命令提示符')
    print('5. macOS/Linux用户如果遇到权限问题，尝试使用sudo:')
    for _, pip_name in missing_libraries:
        print(f'   sudo pip install {pip_name}')
    print('6. 确保使用的Python环境与安装库时的环境一致')
    sys.exit(1)

# 导入必要的库
from PIL import Image
from aip import AipOcr

# 已完全移除图像预处理相关代码

# 读取配置文件函数
def read_config():
    # 配置文件路径
    config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.txt')
    
    # 检查配置文件是否存在，如果不存在则创建
    if not os.path.exists(config_path):
        print('配置文件config.txt不存在，正在创建...')
        # 配置文件不存在时的默认内容
        config_content = """# 百度OCR API配置文件
# 请将以下参数替换为您自己的密钥

# 百度AI平台账号的APP_ID
APP_ID = '你的APP_ID'

# 百度AI平台账号的API_KEY
API_KEY = '你的API_KEY'

# 百度AI平台账号的SECRET_KEY
SECRET_KEY = '你的SECRET_KEY'

# 是否输出OCR调试信息到独立文件
# 可选值: true, false
OUTPUT_OCR_DEBUG = 'false'

# OCR文本提取标记配置
# 开始标记: 当检测到这些文字块时开始记录每张图片内识别到的文本，多个标记用逗号分隔
START_MARKERS = '剧情梗概'

# 结束标记: 当检测到这些文字块时停止记录每张图片内识别到的文本，多个标记用逗号分隔
STOP_MARKERS = 'i,存在分支剧情选项,取消,×,⑧取消'

# 配置说明：
# 1. 访问 https://ai.baidu.com/ 注册账号并创建OCR应用
# 2. 在应用详情页获取APP_ID、API_KEY和SECRET_KEY
# 3. 将获取到的密钥填入上面的对应字段中
# 4. 如需输出OCR调试信息，将OUTPUT_OCR_DEBUG设置为'true'
# 5. 可根据需要修改START_MARKERS和STOP_MARKERS来调整文本提取的起始和结束条件
# 6. 保存文件后，运行process_images.py脚本"""
        with open(config_path, 'w', encoding='utf-8') as f:
            f.write(config_content)
        print(f'配置文件已创建: {config_path}')
        print('请编辑该文件并填入您的百度OCR API密钥，然后重新运行脚本')
        sys.exit(1)
    
    # 读取配置文件
    config = {}
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            for line in f:
                # 跳过注释和空行
                if line.strip().startswith('#') or not line.strip():
                    continue
                # 解析配置项
                if '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip().strip("'").strip('"')
                    config[key] = value
    except Exception as e:
        print(f'读取配置文件出错: {str(e)}')
        sys.exit(1)
    
    # 检查必要的配置项是否存在
    required_keys = ['APP_ID', 'API_KEY', 'SECRET_KEY']
    for key in required_keys:
        if key not in config:
            print(f'错误: 配置文件中缺少必要的项 {key}')
            sys.exit(1)
    
    return config

# 读取配置
config = read_config()
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
    'language_type': font_language,  # 根据字体类型设置语言
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
    print('错误: 请先在config.txt中配置百度OCR API的APP_ID、API_KEY和SECRET_KEY')
    print('获取方法: 访问https://ai.baidu.com/，注册账号并创建OCR应用')
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
                    debug_entry += f"字体类型: {font_language}\n"
                    debug_entry += f"原始识别结果: {result}\n"
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
                f.write('\n提示：未检测到自定义字体文件，推荐在游戏资源文件中找到以下ttf字体文件并放在父目录:\n')
                f.write('      - zh-cn.ttf (简体中文)\n')
                f.write('      - zh-tw.ttf (繁体中文)\n')
                f.write('      - ja-jp.ttf (日语，安装后将启用日语文字识别)\n')
                f.write('      加载对应字体文件可有效提高OCR识别准确率，特别是避免破折号(——)被错误识别为(一一)的问题。\n')
            elif len(found_fonts) > 1:
                f.write('\n警告：父目录中存在多个字体文件，不启用字体增强识别功能。\n')
                f.write('      请确保父目录中只存在一种字体文件: zh-cn.ttf, zh-tw.ttf 或 ja-jp.ttf\n')
                f.write('      当前检测到的字体文件: ' + ', '.join([font[0] for font in found_fonts]) + '\n')

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
            print('\n提示：未检测到自定义字体文件，推荐在游戏资源文件中找到以下ttf字体文件并放在父目录:')
            print('      - zh-cn.ttf (简体中文)')
            print('      - zh-tw.ttf (繁体中文)')
            print('      - ja-jp.ttf (日语，安装后将启用日语文字识别)')
            print('      加载对应字体文件可有效提高OCR识别准确率，特别是避免破折号(——)被错误识别为(一一)的问题。')
        elif len(found_fonts) > 1:
            print('\n警告：父目录中存在多个字体文件，不启用字体增强识别功能。')
            print('      请确保父目录中只存在一种字体文件: zh-cn.ttf, zh-tw.ttf 或 ja-jp.ttf')
            print('      当前检测到的字体文件: ' + ', '.join([font[0] for font in found_fonts]))

except Exception as e:
    print(f'脚本执行出错: {str(e)}')
    sys.exit(1)