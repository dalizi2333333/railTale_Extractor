from ntpath import exists
import os
import sys
import requests
import json
from pathlib import Path

# 目录结构配置
DIRECTORY_STRUCTURE = {
    'lib': {
        'files': [
                '__init__.py',
                'dependency_check.py',
                'lang_manager.py',
                'supported_fonts.json',
                'text_processor.py'
            ],
        'subdirectories': {
            'ocr_core': {
                'files': [
                    '__init__.py',
                    'ocr_module.py',
                    'ocr_module_interface.py',
                    'ocr_module_bootstraper.py'
                ]
            },
            'lang': {},
            'config': {
                'files': [
                    '__init__.py',
                    'config_ensure.py',
                    'config_generator.py',
                    'config_loader.py',
                    'config_manager.py',
                    'default_config.py'
                ]
            },
            'text_extracting': {
                'files': [
                    '__init__.py',
                    'font_enhancement_detector.py',
                    'text_extractor.py'
                ]
            },
            'ocr_modules': {}
        }
    }
}

# 语言优先级顺序
LANGUAGE_PRIORITY = [
    ('zh-cn.json', '简体中文'),
    ('en.json', 'English'),
    ('zh-tw.json', '繁体中文'),
    ('ja-jp.json', '日本語')
]

# 默认语言数据 - 仅包含加载正式语言文件前可能需要的基本条目
DEFAULT_LANG_DATA = {
    'dir_not_found': '错误: 目录 {} 不存在',
    'dir_created': '已创建目录: {}',
    'lang_files_not_found': '错误: lang目录中没有找到语言文件',
    'download_fail': '下载失败: {}，错误: {}',
    'downloading_file': '正在下载文件: {}',
    'download_success': '成功下载: {}',
    'load_default_lang_fail': '加载下载的默认语言文件失败: {}\n程序无法继续执行，将退出。',
    'load_lang_file_fail': '加载语言文件 {} 失败: {}',
    'retry_attempt': '第{}次尝试失败，将重试...',
    'max_retries_reached': '已达到最大重试次数{}',
    'dir_checking': '正在检查目录: {}',
    'file_not_found': '文件不存在: {}',
    'file_found': '文件已找到: {}',
    'critical_file_download_fail': '关键文件下载失败: {}',
    'exit_due_to_download_fail': '由于关键文件下载失败，程序将退出。',
    'check_complete': '检查完成！',
    'ocr_mapping_load_fail': '加载OCR语言映射文件失败: {}'
}


def _get_paths(paths=None):
    """获取路径配置

    Args:
        paths (dict, optional): 路径配置字典. 如果未提供，将使用默认值

    Returns:
        dict: 包含以下路径的配置字典:
            - parent_dir: 项目根目录
            - process_dir: 待处理文件目录
            - project_download_url: 项目文件下载URL
            - lang_dir: 语言文件目录
    """
    if paths is None:
        paths = {}

    # 设置parent_dir默认值: bootstrap.py所在目录的父级目录
    parent_dir = paths.get('parent_dir')
    if parent_dir is None:
        # 获取当前文件所在目录
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # 检查当前目录是否名为'lib'
        current_dir_name = os.path.basename(current_dir)
        if current_dir_name != 'lib':
            raise ValueError(f"当前文件必须位于'lib'目录中，但实际位于'{current_dir_name}'目录")
        # 获取父级目录
        parent_dir = os.path.dirname(current_dir)

    # 设置project_download_url默认值
    project_download_url = paths.get('project_download_url')
    if project_download_url is None:
        project_download_url = 'https://raw.githubusercontent.com/dalizi2333333/railTale_Extractor/main/'

    # 设置process_dir默认值: parent_dir下的to_be_process目录
    process_dir = paths.get('process_dir')
    if process_dir is None:
        process_dir = os.path.join(parent_dir, 'to_be_process')
        # 如果目录不存在则创建
        if not os.path.exists(process_dir):
            os.makedirs(process_dir)

    # 设置lang_dir: lib目录下的lang目录
    lib_dir = os.path.dirname(os.path.abspath(__file__))
    lang_dir = os.path.join(lib_dir, 'lang')

    return {
        'parent_dir': parent_dir,
        'process_dir': process_dir,
        'project_download_url': project_download_url,
        'lang_dir': lang_dir
    }


