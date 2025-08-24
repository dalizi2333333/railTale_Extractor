# 基本配置定义
import os
import sys
from lang_manager import LangManager

# 尝试导入路径
library_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if library_dir not in sys.path:
    sys.path.append(library_dir)

class DefaultConfig:
    """默认配置类，提供应用程序的基础配置定义和管理方法"""
    # 主应用配置定义（使用本地化键）
    APP_CONFIG_DEFINITIONS = {
        'OUTPUT_OCR_DEBUG': {
            'type': 'boolean',
            'options': ['True', 'False'],
            'default': 'False',
            'description_key': 'config_output_ocr_debug',
            'required': False
        },
        'START_MARKERS': {
            'type': 'string',
            'subtype': 'non_empty',
            'default': '剧情梗概',
            'description_key': 'config_start_markers',
            'required': True
        },
        'STOP_MARKERS': {
            'type': 'string',
            'subtype': 'non_empty',
            'default': 'i,存在分支剧情选项,取消,×,⑧取消',
            'description_key': 'config_stop_markers',
            'required': True
        },
        'OCR_MODULE': {
            'type': 'string',
            'subtype': 'option',
            'options': ['baidu','test_module'],
            'default': 'baidu',
            'description_key': 'config_ocr_module',
            'required': True
        },
        'MAX_VERTICAL_IMAGES': {
            'type': 'integer',
            'min_value': 1,
            'max_value': 10,
            'default': '4',
            'description_key': 'config_max_vertical_images',
            'required': False
        },
        'OCR_LANGUAGE': {
            'type': 'string',
            'options': ['zh-cn', 'zh-tw', 'en', 'ja-jp','default'],
            'default': 'default',
            'description_key': 'config_ocr_language',
            'required': False
        }
    }

    # 模块配置注册表
    MODULE_CONFIG_REGISTRY = {}

    @classmethod
    def get_config_definitions(cls, module=None):
        """
        获取配置定义

        Args:
            module (str, optional): 模块名称. 如果为None则返回主配置，否则返回指定模块的配置

        Returns:
            dict: 配置定义字典
        """
        if module is not None and module in cls.MODULE_CONFIG_REGISTRY:
            return cls.MODULE_CONFIG_REGISTRY[module]
        return cls.APP_CONFIG_DEFINITIONS

    @classmethod
    def register_module_config(cls, module_name, config_definitions):
        """
        注册模块配置

        Args:
            module_name (str): 模块名称
            config_definitions (dict): 模块配置定义
        """
        if module_name and config_definitions:
            cls.MODULE_CONFIG_REGISTRY[module_name] = config_definitions
            print(f"Registered config for module: {module_name}")

    @classmethod
    def get_localized_config_definitions(cls, module=None):
        """
        获取带有本地化描述的配置定义

        Args:
            module (str, optional): 模块名称

        Returns:
            dict: 带有本地化描述的配置定义字典
        """
        config_definitions = cls.get_config_definitions(module)

        if module:
            lang_data = LangManager.get_module_lang_data()
        else:
            lang_data = LangManager.get_lang_data()

        # 替换description_key为本地化描述
        localized_definitions = {}
        for key, prop in config_definitions.items():
            localized_prop = prop.copy()
            if 'description_key' in prop:
                localized_prop['description'] = lang_data.get(prop['description_key'], prop['description_key'])
            localized_definitions[key] = localized_prop

        return localized_definitions


# 创建默认配置实例
default_config = DefaultConfig()

# 合并所有配置定义（保持向后兼容性）
CONFIG_DEFINITIONS = default_config.get_config_definitions()