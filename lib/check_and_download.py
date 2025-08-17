import os
import sys
import requests
import json
from pathlib import Path

# GitHub仓库基础URL
GITHUB_BASE_URL = 'https://raw.githubusercontent.com/dalizi2333333/railTale_Extractor/main/'

# 需要检查的目录和文件
REQUIRED_DIRS = [
    'lib',
    'lang'
]

# lib目录中需要检查的基本文件
LIB_BASE_FILES = [
    '__init__.py',
    'config.py',
    'dependency_check.py',
    'font_enhancement.py',
    'ocr_language_mapping.json'
]

# 语言优先级顺序
LANGUAGE_PRIORITY = [
    ('zh-cn.json', '简体中文'),
    ('en.json', 'English'),
    ('zh-tw.json', '繁体中文'),
    ('ja-jp.json', '日本語')
]

def check_and_download_files(parent_dir, lang_data=None):
    """检查必要的目录和文件是否存在，如果不存在则从GitHub下载"""
    # 如果没有提供lang_data，使用默认的
    if lang_data is None:
        lang_data = {
            'dir_not_found': '错误: 目录 {} 不存在',
            'file_not_found': '错误: 文件 {} 不存在',
            'downloading_file': '正在下载文件: {}',
            'download_success': '成功下载: {}',
            'download_fail': '下载失败: {}，错误: {}',
            'checking_lib': '正在检查lib目录...',
            'checking_lang': '正在检查lang目录...',
            'lang_files_not_found': '错误: lang目录中没有找到语言文件',
            'using_fallback_lang': '使用默认语言数据'
        }

    # 检查必要的目录
    for dir_name in REQUIRED_DIRS:
        dir_path = os.path.join(parent_dir, dir_name)
        if not os.path.exists(dir_path):
            print(lang_data['dir_not_found'].format(dir_path))
            # 创建目录
            os.makedirs(dir_path, exist_ok=True)
            print(f'已创建目录: {dir_path}')

    # 检查lib目录中的基本文件
    print(lang_data['checking_lib'])
    lib_dir = os.path.join(parent_dir, 'lib')
    for file_name in LIB_BASE_FILES:
        file_path = os.path.join(lib_dir, file_name)
        if not os.path.exists(file_path):
            print(lang_data['file_not_found'].format(file_path))
            # 从GitHub下载文件
            download_file_from_github(f'lib/{file_name}', file_path, lang_data)

    # 检查lang目录中的语言文件
    print(lang_data['checking_lang'])
    lang_dir = os.path.join(parent_dir, 'lang')
    lang_files = [f for f in os.listdir(lang_dir) if f.lower().endswith('.json')]

    if not lang_files:
        print(lang_data['lang_files_not_found'])
        # 下载默认语言文件
        default_lang_file = LANGUAGE_PRIORITY[0][0]
        file_path = os.path.join(lang_dir, default_lang_file)
        download_file_from_github(f'lang/{default_lang_file}', file_path, lang_data)
        lang_files = [default_lang_file]

    return True

def download_file_from_github(github_path, local_path, lang_data):
    """从GitHub下载文件，支持重试机制"""
    url = f'{GITHUB_BASE_URL}{github_path}'
    print(lang_data['downloading_file'].format(url))

    max_retries = 3
    timeout = 30  # 增加超时时间到30秒

    for attempt in range(max_retries):
        try:
            response = requests.get(url, timeout=timeout)
            response.raise_for_status()

            # 确保目录存在
            os.makedirs(os.path.dirname(local_path), exist_ok=True)

            # 保存文件
            with open(local_path, 'wb') as f:
                f.write(response.content)

            print(lang_data['download_success'].format(local_path))
            return True
        except requests.exceptions.RequestException as e:
            error_msg = str(e)
            if attempt < max_retries - 1:
                print(lang_data['download_fail'].format(url, f'{error_msg}, 第{attempt+1}次尝试失败，将重试...'))
            else:
                print(lang_data['download_fail'].format(url, f'{error_msg}, 已达到最大重试次数{max_retries}'))
    return False

def load_language_file_with_check(parent_dir):
    """检查并加载语言文件"""
    # 创建默认语言数据
    default_lang_data = {
        'dir_not_found': '错误: 目录 {} 不存在',
        'file_not_found': '错误: 文件 {} 不存在',
        'downloading_file': '正在下载文件: {}',
        'download_success': '成功下载: {}',
        'download_fail': '下载失败: {}，错误: {}',
        'checking_lib': '正在检查lib目录...',
        'checking_lang': '正在检查lang目录...',
        'lang_files_not_found': '错误: lang目录中没有找到语言文件',
        'using_fallback_lang': '使用默认语言数据'
    }

    # 先检查并下载必要的文件，传入默认语言数据
    check_and_download_files(parent_dir, default_lang_data)

    lang_dir = os.path.join(parent_dir, 'lang')
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

    # 如果没有找到优先级列表中的语言文件，使用默认数据
    print(default_lang_data['using_fallback_lang'])
    return {
        'lib_import_success': '成功导入 {}',
        'lib_import_fail': '导入失败 {}: {}',
        'missing_required_libs': '错误: 缺少必要的Python库',
        'config_not_found': '错误: 配置文件未找到',
        'config_download_success': '成功下载配置文件到: {}',
        'config_download_fail': '下载配置文件失败: {}\n请手动从 {} 获取配置文件',
        'config_read_error': '读取配置文件错误: {}',
        'missing_required_config': '错误: 缺少必要的配置项: {}',
        'ocr_api_config_prompt': '错误: 请先在config.txt中配置百度OCR API的APP_ID、API_KEY和SECRET_KEY\n获取方法: 访问https://ai.baidu.com/，注册账号并创建OCR应用',
        'script_execution_error': '脚本执行出错: {}',
        'current_language': 'default'
    }

if __name__ == '__main__':
    # 如果直接运行此文件，获取父级目录并执行检查
    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(current_dir)
    check_and_download_files(parent_dir)
    print('检查和下载完成！')