import os
import importlib
import sys
import requests
from config.config_manager import ConfigManager
from lang_manager import LangManager
from config.default_config import DefaultConfig
from config.config_ensure import ensure_config
from config.config_loader import ConfigLoader
from ocr_core.ocr_module import OCRModule
from ocr_core.ocr_module_interface import OCRModuleInterface

class OCRModuleBootstraper:
    """模块引导器，负责OCR模块的自动补全和配置管理"""
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(OCRModuleBootstraper, cls).__new__(cls)
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
            module_name = ConfigManager.get('OCR_MODULE', 'baidu')

        # 获取模块目录
        module_dir, is_newly_created = ConfigManager.get_ocr_module_dir(module_name)

        # 检查模块目录下是否有module_bootstrap.py
        bootstrap_path = os.path.join(module_dir, 'module_bootstrap.py')
        # 如果目录是新创建的，或者module_bootstrap.py不存在，则尝试下载
        if is_newly_created or not os.path.exists(bootstrap_path):
            # 尝试下载module_bootstrap.py
            if not self._download_bootstrap(module_name, bootstrap_path):
                print(LangManager.get_lang_data()['module_bootstrap_missing'].format(module_name))
                return False

        # 加载module_bootstrap.py
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
                'complete_module',
                'get_module_class'
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
                from dependency_check import check_dependencies
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
                # 补全成功，后续会统一注册模块
                # 此时模块语言文件应该已经加载
                # 获取模块需要的配置项
                config_items = module_bootstrap.get_required_config_items()
                """
                返回模块需要的配置项
                这些配置项将被添加到配置文件中
                
                Returns:
                    dict: 包含配置项名称、类型、默认值和描述的字典
                """
                # 注册模块配置
                DefaultConfig.register_module_config(module_name, config_items)
                # 确保配置文件存在并加载配置
                if ensure_config(module_name):
                    ConfigLoader().load_config(module_name)# 一个类方法问题硬控我半天
                # 检查是否有强制配置
                elif module_bootstrap.has_mandatory_config():
                    """
                    返回模块是否有不可为默认值的配置项
                    如果返回True，当根据complete_module方法补全模块后，程序会退出并提醒用户修改配置
                    
                    Returns:
                        bool: 是否有不可为默认值的配置项
                    """
                    print(LangManager.get_lang_data()['module_mandatory_config'].format(module_name))
                    # 有强制配置但配置文件不存在，返回False以在应用层面中断程序
                    return False
                # 注册模块
                module_class = module_bootstrap.get_module_class()
                """
                返回模块的主类
                这个方法会被ModuleBootstraper调用，用于注册模块
                
                Returns:
                    class: 模块的主类
                """
                OCRModule.register_module(module_name, module_class)
                return True
            else:
                print(LangManager.get_lang_data()['module_self_completion_fail'].format(module_name))
                return False

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
            bootstrap_url = f"{download_url}lib/ocr_modules/{module_name}/module_bootstrap.py"

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
module_bootstraper = OCRModuleBootstraper()
