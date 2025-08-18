import os
import sys
import requests
import json
from pathlib import Path

# GitHub仓库基础URL
GITHUB_BASE_URL = 'https://raw.githubusercontent.com/dalizi2333333/railTale_Extractor/main/'

# 目录结构配置
DIRECTORY_STRUCTURE = {
    'lib': {
        'files': [
                '__init__.py',
                'dependency_check.py',
                'font_enhancement.py',
                'ocr_language_mapping.json',
                'ocr_module_loader.py',
                'text_processing_loader.py'
            ],
        'subdirectories': {
            'ocr_core': {
                'files': [
                    '__init__.py',
                    'ocr_module.py',
                    'ocr_module_interface.py',
                    'ocr_module_registry.py'
                ]
            },
            'lang': {},
            'config': {
                'files': [
                    '__init__.py',
                    'base_config.py',
                    'config_generator.py',
                    'config_loader.py',
                    'config_manager.py',
                    'module_config.py'
                ]
            },
            'text_processing': {
                'files': [
                    '__init__.py',
                    'text_processor.py'
                ]
            }
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

class LocalizationManager:
    """本地化管理器，负责语言文件加载和本地化功能"""
    # 单例实例
    _instance = None

    def __new__(cls, parent_dir=None):
        if cls._instance is None:
            cls._instance = super(LocalizationManager, cls).__new__(cls)
            # 确保parent_dir指向项目根目录
            if parent_dir:
                cls._instance.parent_dir = parent_dir
            else:
                # 获取项目根目录（lib目录的父目录）
                cls._instance.parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            cls._instance.lang_data = None
            cls._instance.current_lang_file = None
            cls._instance.ocr_language_mapping = None
            cls._instance._bootstrap()
        return cls._instance

    @staticmethod
    def get_instance():
        """获取LocalizationManager实例"""
        if LocalizationManager._instance is None:
            LocalizationManager()
        return LocalizationManager._instance

    def _bootstrap(self):
        """引导函数，检查并下载必要文件，加载语言数据"""
        # 首先加载语言文件
        self._load_language_file()
        # 加载OCR语言映射
        self._load_ocr_language_mapping()
        # 然后检查并下载其他必要文件
        self._check_and_download_files()

    def get_lang_data(self):
        """获取语言数据"""
        return self.lang_data

    def get_current_language_file(self):
        """获取当前语言文件名"""
        return self.current_lang_file

    def get_ocr_language(self):
        """获取当前语言对应的OCR语言类型"""
        if not self.ocr_language_mapping:
            self._load_ocr_language_mapping()

        # 默认OCR语言
        default_ocr_language = self.ocr_language_mapping.get('default_ocr_language', 'ENG')

        # 如果有当前语言文件，则根据语言映射获取OCR语言
        if self.current_lang_file:
            language_mapping = self.ocr_language_mapping.get('language_mapping', {})
            return language_mapping.get(self.current_lang_file, default_ocr_language)

        return default_ocr_language

    def _load_ocr_language_mapping(self):
        """加载OCR语言映射配置"""
        config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ocr_language_mapping.json')
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                self.ocr_language_mapping = json.load(f)
        except Exception as e:
            print(self.lang_data['ocr_mapping_load_fail'].format(str(e)))
            # 使用空字典作为默认值，确保程序可以继续运行
            self.ocr_language_mapping = {'language_mapping': {}, 'default_ocr_language': 'ENG'}
            # 记录错误日志，便于调试
            import logging
            logging.error(self.lang_data['ocr_mapping_load_fail'].format(str(e)))

    def _download_file_from_github(self, github_path, local_path):
        """从GitHub下载文件，支持重试机制"""
        url = f'{GITHUB_BASE_URL}{github_path}'
        print(self.lang_data['downloading_file'].format(url))

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

                print(self.lang_data['download_success'].format(local_path))
                return True
            except requests.exceptions.RequestException as e:
                error_msg = str(e)
                if attempt < max_retries - 1:
                    print(self.lang_data['download_fail'].format(url, error_msg))
                    print(self.lang_data['retry_attempt'].format(attempt+1))
                else:
                    print(self.lang_data['download_fail'].format(url, error_msg))
                    print(self.lang_data['max_retries_reached'].format(max_retries))
        return False

    def _load_language_file(self):
        """检查并加载语言文件"""
        # 初始使用默认语言数据
        self.lang_data = DEFAULT_LANG_DATA

        # 从lib/lang目录加载语言文件 (强制使用lib目录)
        lib_dir = os.path.dirname(os.path.abspath(__file__))
        lang_dir = os.path.join(lib_dir, 'lang')
        
        # 确保lib/lang目录存在
        if not os.path.exists(lang_dir):
            print(f"Directory not found: {lang_dir}")
            os.makedirs(lang_dir, exist_ok=True)
            print(f"Directory created: {lang_dir}")

        # 检查lib/lang目录中的语言文件
        if not [f for f in os.listdir(lang_dir) if f.lower().endswith('.json')]:
            raise FileNotFoundError(f"No language files found in {lang_dir}")

        # 检查lang目录中的语言文件
        lang_files = [f for f in os.listdir(lang_dir) if f.lower().endswith('.json')]

        # 如果有语言文件
        if lang_files:
            # 如果只有一个语言文件，直接加载
            if len(lang_files) == 1:
                self.current_lang_file = lang_files[0]
                lang_file = os.path.join(lang_dir, self.current_lang_file)
                try:
                    with open(lang_file, 'r', encoding='utf-8') as f:
                            loaded_data = json.load(f)
                            # 合并加载的数据到现有语言数据
                            self.lang_data = {**self.lang_data, **loaded_data}
                            self.lang_data['current_language'] = self.current_lang_file
                except Exception as e:
                    print(self.lang_data['load_lang_file_fail'].format(self.lang_data['main_lang_file_type'], self.current_lang_file, str(e)))
                    # 继续使用默认数据
            # 多个语言文件，按照优先级顺序加载
            else:
                for file_name, display_name in LANGUAGE_PRIORITY:
                    if file_name in lang_files:
                        self.current_lang_file = file_name
                        lang_file = os.path.join(lang_dir, self.current_lang_file)
                        try:
                            with open(lang_file, 'r', encoding='utf-8') as f:
                                loaded_data = json.load(f)
                                # 合并加载的数据到现有语言数据
                                self.lang_data = {**self.lang_data, **loaded_data}
                                self.lang_data['current_language'] = self.current_lang_file
                                break
                        except Exception as e:
                            print(self.lang_data['load_lang_file_fail'].format(self.lang_data['main_lang_file_type'], file_name, str(e)))
                            # 继续尝试下一个语言文件
        else:
            # 如果没有找到语言文件，下载默认语言文件
            print(self.lang_data['lang_files_not_found'])
            self.current_lang_file = LANGUAGE_PRIORITY[0][0]
            file_path = os.path.join(lang_dir, self.current_lang_file)
            self._download_file_from_github(f'lang/{self.current_lang_file}', file_path)

            # 尝试加载下载的默认语言文件
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    loaded_data = json.load(f)
                    # 合并加载的数据到现有语言数据
                    self.lang_data = {**self.lang_data, **loaded_data}
                    self.lang_data['current_language'] = self.current_lang_file
            except Exception as e:
                print(self.lang_data['load_default_lang_fail'].format(str(e)))
                sys.exit(1)

    def _check_directory_structure(self, base_path, dir_config, github_prefix=''):
        """递归检查目录结构并下载缺失文件"""
        # 检查当前目录是否存在
        if not os.path.exists(base_path):
            print(self.lang_data['dir_not_found'].format(base_path))
            os.makedirs(base_path, exist_ok=True)
            print(self.lang_data['dir_created'].format(base_path))

        # 检查当前目录中的文件
        if 'files' in dir_config:
            print(self.lang_data['dir_checking'].format(base_path))
            for file_name in dir_config['files']:
                file_path = os.path.join(base_path, file_name)
                # 检查文件是否存在
                if os.path.exists(file_path):
                    print(self.lang_data['file_found'].format(file_path))
                else:
                    print(self.lang_data['file_not_found'].format(file_path))
                    # 构建GitHub路径
                    github_path = f'{github_prefix}/{file_name}' if github_prefix else file_name
                    # 从GitHub下载文件
                    if not self._download_file_from_github(github_path, file_path):
                        self.critical_files_downloaded = False
                        print(self.lang_data['critical_file_download_fail'].format(github_path))

        # 递归检查子目录
        if 'subdirectories' in dir_config:
            for subdir_name, subdir_config in dir_config['subdirectories'].items():
                subdir_path = os.path.join(base_path, subdir_name)
                # 构建子目录的GitHub前缀
                new_github_prefix = f'{github_prefix}/{subdir_name}' if github_prefix else subdir_name
                self._check_directory_structure(subdir_path, subdir_config, new_github_prefix)

    def _check_and_download_files(self):
        """检查必要的目录和文件是否存在，如果不存在则从GitHub下载"""
        self.critical_files_downloaded = True
        # 从根目录结构开始检查
        for dir_name, dir_config in DIRECTORY_STRUCTURE.items():
            dir_path = os.path.join(self.parent_dir, dir_name)
            self._check_directory_structure(dir_path, dir_config, dir_name)

        # 如果关键文件下载失败，终止程序
        if not self.critical_files_downloaded:
            print(self.lang_data['exit_due_to_download_fail'])
            sys.exit(1)

    def get_lang_data(self):
        """获取语言数据"""
        return self.lang_data

    def load_module_language_file(self, module_path):
        """加载子模块文件夹里lang文件夹内的子语言文件"""
        # 构建子模块的lang目录路径
        module_lang_dir = os.path.join(module_path, 'lang')

        # 检查子模块lang目录是否存在
        if not os.path.exists(module_lang_dir):
            return

        # 获取子模块lang目录中的所有语言文件
        module_lang_files = [f for f in os.listdir(module_lang_dir) if f.lower().endswith('.json')]

        if not module_lang_files:
            return

        # 优先加载与当前语言文件同名的子语言文件
        if self.current_lang_file in module_lang_files:
            lang_file_path = os.path.join(module_lang_dir, self.current_lang_file)
            try:
                with open(lang_file_path, 'r', encoding='utf-8') as f:
                    module_lang_data = json.load(f)
                    # 合并语言数据，子模块的语言数据优先级高于基础语言数据
                    self.lang_data = {**self.lang_data, **module_lang_data}
                    self.lang_data['loaded_module_lang'] = self.current_lang_file
            except Exception as e:
                print(self.lang_data['load_lang_file_fail'].format(self.lang_data['module_lang_file_type'], self.current_lang_file, str(e)))
                # 继续尝试其他语言文件
        else:
            # 如果没有同名的语言文件，则按照LANGUAGE_PRIORITY的顺序加载
            for file_name, _ in LANGUAGE_PRIORITY:
                if file_name in module_lang_files:
                    lang_file_path = os.path.join(module_lang_dir, file_name)
                    try:
                        with open(lang_file_path, 'r', encoding='utf-8') as f:
                            module_lang_data = json.load(f)
                            # 合并语言数据
                            self.lang_data = {**self.lang_data, **module_lang_data}
                            self.lang_data['loaded_module_lang'] = file_name
                            break
                    except Exception as e:
                        print(self.lang_data['load_lang_file_fail'].format(self.lang_data['module_lang_file_type'], file_name, str(e)))
                        # 继续尝试下一个语言文件

# 引导函数，供外部调用
def bootstrap(parent_dir):
    """引导函数，初始化本地化管理器并返回语言数据"""
    loc_manager = LocalizationManager(parent_dir)
    return loc_manager