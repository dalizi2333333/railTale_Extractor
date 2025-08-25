import os
import json
import sys

from lang_manager import LangManager
from config.config_manager import ConfigManager

# 百度OCR模块的bootstrap
# 此文件由ModuleBootstraper加载和使用，负责模块的依赖管理、配置和初始化


def get_required_dependencies():
    """
    返回模块需要的额外依赖
    这些依赖不会被自动安装，需要用户手动安装或通过依赖管理工具安装
    
    Returns:
        dict: 包含依赖信息的字典，格式为 {import_name: {'install_name': install_name, 'version': version}}
    """
    return {
        'aip': {
            'install_name': 'baidu-aip',
            'version': '>=4.0.0'
        }
    }


def get_required_config_items():
    """
    返回模块需要的配置项
    这些配置项将被添加到配置文件中
    
    Returns:
        dict: 包含配置项名称、类型、默认值和描述的字典
    """
    
    return {
        'BAIDU_APP_ID': {
            'type': 'str',
            'default': 'your_app_id',
            'description_key': 'baidu_app_id_desc',
            'cannot_use_default': True
        },
        'BAIDU_API_KEY': {
            'type': 'str',
            'default': 'your_api_key',
            'description_key': 'baidu_api_key_desc', 
            'cannot_use_default': True
        },
        'BAIDU_SECRET_KEY': {
            'type': 'str',
            'default': 'your_secret_key',
            'description_key': 'baidu_secret_key_desc',
            'cannot_use_default': True
        }
    }


def has_mandatory_config():
    """
    返回模块是否有不可为默认值的配置项
    如果返回True，当根据complete_module方法补全模块后，程序会退出并提醒用户修改配置
    
    Returns:
        bool: 是否有不可为默认值的配置项
    """
    return True


def _download_file_from_github(github_path, local_path, download_url, default_lang_data=None):
    """从GitHub下载文件

    Args:
        github_path (str): GitHub路径
        local_path (str): 本地文件路径
        download_url (str): 下载基础URL

    Returns:
        bool: 是否下载成功
    """
    max_retries = 3
    timeout = 10
    url = f'{download_url}/{github_path}'

    for attempt in range(max_retries):
        try:
            import requests
            response = requests.get(url, timeout=timeout)
            response.raise_for_status()

            # 确保目录存在
            os.makedirs(os.path.dirname(local_path), exist_ok=True)

            # 保存文件
            with open(local_path, 'wb') as f:
                f.write(response.content)

            # 尝试使用语言数据，如果失败则使用默认文本
            try:
                print(LangManager.get_module_lang('download_success').format(local_path))
            except (KeyError, Exception):
                if default_lang_data and 'download_success' in default_lang_data:
                    print(default_lang_data['download_success'].format(local_path))
                else:
                    print(f'下载成功: {local_path}')
            return True
        except requests.exceptions.RequestException as e:
            error_msg = str(e)
            if attempt < max_retries - 1:
                # 尝试使用语言数据，如果失败则使用默认文本
                try:
                    print(LangManager.get_module_lang('download_fail').format(url, error_msg))
                    print(LangManager.get_module_lang('retry_attempt').format(attempt+1))
                except (KeyError, Exception):
                    if default_lang_data:
                        if 'download_fail' in default_lang_data:
                            print(default_lang_data['download_fail'].format(url, error_msg))
                        if 'retry_attempt' in default_lang_data:
                            print(default_lang_data['retry_attempt'].format(attempt+1))
                    else:
                        print(f'下载失败 ({url}): {error_msg}')
                        print(f'重试尝试 {attempt+1}...')
            else:
                # 尝试使用语言数据，如果失败则使用默认文本
                try:
                    print(LangManager.get_module_lang('download_fail').format(url, error_msg))
                    print(LangManager.get_module_lang('max_retries_reached').format(max_retries))
                except (KeyError, Exception):
                    if default_lang_data:
                        if 'download_fail' in default_lang_data:
                            print(default_lang_data['download_fail'].format(url, error_msg))
                        if 'max_retries_reached' in default_lang_data:
                            print(default_lang_data['max_retries_reached'].format(max_retries))
                    else:
                        print(f'下载失败 ({url}): {error_msg}')
                        print(f'已达到最大重试次数 ({max_retries})')
    return False


