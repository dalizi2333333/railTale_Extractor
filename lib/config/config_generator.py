import os
import sys
import datetime

# 尝试导入bootstrap模块
library_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if library_dir not in sys.path:
    sys.path.append(library_dir)

try:
    from lib.lang_manager import LocalizationManager
    from .config_manager import ConfigManager
    from lib.ocr_module_bootstraper import module_bootstraper
    # 获取LocalizationManager单例实例
    loc_manager = LocalizationManager.get_instance()
    lang_data = loc_manager.get_lang_data()
    print(lang_data.get("language_system_loaded", "语言系统加载成功"))
except ImportError as e:
    # 尝试使用默认错误消息
    print(f"语言系统加载失败: {str(e)}")
    print(f"当前目录: {os.getcwd()}")
    print(f"Python路径: {sys.path}")
    print("程序将退出...")
    sys.exit(1)

from .base_config import CONFIG_DEFINITIONS

class ConfigGenerator:
    """配置生成器类，负责生成应用程序配置文件"""
    def __init__(self, loc_manager=None):
        self._loc_manager = loc_manager or LocalizationManager.get_instance()
        self._lang_data = self._loc_manager.get_lang_data()
        
        # 使用全局config_manager实例获取process_dir
        process_dir = ConfigManager.get_process_dir()
        self._config_path = os.path.join(process_dir, 'config.txt')

    def generate_config(self, module=None):
        """自动生成配置文件

        Args:
            module (str, optional): 模块名称. 如果为None则生成主配置，否则生成指定模块的配置

        Raises:
            Exception: 生成配置文件失败时抛出异常
        """
        process_dir = ConfigManager.get_process_dir()

        # 确定配置路径和配置定义
        if module is not None:
            # 使用模块引导器获取配置定义
            config_definitions = module_bootstraper.get_required_config_items(module)
            if not config_definitions:
                print(self._lang_data.get("module_config_not_found").format(module))
                raise ValueError(f"无法获取模块 '{module}' 的配置定义")
            # 使用get_ocr_module_dir获取模块路径
            module_dir, is_newly_created = config_manager.get_ocr_module_dir(module)
            config_path = os.path.join(module_dir, f'{module}_config.txt')
            config_type = f"{self._lang_data.get('config_module_file', '模块配置文件')} ({module})"
        else:
            config_definitions = CONFIG_DEFINITIONS
            config_path = os.path.join(process_dir, 'config.txt')
            config_type = self._lang_data.get('config_main_file', '主配置文件')

        try:
            # 确保目录存在
            os.makedirs(os.path.dirname(config_path), exist_ok=True)

            with open(config_path, 'w', encoding='utf-8') as f:
                f.write("# {}\n".format(
                    self._lang_data.get("config_auto_generated").format(config_type)
                ))
                f.write("# {} {}\n".format(
                    self._lang_data.get("config_auto_generated").format(config_type),
                    self._lang_data.get("config_last_generated_time"),
                    datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                ))

                # 遍历配置定义，生成配置项
                for key, prop in config_definitions.items():
                    # 直接使用默认值
                    value = prop['default']

                    # 写入注释
                    f.write(f"# {prop['description']}\n")
                    if 'subtype' in prop:
                        if prop['subtype'] == 'non_empty':
                            f.write(f"# {self._lang_data.get('config_not_empty')}\n")
                        elif prop['subtype'] == 'option':
                            f.write(f"# {self._lang_data.get('config_option_values').format(', '.join(prop['options']))}\n")
                    elif 'options' in prop:
                        f.write(f"# {self._lang_data.get('config_option_values').format(', '.join(prop['options']))}\n")
                    if 'min_value' in prop and 'max_value' in prop:
                        f.write(f"# {self._lang_data.get('config_value_range').format(prop['min_value'], prop['max_value'])}\n")
                    # 写入配置项
                    f.write(f"{key} = '{value}'\n\n")

            print(self._lang_data['config_generate_success'].format(config_path))

            # 按用户要求，不再自动生成所有模块配置
            # 模块配置需要单独加载

        except Exception as e:
            error_msg = self._lang_data['config_generate_fail'].format(str(e))
            print(error_msg)
            raise Exception(error_msg)