import os
import json

# 测试OCR模块的bootstrap
# 此文件由ModuleBootstraper加载和使用，负责模块的依赖管理、配置和初始化


def get_required_dependencies():
    """
    返回模块需要的额外依赖
    这些依赖不会被自动安装，需要用户手动安装或通过依赖管理工具安装

    Returns:
        dict: 包含依赖信息的字典，格式为 {import_name: {'install_name': install_name, 'version': version}}
    """
    return {}


def get_required_config_items():
    """
    返回模块需要的配置项
    这些配置项将被添加到配置文件中

    Returns:
        dict: 包含配置项名称、类型、默认值和描述的字典
    """
    return {
        'TEST_MODE': {
            'type': 'bool',
            'default': True,
            'description_key': 'test_mode_desc'
        }
    }


def has_mandatory_config():
    """
    返回模块是否有不可为默认值的配置项
    如果返回True，当根据complete_module方法补全模块后，程序会退出并提醒用户修改配置

    Returns:
        bool: 是否有不可为默认值的配置项
    """
    return False


def complete_module():
    """
    补全模块的方式
    负责初始化模块所需的语言文件和其他资源，包括从网络下载必要文件

    Returns:
        bool: 是否补全成功
    """
    import os
    import shutil
    import requests
    from config.config_manager import ConfigManager
    from lang_manager import LangManager

    try:
        # 获取当前模块路径
        module_path = os.path.dirname(os.path.abspath(__file__))
        print(f"正在补全测试模块，模块路径: {module_path}")

        # 硬编码完整的下载链接
        download_url = 'https://raw.githubusercontent.com/dalizi2333333/railTale_Extractor/main/lib/ocr_modules/test_module/ocr_test_module.py'

        # 下载ocr_test_module.py文件
        module_file_path = os.path.join(module_path, 'ocr_test_module.py')
        # 只有当文件不存在或大小为0时才下载
        if not os.path.exists(module_file_path) or os.path.getsize(module_file_path) == 0:
            print(f"正在下载ocr_test_module.py文件从: {download_url}")
            response = requests.get(download_url, timeout=10)
            if response.status_code != 200:
                print(f"下载ocr_test_module.py失败，状态码: {response.status_code}")
                raise Exception(f"无法下载测试模块文件: {download_url}")
            
            with open(module_file_path, 'wb') as f:
                f.write(response.content)
            print(f"成功下载ocr_test_module.py到: {module_file_path}")
        else:
            print(f"ocr_test_module.py文件已存在且不为空，跳过下载")

        # 确保lang目录存在
        lang_dir = os.path.join(module_path, 'lang')
        if not os.path.exists(lang_dir):
            os.makedirs(lang_dir, exist_ok=True)
            print(f'创建语言目录: {lang_dir}')

        # 生成语言文件
        # 测试模块只有test_mode_desc这一个键
        lang_data = {
            'test_mode_desc': '测试模式: 启用后将使用测试模块进行OCR识别，适用于开发和调试'
        }

        # 保存中文语言文件
        zh_cn_path = os.path.join(lang_dir, 'zh-cn.json')
        if not os.path.exists(zh_cn_path) or os.path.getsize(zh_cn_path) == 0:
            with open(zh_cn_path, 'w', encoding='utf-8') as f:
                json.dump(lang_data, f, ensure_ascii=False, indent=2)
            print(f"已创建中文语言文件: {zh_cn_path}")
        else:
            print(f"中文语言文件已存在且不为空，跳过创建")

        # 加载模块语言文件
        LangManager.load_module_language_file(module_path)
        print("测试模块补全完成")
        return True
    except Exception as e:
        print(f"补全测试模块失败: {str(e)}")
        return False


def get_module_class():
    """
    返回模块的主类
    这个方法会被ModuleBootstraper调用，用于注册模块

    Returns:
        class: 模块的主类
    """
    # 使用importlib.util从文件路径直接导入，避免相对导入问题
    import importlib.util
    import os
    # 获取当前模块所在目录
    module_dir = os.path.dirname(os.path.abspath(__file__))
    # 构造模块文件路径
    module_file_path = os.path.join(module_dir, 'ocr_test_module.py')
    # 创建模块规范
    spec = importlib.util.spec_from_file_location('ocr_test_module', module_file_path)
    # 加载模块
    ocr_module = importlib.util.module_from_spec(spec)
    # 执行模块
    spec.loader.exec_module(ocr_module)
    # 返回模块类
    return ocr_module.OCRTestModule