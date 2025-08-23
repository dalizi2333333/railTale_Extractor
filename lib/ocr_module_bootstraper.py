import os
import importlib
import sys
import requests
from lib.config.config_manager import ConfigManager
from lib.lang_manager import LangManager
from lib.config.default_config import DefaultConfig
from lib.config.config_ensure import ensure_config
from lib.config.config_loader import ConfigLoader

class ModuleBootstraper:
    """模块引导器，负责OCR模块的自动补全和配置管理"""
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ModuleBootstraper, cls).__new__(cls)
            cls._instance._lang_manager = LangManager.get_instance()
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
            module_name = ConfigManager.get_config('ocr_module', 'baidu')

        # 获取模块目录
        module_dir, is_newly_created = ConfigManager.get_ocr_module_dir(module_name)

        # 检查模块目录下是否有bootstrap.py
        bootstrap_path = os.path.join(module_dir, 'bootstrap.py')
        # 如果目录是新创建的，或者bootstrap.py不存在，则尝试下载
        if is_newly_created or not os.path.exists(bootstrap_path):
            # 尝试下载bootstrap.py
            if not self._download_bootstrap(module_name, bootstrap_path):
                print(LangManager.get_lang_data()['module_bootstrap_missing'].format(module_name))
                return False

        # 加载bootstrap.py
        try:
            # 将模块目录添加到Python路径
            if module_dir not in sys.path:
                sys.path.append(module_dir)

            # 导入bootstrap模块
            module_bootstrap = importlib.import_module('module_bootstrap')

            # 检查必要的方法是否存在
            required_methods = [
                'get_required_dependencies',
                'get_required_config_items',
                'has_mandatory_config',
                'complete_module'
            ]

            # 测试能否导入并使用模块内的module_bootstrap内的方法
            # module_bootstrap.test_module()
            for method_name in required_methods:
                if not hasattr(module_bootstrap, method_name):
                    print(LangManager.get_lang_data()['module_method_missing'].format(module_name, method_name))
                    return False

            # 调用方法
            required_deps = module_bootstrap.get_required_dependencies()
            """
            返回模块需要的额外依赖
            这些依赖不会被自动安装，需要用户手动安装或通过依赖管理工具安装

            Returns:
                dict: 包含依赖信息的字典，格式为 {import_name: {'install_name': install_name, 'version': version}}
            """

            # 检查依赖
            if required_deps:
                from lib.dependency_check import check_dependencies
                if not check_dependencies(required_deps):
                    return False

            # 补全模块
            if module_bootstrap.complete_module():
                """
                补全模块的方式
                负责初始化模块所需的语言文件和其他资源
                
                Returns:
                    bool: 是否补全成功
                """
                # 加载模块语言文件
                LangManager.load_module_language_file(module_dir)
                # 获取模块需要的配置项
                config_items = module_bootstrap.get_required_config_items()
                # 注册模块配置
                DefaultConfig.register_module_config(module_name, config_items)
                # 确保配置文件存在并加载配置
                if ensure_config(module_name):
                    ConfigLoader.load_config(module_name)
                # 检查是否有强制配置
                if module_bootstrap.has_mandatory_config():
                    print(LangManager.get_lang_data()['module_mandatory_config'].format(module_name))
                    return False
                else:
                    return True
            else:
                print(LangManager.get_lang_data()['module_bootstrap_fail'].format(module_name))
                return False

            return True

        except Exception as e:
            print(LangManager.get_lang_data()['module_bootstrap_error'].format(module_name, str(e)))
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
            download_url = ConfigManager.get_project_download_url()
            if not download_url:
                print(LangManager.get_lang_data()['download_url_not_set'])
                return False

            # 构建bootstrap.py的下载URL
            bootstrap_url = f"{download_url}/ocr_modules/{module_name}/bootstrap.py"

            # 下载文件
            response = requests.get(bootstrap_url)
            if response.status_code == 404:
                print(LangManager.get_lang_data()['bootstrap_not_found'].format(module_name, bootstrap_url))
                return False

            response.raise_for_status()

            # 保存文件
            with open(bootstrap_path, 'w', encoding='utf-8') as f:
                f.write(response.text)

            print(LangManager.get_lang_data()['bootstrap_downloaded'].format(module_name))
            return True

        except requests.RequestException as e:
            print(LangManager.get_lang_data()['bootstrap_download_failed'].format(module_name, str(e)))
            return False


# 创建全局实例
module_bootstraper = ModuleBootstraper()