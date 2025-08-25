import os
import sys
import json
import logging

# 语言优先级顺序
LANGUAGE_PRIORITY = [
    ('zh-cn.json', '简体中文'),
    ('en.json', 'English'),
    ('zh-tw.json', '繁体中文'),
    ('ja-jp.json', '日本語')
]

class LangManager:
    """语言管理器，负责语言文件加载和语言数据管理"""
    # 单例实例和初始化标记
    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(LangManager, cls).__new__(cls)
            cls._instance._lang_data = {}
            cls._instance._module_lang_data = {}
            cls._instance._current_lang_file = None
        return cls._instance

    @classmethod
    def get_instance(cls):
        """获取语言管理器单例实例

        Returns:
            LangManager: 语言管理器实例
        """
        return cls()

    @classmethod
    def initialize(cls, lang_data):
        """初始化语言管理器，设置语言数据

        Args:
            lang_data (dict): 语言数据字典，包含current_language等信息
        """
        instance = cls.get_instance()
        if not cls._initialized:
            # 直接使用提供的语言数据
            instance._lang_data = lang_data
            instance._current_lang_file = lang_data.get('current_language')

            cls._initialized = True
        return instance

    @classmethod
    def get_lang_data(cls):
        """获取基础语言数据

        Returns:
            dict: 基础语言数据
        """
        return cls()._lang_data

    @classmethod
    def get_module_lang_data(cls):
        """
        获取模块语言数据

        Returns:
            dict: 模块语言数据
        """
        return cls()._module_lang_data

    @classmethod
    def get_lang(cls, key):
        """
        获取基础语言文本，如果键不存在则返回键本身

        Args:
            key (str): 语言键

        Returns:
            str: 语言文本或键本身
        """
        return cls()._lang_data.get(key, key)

    @classmethod
    def get_module_lang(cls, key):
        """
        获取模块语言文本，如果键不存在则返回键本身

        Args:
            key (str): 模块语言键

        Returns:
            str: 模块语言文本或键本身
        """
        return cls()._module_lang_data.get(key, key)

    @classmethod
    def get_current_language_file(cls):
        """获取当前语言文件名

        Returns:
            str: 当前语言文件名
        """
        return cls()._current_lang_file

    @classmethod
    def load_module_language_file(cls, module_path):
        """加载子模块文件夹里lang文件夹内的子语言文件到模块语言数据表中

        Args:
            module_path (str): 模块路径

        Returns:
            bool: 是否成功加载
        """
        instance = cls.get_instance()
        # 构建子模块的lang目录路径
        module_lang_dir = os.path.join(module_path, 'lang')

        # 检查子模块lang目录是否存在
        if not os.path.exists(module_lang_dir):
            return False

        # 获取子模块lang目录中的所有语言文件
        module_lang_files = [f for f in os.listdir(module_lang_dir) if f.lower().endswith('.json')]

        if not module_lang_files:
            return False

        # 优先加载与当前语言文件同名的子语言文件
        if instance._current_lang_file in module_lang_files:
            lang_file_path = os.path.join(module_lang_dir, instance._current_lang_file)
            try:
                with open(lang_file_path, 'r', encoding='utf-8') as f:
                    module_lang_data = json.load(f)
                    # 将模块语言数据存储到单独的表中
                    instance._module_lang_data = module_lang_data
                    return True
            except Exception as e:
                logging.error(instance._lang_data["load_lang_file_fail"].format(instance._lang_data["module_lang_file_type"], instance._current_lang_file, str(e)))

                # 继续尝试其他语言文件
        else:
            # 如果没有同名的语言文件，则按照LANGUAGE_PRIORITY的顺序加载
            for file_name, _ in LANGUAGE_PRIORITY:
                if file_name in module_lang_files:
                    lang_file_path = os.path.join(module_lang_dir, file_name)
                    try:
                        with open(lang_file_path, 'r', encoding='utf-8') as f:
                            module_lang_data = json.load(f)
                            # 将模块语言数据存储到单独的表中
                            instance._module_lang_data = module_lang_data
                            return True
                    except Exception as e:
                        logging.error(instance._lang_data["load_lang_file_fail"].format(instance._lang_data["module_lang_file_type"], file_name, str(e)))
                        # 继续尝试下一个语言文件
        return False