def _download_file_from_github(github_path, local_path, download_url, lang_data):
    """从GitHub下载文件，支持重试机制

    Args:
        github_path (str): GitHub上的文件路径
        local_path (str): 本地保存路径
        download_url (str): 下载基础URL
        lang_data (dict): 语言数据字典，用于获取本地化消息

    Returns:
        bool: 下载是否成功
    """
    url = f'{download_url}{github_path}'
    print(lang_data['downloading_file'].format(url))

    max_retries = 3
    timeout = 10

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
                print(lang_data['download_fail'].format(url, error_msg))
                print(lang_data['retry_attempt'].format(attempt+1))
            else:
                print(lang_data['download_fail'].format(url, error_msg))
                print(lang_data['max_retries_reached'].format(max_retries))
    return False


def _check_directory_structure(base_path, dir_config, github_prefix, download_url, lang_data):
    """递归检查目录结构并下载缺失文件

    Args:
        base_path (str): 当前检查的基础目录路径
        dir_config (dict): 目录配置字典，包含files和subdirectories等键
        github_prefix (str): GitHub路径前缀
        download_url (str): 下载基础URL
        lang_data (dict): 语言数据字典，用于获取本地化消息

    Returns:
        bool: 关键文件是否全部成功下载
    """
    critical_files_downloaded = True

    # 检查当前目录是否存在
    if not os.path.exists(base_path):
        print(lang_data['dir_not_found'].format(base_path))
        os.makedirs(base_path, exist_ok=True)
        print(lang_data['dir_created'].format(base_path))

    # 检查当前目录中的文件
    if 'files' in dir_config:
        #print(lang_data['dir_checking'].format(base_path))
        for file_name in dir_config['files']:
            file_path = os.path.join(base_path, file_name)
            # 检查文件是否存在
            if os.path.exists(file_path):
                #print(lang_data['file_found'].format(file_path))
                pass#暂时提示
            else:
                print(lang_data['file_not_found'].format(file_path))
                # 构建GitHub路径
                github_path = f'{github_prefix}/{file_name}' if github_prefix else file_name
                # 从GitHub下载文件
                if not _download_file_from_github(github_path, file_path, download_url, lang_data):
                    critical_files_downloaded = False
                    print(lang_data['critical_file_download_fail'].format(github_path))

    # 递归检查子目录
    if 'subdirectories' in dir_config:
        for subdir_name, subdir_config in dir_config['subdirectories'].items():
            subdir_path = os.path.join(base_path, subdir_name)
            # 构建子目录的GitHub前缀
            new_github_prefix = f'{github_prefix}/{subdir_name}' if github_prefix else subdir_name
            subdir_critical = _check_directory_structure(subdir_path, subdir_config, new_github_prefix, download_url, lang_data)
            critical_files_downloaded = critical_files_downloaded and subdir_critical

    return critical_files_downloaded


def _get_language_data(paths):
    """确定语言文件存在，加载语言文件并返回语言数据

    Args:
        paths (dict): 路径配置字典，需包含lang_dir等键

    Returns:
        dict: 语言数据字典，包含本地化消息和当前语言设置
    """
    # 初始使用默认语言数据
    lang_data = DEFAULT_LANG_DATA

    # 确保lang目录存在
    lang_dir = paths['lang_dir']
    if not os.path.exists(lang_dir):
        print(f"Directory not found: {lang_dir}")
        os.makedirs(lang_dir, exist_ok=True)
        print(f"Directory created: {lang_dir}")

    # 检查lang目录中的语言文件
    lang_files = [f for f in os.listdir(lang_dir) if f.lower().endswith('.json')]

    # 如果没有语言文件，尝试下载默认语言文件
    if not lang_files:
        print(lang_data['lang_files_not_found'])
        current_lang_file = LANGUAGE_PRIORITY[0][0]
        file_path = os.path.join(lang_dir, current_lang_file)
        _download_file_from_github(f'lib/lang/{current_lang_file}', file_path, paths['project_download_url'], lang_data)
        lang_files = [current_lang_file]

    # 加载语言文件
    if lang_files:
        # 如果只有一个语言文件，直接加载
        if len(lang_files) == 1:
            current_lang_file = lang_files[0]
            lang_file = os.path.join(lang_dir, current_lang_file)
            try:
                with open(lang_file, 'r', encoding='utf-8') as f:
                        loaded_data = json.load(f)
                        # 合并加载的数据到现有语言数据
                        lang_data = {**lang_data, **loaded_data}
                        lang_data['current_language'] = current_lang_file
            except Exception as e:
                print(lang_data['load_lang_file_fail'].format(current_lang_file, str(e)))
                # 继续使用默认数据
        # 多个语言文件，按照优先级顺序加载
        else:
            for file_name, display_name in LANGUAGE_PRIORITY:
                if file_name in lang_files:
                    current_lang_file = file_name
                    lang_file = os.path.join(lang_dir, current_lang_file)
                    try:
                        with open(lang_file, 'r', encoding='utf-8') as f:
                            loaded_data = json.load(f)
                            # 合并加载的数据到现有语言数据
                            lang_data = {**lang_data, **loaded_data}
                            lang_data['current_language'] = current_lang_file
                            break
                    except Exception as e:
                        print(lang_data['load_lang_file_fail'].format(file_name, str(e)))
                        # 继续尝试下一个语言文件
    else:
        # 如果没有找到语言文件，下载默认语言文件
        print(lang_data['lang_files_not_found'])
        current_lang_file = LANGUAGE_PRIORITY[0][0]
        file_path = os.path.join(lang_dir, current_lang_file)
        _download_file_from_github(f'lang/{current_lang_file}', file_path, paths['project_download_url'], lang_data)

        # 尝试加载下载的默认语言文件
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                loaded_data = json.load(f)
                # 合并加载的数据到现有语言数据
                lang_data = {**lang_data, **loaded_data}
                lang_data['current_language'] = current_lang_file
        except Exception as e:
            print(lang_data['load_default_lang_fail'].format(str(e)))
            sys.exit(1)

    return lang_data

