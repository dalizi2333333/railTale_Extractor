import os
import sys

# 尝试导入bootstrap模块
library_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if library_dir not in sys.path:
    sys.path.append(library_dir)

try:
    from bootstrap import LocalizationManager
    # 创建LocalizationManager实例
    loc_manager = LocalizationManager()
    lang_data = loc_manager.get_lang_data()
    print(lang_data.get("import_bootstrap_success"))
except ImportError as e:
    # 尝试使用默认错误消息
    print(f"导入bootstrap模块失败: {str(e)}")
    print(f"当前目录: {os.getcwd()}")
    print(f"Python路径: {sys.path}")
    print("程序将退出...")
    sys.exit(1)

from .base_config import CONFIG_DEFINITIONS, MODULE_CONFIG_REGISTRY
from .config_generator import ConfigGenerator

class ConfigLoader:
    """配置加载器类，负责加载应用程序配置文件"""
    def __init__(self, loc_manager=None, process_dir=None):
        self._loc_manager = loc_manager or LocalizationManager.get_instance()
        self._lang_data = self._loc_manager.get_lang_data()
        
        if process_dir:
            # 使用传入的目录
            self._config_path = os.path.join(process_dir, 'config.txt')
        else:
            # 直接使用example目录下的process_images.py
            root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            example_dir = os.path.join(root_dir, 'example')
            process_images_path = os.path.join(example_dir, 'process_images.py')
            
            if os.path.exists(process_images_path):
                # 如果找到process_images.py，在其旁边生成config.txt
                self._config_path = os.path.join(os.path.dirname(process_images_path), 'config.txt')
            else:
                # 如果找不到，默认使用example目录
                self._config_path = os.path.join(example_dir, 'config.txt')
                print(self._lang_data.get("warning_no_process_images_load").format(self._config_path))

        # 使用配置定义中的默认值
        self._default_config = {}
        for key, prop in CONFIG_DEFINITIONS.items():
            self._default_config[key.lower()] = prop['default']
        # 模块配置缓存
        self._module_configs = {}
        self._config = None
        self._config_generator = ConfigGenerator(self._loc_manager)
    
    def _find_process_images(self, start_dir):
        """递归查找process_images.py文件"""
        for root, dirs, files in os.walk(start_dir):
            if 'process_images.py' in files:
                return os.path.join(root, 'process_images.py')
        return None

    def load_config(self):
        """加载配置文件

        Returns:
            dict: 加载的配置字典

        Raises:
            Exception: 配置读取或生成失败时抛出异常
        """
        if self._config is not None:
            return self._config

        # 检查配置文件是否存在
        if not os.path.exists(self._config_path):
            print(self._lang_data['config_not_found'])
            self._config_generator.generate_config()

        # 读取配置文件
        try:
            self._config = {**self._default_config}  # 从默认配置开始
            with open(self._config_path, 'r', encoding='utf-8') as f:
                for line in f:
                    # 跳过注释和空行
                    if line.strip().startswith('#') or not line.strip():
                        continue
                    # 解析配置项
                    if '=' in line:
                        key, value = line.split('=', 1)
                        key = key.strip().lower()  # 转换为小写以支持大小写不敏感
                        value = value.strip().strip("'").strip('"')

                        # 验证配置项
                        if key.upper() in CONFIG_DEFINITIONS:
                            prop = CONFIG_DEFINITIONS[key.upper()]
                            # 类型验证
                            if prop['type'] == 'integer' and not value.isdigit():
                                print(self._lang_data['config_validation_error'].format(
                                    key.upper(), f"必须是整数，当前值: {value}"
                                ))
                                continue
                            # 选项验证
                            if 'options' in prop and value not in prop['options']:
                                print(self._lang_data['config_validation_error'].format(
                                    key.upper(), f"必须是以下选项之一: {', '.join(prop['options'])}, 当前值: {value}"
                                ))
                                continue
                            # 范围验证
                            if prop['type'] == 'integer':
                                value_int = int(value)
                                if 'min_value' in prop and value_int < prop['min_value']:
                                    print(self._lang_data['config_validation_error'].format(
                                        key.upper(), f"必须大于或等于 {prop['min_value']}, 当前值: {value}"
                                    ))
                                    continue
                                if 'max_value' in prop and value_int > prop['max_value']:
                                    print(self._lang_data['config_validation_error'].format(
                                        key.upper(), f"必须小于或等于 {prop['max_value']}, 当前值: {value}"
                                    ))
                                    continue

                        self._config[key] = value

            # 检查必需的配置项
            for key, prop in CONFIG_DEFINITIONS.items():
                if prop.get('required', False) and key.lower() not in self._config:
                    print(self._lang_data['missing_required_config'].format(key))
                    self._config[key.lower()] = prop['default']
                    print(self._lang_data['using_default_value'].format(key, prop['default']))

            print(self._lang_data['config_load_success'].format(self._config_path))
            return self._config
        except Exception as e:
            error_msg = self._lang_data['config_read_error'].format(str(e))
            print(error_msg)
            raise Exception(error_msg)

    def load_module_config(self, module_name):
        """加载模块配置

        Args:
            module_name (str): 模块名称

        Returns:
            dict: 模块配置字典
        """
        if module_name in self._module_configs:
            return self._module_configs[module_name]

        if module_name not in MODULE_CONFIG_REGISTRY:
            print(self._lang_data.get("module_not_registered").format(module_name))
            self._module_configs[module_name] = {}
            return {}

        module_info = MODULE_CONFIG_REGISTRY[module_name]
        config_definitions = module_info['definitions']
        config_path = module_info['path']

        # 如果未指定路径或路径不存在，生成配置文件
        if config_path is None or not os.path.exists(config_path):
            self._config_generator.generate_module_config(module_name)
            config_path = MODULE_CONFIG_REGISTRY[module_name]['path']

        # 读取配置文件
        module_config = {}
        try:
            # 使用默认值初始化
            for key, prop in config_definitions.items():
                module_config[key.lower()] = prop['default']

            with open(config_path, 'r', encoding='utf-8') as f:
                for line in f:
                    # 跳过注释和空行
                    if line.strip().startswith('#') or not line.strip():
                        continue
                    # 解析配置项
                    if '=' in line:
                        key, value = line.split('=', 1)
                        key = key.strip().lower()  # 转换为小写以支持大小写不敏感
                        value = value.strip().strip("'").strip('"')

                        # 验证配置项
                        if key.upper() in config_definitions:
                            prop = config_definitions[key.upper()]
                            # 类型验证
                            if prop['type'] == 'integer' and not value.isdigit():
                                print(self._lang_data.get("config_validation_error_int").format(key.upper(), value))
                                continue
                            # 选项验证
                            if 'options' in prop and value not in prop['options']:
                                print(self._lang_data.get("config_validation_error_options").format(key.upper(), ', '.join(prop['options']), value))
                                continue
                            # 范围验证
                            if prop['type'] == 'integer':
                                value_int = int(value)
                                if 'min_value' in prop and value_int < prop['min_value']:
                                    print(self._lang_data.get("config_validation_error_min").format(key.upper(), prop['min_value'], value))
                                    continue
                                if 'max_value' in prop and value_int > prop['max_value']:
                                    print(self._lang_data.get("config_validation_error_max").format(key.upper(), prop['max_value'], value))
                                    continue

                        module_config[key] = value

            # 检查必需的配置项
            for key, prop in config_definitions.items():
                if prop.get('required', False) and key.lower() not in module_config:
                    print(self._lang_data.get("missing_required_config_item").format(key))
                    module_config[key.lower()] = prop['default']
                    print(self._lang_data.get("using_default_value_item").format(key, prop['default']))

            print(self._lang_data.get("module_config_loaded").format(module_name, config_path))
            self._module_configs[module_name] = module_config
            return module_config
        except Exception as e:
            error_msg = self._lang_data.get("module_config_read_fail").format(module_name, str(e))
            print(error_msg)
            self._module_configs[module_name] = {}
            return {}

    def get_config(self):
        """获取配置

        Returns:
            dict: 配置字典

        Raises:
            Exception: 配置读取或生成失败时抛出异常
        """
        if self._config is None:
            self.load_config()
        return self._config

    def get_module_config(self, module_name):
        """获取模块配置

        Args:
            module_name (str): 模块名称

        Returns:
            dict: 模块配置字典
        """
        if module_name not in self._module_configs:
            self.load_module_config(module_name)
        return self._module_configs.get(module_name, {})