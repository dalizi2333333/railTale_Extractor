import os
import importlib
import sys
import requests
from lib.config.config_manager import ConfigManager
from lib.lang_manager import LocalizationManager

class ModuleBootstraper:
    """模块引导器，负责OCR模块的自动补全和配置管理"""
    _instance = None
    _bootstrap_cache = {}  # 缓存模块引导结果

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ModuleBootstraper, cls).__new__(cls)
            cls._instance._loc_manager = LocalizationManager.get_instance()
            cls._instance._bootstrap_cache = {}  # 初始化缓存字典
        return cls._instance

    def bootstrap_module(self, module_name=None):
        """引导指定OCR模块

        Args:
            module_name (str, optional): OCR模块名称，默认为配置中的值

        Returns:
            bool: 是否引导成功
        """

        # 获取模块名称
        if module_name is None:
            module_name = ConfigManager.get('ocr_module', 'baidu')

        # 检查缓存
        if module_name in self._bootstrap_cache:
            return self._bootstrap_cache[module_name]

        # 获取模块目录
        module_dir, is_newly_created = ConfigManager.get_ocr_module_dir(module_name)

        # 检查模块目录下是否有bootstrap.py
        bootstrap_path = os.path.join(module_dir, 'bootstrap.py')
        # 如果目录是新创建的，或者bootstrap.py不存在，则尝试下载
        if is_newly_created or not os.path.exists(bootstrap_path):
            # 尝试下载bootstrap.py
            if not self._download_bootstrap(module_name, bootstrap_path):
                print(LocalizationManager.get_lang_data()['module_bootstrap_missing'].format(module_name))
                return False

        # 加载bootstrap.py
        try:
            # 将模块目录添加到Python路径
            if module_dir not in sys.path:
                sys.path.append(module_dir)

            # 导入bootstrap模块
            bootstrap_module = importlib.import_module('bootstrap')

            # 检查必要的方法是否存在
            required_methods = [
                'get_required_dependencies',
                'get_required_config_items',
                'has_mandatory_config',
                'complete_module'
            ]

            for method_name in required_methods:
                if not hasattr(bootstrap_module, method_name):
                    print(LocalizationManager.get_lang_data()['module_method_missing'].format(module_name, method_name))
                    return False

            # 调用方法
            required_deps = bootstrap_module.get_required_dependencies()

            # 注册依赖
            if required_deps:
                from lib.dependency_check import dependency_checker
                for dep in required_deps:
                    dependency_checker.register_dependency(dep)

            # 补全模块
            bootstrap_module.complete_module()

            # 缓存成功结果
            self._bootstrap_cache[module_name] = True
            return True

        except Exception as e:
            print(self._loc_manager.get_lang_data()['module_bootstrap_error'].format(module_name, str(e)))
            # 缓存失败结果
            self._bootstrap_cache[module_name] = False
            return False

    def _download_bootstrap(self, module_name, bootstrap_path):
        """从项目下载URL下载模块的bootstrap.py

        Args:
            module_name (str): 模块名称
            bootstrap_path (str): 保存路径

        Returns:
            bool: 是否下载成功
        """
        try:
            download_url = config_manager.get_project_download_url()
            if not download_url:
                print(self._loc_manager.get_lang_data()['download_url_not_set'])
                return False

            # 构建bootstrap.py的下载URL
            bootstrap_url = f"{download_url}/ocr_modules/{module_name}/bootstrap.py"

            # 下载文件
            response = requests.get(bootstrap_url)
            if response.status_code == 404:
                print(self._loc_manager.get_lang_data()['bootstrap_not_found'].format(module_name, bootstrap_url))
                return False

            response.raise_for_status()

            # 保存文件
            with open(bootstrap_path, 'w', encoding='utf-8') as f:
                f.write(response.text)

            print(self._loc_manager.get_lang_data()['bootstrap_downloaded'].format(module_name))
            return True

        except requests.RequestException as e:
            print(self._loc_manager.get_lang_data()['bootstrap_download_failed'].format(module_name, str(e)))
            return False

    def get_required_config_items(self, module_name=None):
        """获取模块需要的配置项

        Args:
            module_name (str, optional): 模块名称

        Returns:
            dict: 配置项字典
        """
        if module_name is None:
            module_name = config_manager.get_config('ocr_module', 'baidu')

        # 确保模块已引导
        if not self.bootstrap_module(module_name):
            return {}

        # 直接从模块目录导入bootstrap.py获取配置项
        module_dir, _ = config_manager.get_ocr_module_dir(module_name)
        if module_dir not in sys.path:
            sys.path.append(module_dir)

        try:
            bootstrap_module = importlib.import_module('bootstrap')
            if hasattr(bootstrap_module, 'get_required_config_items'):
                return bootstrap_module.get_required_config_items()
            return {}
        except ImportError:
            return {}

    def has_mandatory_config(self, module_name=None):
        """检查模块是否有不可为默认值的配置项

        Args:
            module_name (str, optional): 模块名称

        Returns:
            bool: 是否有不可为默认值的配置项
        """
        if module_name is None:
            module_name = config_manager.get_config('ocr_module', 'baidu')

        # 确保模块已引导
        if not self.bootstrap_module(module_name):
            return False

        # 直接从模块目录导入bootstrap.py检查
        module_dir, _ = config_manager.get_ocr_module_dir(module_name)
        if module_dir not in sys.path:
            sys.path.append(module_dir)

        try:
            bootstrap_module = importlib.import_module('bootstrap')
            if hasattr(bootstrap_module, 'has_mandatory_config'):
                return bootstrap_module.has_mandatory_config()
            return False
        except ImportError:
            return False

# 创建全局实例
module_bootstraper = ModuleBootstraper()