def _check_module_files(module_dir, download_url, default_lang_data=None):
    """检查模块文件结构并下载缺失文件

    Args:
        module_dir (str): 模块目录路径
        download_url (str): 下载基础URL

    Returns:
        bool: 关键文件是否全部成功下载
    """
    critical_files_downloaded = True

    # 定义模块目录结构
    MODULE_STRUCTURE = {
        'files': ['__init__.py', 'baidu_ocr_module.py', 'module_bootstrap.py', 'debug_utils.py'],
        'subdirectories': {
            'lang': {
                'files': ['zh-cn.json', 'en.json']
            }
        }
    }

    # 递归检查目录结构
    def _check_dir_structure(base_path, dir_config, github_prefix, default_lang_data=None):
        nonlocal critical_files_downloaded

        # 检查当前目录是否存在
        if not os.path.exists(base_path):
            # 为dir_not_found添加异常处理
            try:
                print(LangManager.get_module_lang('dir_not_found').format(base_path))
            except (KeyError, Exception):
                if default_lang_data and 'dir_not_found' in default_lang_data:
                    print(default_lang_data['dir_not_found'].format(base_path))
                else:
                    print(f'目录未找到: {base_path}')
            os.makedirs(base_path, exist_ok=True)
            # 为dir_created添加异常处理
            try:
                print(LangManager.get_module_lang('dir_created').format(base_path))
            except (KeyError, Exception):
                if default_lang_data and 'dir_created' in default_lang_data:
                    print(default_lang_data['dir_created'].format(base_path))
                else:
                    print(f'已创建目录: {base_path}')

        # 检查当前目录中的文件
        if 'files' in dir_config:
            # 为dir_checking添加异常处理
            try:
                print(LangManager.get_module_lang('dir_checking').format(base_path))
            except (KeyError, Exception):
                if default_lang_data and 'dir_checking' in default_lang_data:
                    print(default_lang_data['dir_checking'].format(base_path))
                else:
                    print(f'正在检查目录: {base_path}')
            for file_name in dir_config['files']:
                file_path = os.path.join(base_path, file_name)
                # 检查文件是否存在
                if os.path.exists(file_path):
                    # 为file_found添加异常处理
                    try:
                        print(LangManager.get_module_lang('file_found').format(file_path))
                    except (KeyError, Exception):
                        if default_lang_data and 'file_found' in default_lang_data:
                            print(default_lang_data['file_found'].format(file_path))
                        else:
                            print(f'找到文件: {file_path}')
                else:
                    # 为file_not_found添加异常处理
                    try:
                        print(LangManager.get_module_lang('file_not_found').format(file_path))
                    except (KeyError, Exception):
                        if default_lang_data and 'file_not_found' in default_lang_data:
                            print(default_lang_data['file_not_found'].format(file_path))
                        else:
                            print(f'未找到文件: {file_path}')
                    # 构建GitHub路径
                    github_path = f'{github_prefix}/{file_name}' if github_prefix else file_name
                    # 从GitHub下载文件
                    if not _download_file_from_github(github_path, file_path, download_url):
                        critical_files_downloaded = False
                        # 为critical_file_download_fail添加异常处理
                        try:
                            print(LangManager.get_module_lang('critical_file_download_fail').format(github_path))
                        except (KeyError, Exception):
                            if default_lang_data and 'critical_file_download_fail' in default_lang_data:
                                print(default_lang_data['critical_file_download_fail'].format(github_path))
                            else:
                                print(f'关键文件下载失败: {github_path}')

        # 递归检查子目录
        if 'subdirectories' in dir_config:
            for subdir_name, subdir_config in dir_config['subdirectories'].items():
                subdir_path = os.path.join(base_path, subdir_name)
                # 构建子目录的GitHub前缀
                new_github_prefix = f'{github_prefix}/{subdir_name}' if github_prefix else subdir_name
                # 传递default_lang_data参数给递归调用
                _check_dir_structure(subdir_path, subdir_config, new_github_prefix, default_lang_data)

    # 开始检查模块目录结构
    # 传递default_lang_data参数
    _check_dir_structure(module_dir, MODULE_STRUCTURE, '', default_lang_data)
    return critical_files_downloaded