def _check_and_download_files(paths, lang_data):
    """检查必要的目录和文件是否存在，如果不存在则从GitHub下载

    Args:
        paths (dict): 路径配置字典
        lang_data (dict): 语言数据字典，用于获取本地化消息

    Raises:
        SystemExit: 如果关键文件下载失败，程序将退出
    """
    # 检查目录结构
    critical_files_downloaded = True
    # 从根目录结构开始检查
    for dir_name, dir_config in DIRECTORY_STRUCTURE.items():
        dir_path = os.path.join(paths['parent_dir'], dir_name)
        dir_critical = _check_directory_structure(dir_path, dir_config, dir_name, paths['project_download_url'], lang_data)
        critical_files_downloaded = critical_files_downloaded and dir_critical

    # 如果关键文件下载失败，终止程序
    if not critical_files_downloaded:
        print(lang_data['exit_due_to_download_fail'])
        sys.exit(1)

    print(lang_data['check_complete'])

# 引导函数，供外部调用
def bootstrap(paths=None):
    """引导函数，初始化项目

    Args:
        paths (dict, optional): 路径配置字典. 如果未提供，将使用默认值

    Returns:
        dict: 包含以下对象的字典:
            - config_manager: 配置管理器实例
            - lang_manager: 语言管理器实例
            - paths: 路径配置字典
            - text: 提取的文本数据
    """
    # 1. 获取路径配置
    paths = _get_paths(paths)

    # 2. 获取语言数据
    lang_data = _get_language_data(paths)

    # 3. 检查并下载必要文件
    _check_and_download_files(paths, lang_data)

    # 4. 初始化语言管理器
    from lang_manager import LangManager
    lang_manager = LangManager.initialize(lang_data)

    # 5. 初始化配置管理器
    from config.config_manager import ConfigManager
    config_manager = ConfigManager.initialize(paths)

    # 加载配置文件
    from config.config_ensure import ensure_config
    from config.config_loader import ConfigLoader

    # 确保配置文件存在并加载默认配置
#    if ensure_config():
#        ConfigLoader().load_config()
    exists_config = ensure_config()
    if exists_config:
        ConfigLoader().load_config()

    # 6. 初始化OCR模块
    from ocr_core.ocr_module_bootstraper import OCRModuleBootstraper
    module_bootstraper = OCRModuleBootstraper()
    if not module_bootstraper.bootstrap_module():
        print(LangManager.get_lang_data()['module_bootstrap_fail'].format(ConfigManager.get('OCR_MODULE' , 'baidu')))
        sys.exit(1)

    # 7. 处理项目
    from text_processor import TextProcessor
    text = TextProcessor().run()

    return {
        'config_manager': config_manager,
        'lang_manager': lang_manager,
        'paths': paths,
        'exists_config': exists_config,
        'text': text
    }