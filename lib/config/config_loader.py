import os
import sys

# 尝试导入bootstrap模块
library_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if library_dir not in sys.path:
    sys.path.append(library_dir)

# 导入必要的模块
from lib.lang_manager import LangManager
from .config_manager import ConfigManager

# 配置管理器通过静态方法使用，无需创建实例

from .default_config import DefaultConfig
from .config_generator import ConfigGenerator

class ConfigLoader:
    """配置加载器类，负责加载应用程序配置文件到全局config_manager"""
    def __init__(self, loc_manager=None):
        self._loc_manager = loc_manager or LangManager.get_instance()
        self._lang_data = self._loc_manager.get_lang_data()
        
        self._config_generator = ConfigGenerator(self._loc_manager)
    
    def load_config(self, module=None):
        """加载配置文件到全局config_manager

        Args:
            module (str, optional): 模块名称，如果为None则加载主配置

        Returns:
            dict: 加载的配置字典

        Raises:
            Exception: 配置读取失败时抛出异常
        """
        # 确保配置管理器已初始化
        ConfigManager.initialize()

        # 确定是加载主配置还是模块配置
        # 使用DefaultConfig获取配置定义
        config_definitions = DefaultConfig.get_config_definitions(module)
        if not config_definitions:
            print(LangManager.get_lang_data()["module_config_not_found"].format(module))
            return {}

        if module is None:
            # 主配置
            process_dir = ConfigManager.get_process_dir()
            config_path = os.path.join(process_dir, 'config.txt')
        else:
            # 模块配置
            # 获取模块目录并构建配置文件路径
            module_dir, is_newly_created = ConfigManager.get_ocr_module_dir(module)
            config_path = os.path.join(module_dir, f'{module}_config.txt')

            # 如果配置文件不存在，生成配置文件
            if not os.path.exists(config_path):
                self._config_generator.generate_config(module)

            # 再次检查配置文件是否存在
            if not os.path.exists(config_path):
                print(LangManager.get_lang_data()["config_file_not_found"].format(config_path))
                return {}

        # 初始化配置状态变量
        config_valid = 2  # 0: 不可用, 1: 部分可用(使用了默认值), 2: 完全可用
        config = {}

        try:
            # 初始化配置字典，设置默认值
            for key, prop in config_definitions.items():
                config[key] = prop['default']
                ConfigManager.set(key, prop['default'])

            # 读取配置文件
            with open(config_path, 'r', encoding='utf-8') as f:
                for line in f:
                    # 跳过注释和空行
                    if line.strip().startswith('#') or not line.strip():
                        continue
                    # 解析配置项
                    if '=' in line:
                        key, value = line.split('=', 1)
                        key = key.strip().upper()  # 转换为大写键
                        value = value.strip().strip("'").strip('"')

                        # 验证配置项
                        if key in config_definitions:
                            prop = config_definitions[key]
                            is_valid = True
                            error_msg = ""

                            # 处理不可取默认值类型
                            if prop.get('cannot_use_default', False) and value == prop['default']:
                                config_valid = 0
                                print(LangManager.get_lang_data()['config_cannot_use_default'].format(key))
                                continue

                            # 类型和范围验证
                            if prop['type'] == 'integer':
                                if not value.isdigit():
                                    is_valid = False
                                    error_msg = LangManager.get_lang_data()['must_be_integer'].format(value)
                                else:
                                    value_int = int(value)
                                    if 'min_value' in prop and value_int < prop['min_value']:
                                        is_valid = False
                                        error_msg = LangManager.get_lang_data()['must_be_greater_or_equal'].format(prop['min_value'], value)
                                    elif 'max_value' in prop and value_int > prop['max_value']:
                                        is_valid = False
                                        error_msg = LangManager.get_lang_data()['must_be_less_or_equal'].format(prop['max_value'], value)
                            elif prop['type'] == 'float':
                                try:
                                    value_float = float(value)
                                    if 'min_value' in prop and value_float < prop['min_value']:
                                        is_valid = False
                                        error_msg = LangManager.get_lang_data()['must_be_greater_or_equal'].format(prop['min_value'], value)
                                    elif 'max_value' in prop and value_float > prop['max_value']:
                                        is_valid = False
                                        error_msg = LangManager.get_lang_data()['must_be_less_or_equal'].format(prop['max_value'], value)
                                except ValueError:
                                    is_valid = False
                                    error_msg = LangManager.get_lang_data()['must_be_float'].format(value)
                            elif prop['type'] == 'boolean':
                                if value.lower() not in ['true', 'false']:
                                    is_valid = False
                                    error_msg = LangManager.get_lang_data()['must_be_boolean'].format(value)
                            elif 'options' in prop and value not in prop['options']:
                                is_valid = False
                                error_msg = LangManager.get_lang_data()['must_be_one_of_options'].format(', '.join(prop['options']), value)
                            elif prop['type'] == 'string' and prop.get('non_empty', False) and not value:
                                is_valid = False
                                error_msg = LangManager.get_lang_data()['cannot_be_empty']

                            # 处理验证结果
                            if is_valid:
                                # 处理多值情况
                                if prop.get('allow_multiple', False) and ',' in value:
                                    config[key] = [v.strip() for v in value.split(',')]
                                    ConfigManager.set(key, config[key])
                                else:
                                    config[key] = value
                                    ConfigManager.set(key, value)
                            else:
                                # 使用默认值
                                config_valid = 1
                                print(LangManager.get_lang_data()['config_validation_error'].format(key, error_msg))
                                print(LangManager.get_lang_data()['using_default_value'].format(key, prop['default']))
                        else:
                            print(LangManager.get_lang_data()['unknown_config_key'].format(key))
        except Exception as e:
            error_msg = LangManager.get_lang_data()['config_read_error'].format(str(e))
            print(error_msg)
            raise Exception(error_msg)

        # 检查必需的配置项
        for key, prop in config_definitions.items():
            if prop.get('required', False) and key not in config:
                print(LangManager.get_lang_data()['missing_required_config'].format(key))
                config[key] = prop['default']
                ConfigManager.set(key, prop['default'])
                print(LangManager.get_lang_data()['using_default_value'].format(key, prop['default']))
                config_valid = 1

        # 检查配置是否完全不可用
        if config_valid == 0:
            error_msg = LangManager.get_lang_data()['config_cannot_use_default'].format('CONFIG_VALID')
            print(error_msg)
            raise Exception(error_msg)

        # 存储配置有效状态
        ConfigManager.set('CONFIG_VALID', config_valid)
        config['CONFIG_VALID'] = config_valid

        print(LangManager.get_lang_data()['config_load_success'].format(config_path))
        return config
