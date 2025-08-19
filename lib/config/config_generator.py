import os
import sys
import datetime

# 尝试导入bootstrap模块
library_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if library_dir not in sys.path:
    sys.path.append(library_dir)

try:
    from bootstrap import LocalizationManager
    # 创建LocalizationManager实例
    loc_manager = LocalizationManager()
    lang_data = loc_manager.get_lang_data()
    print(lang_data.get("import_bootstrap_success", "导入bootstrap模块成功"))
except ImportError as e:
    # 尝试使用默认错误消息
    print(f"导入bootstrap模块失败: {str(e)}")
    print(f"当前目录: {os.getcwd()}")
    print(f"Python路径: {sys.path}")
    print("程序将退出...")
    sys.exit(1)

from .base_config import CONFIG_DEFINITIONS, MODULE_CONFIG_REGISTRY

class ConfigGenerator:
    """配置生成器类，负责生成应用程序配置文件"""
    def __init__(self, loc_manager=None, process_dir=None):
        self._loc_manager = loc_manager or LocalizationManager.get_instance()
        self._lang_data = self._loc_manager.get_lang_data()
        
        if process_dir:
            # 使用传入的目录
            self._config_path = os.path.join(process_dir, 'config.txt')
        else:
            # 直接使用当前工作目录
            current_dir = os.getcwd()
            self._config_path = os.path.join(current_dir, 'config.txt')
    
    def _find_process_images(self, start_dir):
        """递归查找process_images.py文件"""
        for root, dirs, files in os.walk(start_dir):
            if 'process_images.py' in files:
                return os.path.join(root, 'process_images.py')
        return None

    def generate_config(self):
        """自动生成配置文件

        Raises:
            Exception: 生成配置文件失败时抛出异常
        """
        try:
            # 确保目录存在
            os.makedirs(os.path.dirname(self._config_path), exist_ok=True)

            with open(self._config_path, 'w', encoding='utf-8') as f:
                f.write("# {}\n# {} {}\n\n".format(
                    self._lang_data.get("config_auto_generated"),
                    self._lang_data.get("config_last_generated_time"),
                    datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                ))

                # 遍历配置定义，生成配置项
                for key, prop in CONFIG_DEFINITIONS.items():
                    # 写入注释
                    f.write(f"# {prop['description']}\n")
                    if 'options' in prop:
                        f.write(f"# {self._lang_data.get('config_option_values').format(', '.join(prop['options']))}\n")
                    if 'min_value' in prop and 'max_value' in prop:
                        f.write(f"# {self._lang_data.get('config_value_range').format(prop['min_value'], prop['max_value'])}\n")
                    # 写入配置项
                    f.write(f"{key} = '{prop['default']}'\n\n")

            print(self._lang_data['config_generate_success'].format(self._config_path))

            # 生成模块配置文件
            for module_name in MODULE_CONFIG_REGISTRY:
                self.generate_module_config(module_name)

        except Exception as e:
            error_msg = self._lang_data['config_generate_fail'].format(str(e))
            print(error_msg)
            raise Exception(error_msg)

    def generate_module_config(self, module_name):
        """生成模块配置文件

        Args:
            module_name (str): 模块名称

        Raises:
            Exception: 生成模块配置文件失败时抛出异常
        """
        if module_name not in MODULE_CONFIG_REGISTRY:
            print(self._lang_data.get("module_not_registered").format(module_name))
            return

        module_info = MODULE_CONFIG_REGISTRY[module_name]
        config_definitions = module_info['definitions']
        config_path = module_info['path']

        # 如果未指定路径，使用默认路径
        if config_path is None:
                # 使用当前工作目录
                config_path = os.path.join(os.getcwd(), f'{module_name}_config.txt')

        try:
            # 确保目录存在
            os.makedirs(os.path.dirname(config_path), exist_ok=True)

            with open(config_path, 'w', encoding='utf-8') as f:
                f.write(f"# {self._lang_data.get('config_auto_generated_comment', '').format(module_name)}\n# {self._lang_data.get('config_last_generated_time', '最后生成时间:')} {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

                # 遍历模块配置定义，生成配置项
                for key, prop in config_definitions.items():
                    # 写入注释
                    f.write(f"# {prop['description']}\n")
                    if 'options' in prop:
                        f.write(f"# 可选值: {', '.join(prop['options'])}\n")
                    if 'min_value' in prop and 'max_value' in prop:
                        f.write(f"# 取值范围: {prop['min_value']}-{prop['max_value']}\n")
                    # 写入配置项
                    f.write(f"{key} = '{prop['default']}'\n\n")

            print(self._lang_data.get('config_module_file_generated', '').format(module_name, config_path))
            # 更新注册表中的路径
            MODULE_CONFIG_REGISTRY[module_name]['path'] = config_path
        except Exception as e:
            error_msg = self._lang_data.get("module_config_generate_fail").format(module_name, str(e))
            print(error_msg)
            raise Exception(error_msg)