def complete_module():
    """
    补全模块的方式
    负责初始化模块所需的语言文件和其他资源
    
    Returns:
        bool: 是否补全成功
    """
    try:
        # 获取模块目录
        module_dir, _ = ConfigManager.get_ocr_module_dir('baidu')

        # 下载基础URL
        download_url = 'https://raw.githubusercontent.com/dalizi2333333/railTale_Extractor/0.1.1/lib/ocr_modules/baidu'

        # 确保lang目录存在
        lang_dir = os.path.join(module_dir, 'lang')
        if not os.path.exists(lang_dir):
            os.makedirs(lang_dir, exist_ok=True)
            print(f'创建语言目录: {lang_dir}')

        # 初始使用默认语言数据
        default_lang_data = {
            'dir_not_found': '目录未找到: {{}}',
            'dir_created': '已创建目录: {{}}',
            'dir_checking': '正在检查目录: {{}}',
            'file_found': '找到文件: {{}}',
            'file_not_found': '未找到文件: {{}}',
            'download_success': '下载成功: {{}}',
            'download_fail': '下载失败 ({{}}): {{}}',
            'retry_attempt': '重试尝试 {{}}...',
            'max_retries_reached': '已达到最大重试次数 ({{}})',
            'critical_file_download_fail': '关键文件下载失败: {{}}',
            'check_complete': '检查完成',
            'exit_due_to_download_fail': '由于文件下载失败，程序退出'
        }

        # 检查语言文件是否存在，如果不存在则从GitHub下载
        languages = ['zh-cn', 'en']
        for lang in languages:
            lang_file = os.path.join(lang_dir, f'{lang}.json')
            if not os.path.exists(lang_file):
                print(f'未找到语言文件: {lang_file}')
                github_path = f'lang/{lang}.json'
                # 传递默认语言数据给下载函数
                if not _download_file_from_github(github_path, lang_file, download_url, default_lang_data):
                    print(f'下载语言文件失败: {lang_file}')
                    sys.exit(1)
            else:
                print(f'找到语言文件: {lang_file}')

        # 加载语言数据
        LangManager.load_module_language_file(module_dir)
        # 检查并下载模块文件
        # 为check_start添加异常处理
        try:
            print(LangManager.get_module_lang('check_start'))
        except (KeyError, Exception):
            if default_lang_data and 'check_start' in default_lang_data:
                print(default_lang_data['check_start'])
            else:
                print('开始检查模块文件...')

        if not _check_module_files(module_dir, download_url, default_lang_data):
            # 为exit_due_to_download_fail添加异常处理
            try:
                print(LangManager.get_module_lang('exit_due_to_download_fail'))
            except (KeyError, Exception):
                if default_lang_data and 'exit_due_to_download_fail' in default_lang_data:
                    print(default_lang_data['exit_due_to_download_fail'])
                else:
                    print('由于文件下载失败，程序退出')
            return False

        # 为check_complete添加异常处理
        try:
            print(LangManager.get_module_lang('check_complete'))
        except (KeyError, Exception):
            if default_lang_data and 'check_complete' in default_lang_data:
                print(default_lang_data['check_complete'])
            else:
                print('检查完成')
        return True
    except Exception as e:
        # 为complete_fail添加异常处理和调试信息
        try:
            lang_data = LangManager.get_module_lang_data()
            print(f'语言数据状态: {lang_data}')
            if 'complete_fail' in lang_data:
                print(lang_data['complete_fail'].format(str(e)))
            else:
                print(f'补全失败: {str(e)}')
        except Exception as lang_e:
            print(f'获取语言数据时出错: {str(lang_e)}')
            print(f'补全失败: {str(e)}')
        return False

def get_module_class():
    """
    返回模块的主类
    这个方法会被ModuleBootstraper调用，用于注册模块
    
    Returns:
        class: 模块的主类
    """
    from baidu_ocr_module import BaiduOCRModule
    return BaiduOCRModule

# 模块初始化代码
if __name__ == '__main__':
    # 当直接运行此文件时，可以用于测试模块补全功能
    complete_module()
    print('百度OCR模块bootstrap完成')