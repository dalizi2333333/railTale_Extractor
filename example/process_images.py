import os
import sys
import time
import json
import requests
from pathlib import Path

# 获取当前脚本所在目录
current_dir = os.path.dirname(os.path.abspath(__file__))
# 获取父级目录
parent_dir = os.path.dirname(current_dir)

# GitHub仓库基础URL
GITHUB_BASE_URL = 'https://raw.githubusercontent.com/dalizi2333333/railTale_Extractor/main/'

# 添加父级目录到Python路径
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

# 检查bootstrap.py是否存在
bootstrap_path = os.path.join(parent_dir, 'lib', 'bootstrap.py')
if not os.path.exists(bootstrap_path):
    print('Bootstrap module not found. Downloading from GitHub...')
    try:
        # 下载bootstrap.py
        response = requests.get(f'{GITHUB_BASE_URL}lib/bootstrap.py', timeout=10)
        response.raise_for_status()
        with open(bootstrap_path, 'wb') as f:
            f.write(response.content)
        print(f'Successfully downloaded bootstrap.py to: {bootstrap_path}')
        print('\nFirst download of bootstrap.py detected. To ensure successful import, please restart the program.')
        print('Program will exit in 3 seconds...')
        time.sleep(3)
        sys.exit(0)
    except Exception as e:
        print(f'Failed to download bootstrap.py: {str(e)}')
        print('Program will exit.')
        sys.exit(1)

# 尝试导入bootstrap功能
try:
    from lib.bootstrap import bootstrap
    bootstrap_available = True
except ImportError:
    print('Failed to import bootstrap module even though file exists.')
    print('Program will exit.')
    sys.exit(1)

# 初始化本地化管理器
loc_manager = bootstrap(parent_dir)

# 添加lib目录到Python路径
lib_dir = os.path.join(parent_dir, 'lib')
if lib_dir not in sys.path:
    sys.path.append(lib_dir)

# 添加父级目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 预加载OCR模块配置并注册依赖
from lib.ocr_module_loader import OCRModuleLoader
loader = OCRModuleLoader(parent_dir)
config = loader.load_config()
# 在依赖检查前注册OCR模块依赖
loader.pre_register_module_dependencies()

# 检查必要的库是否安装
from lib.dependency_check import dependency_checker
dependency_checker.check_all_dependencies()

# 导入文本处理加载器
from lib.text_processing_loader import TextProcessingLoader

# 读取配置
from lib.config.config_manager import ConfigManager
config_manager = ConfigManager(process_dir=current_dir)
config = config_manager.get_config()

# 目录名称（用于结果文件命名）
dir_name = os.path.basename(current_dir)

# 准备配置参数
loader_config = {
    'output_file': os.path.join(parent_dir, f'{dir_name}.txt'),
    'debug_output_file': os.path.join(parent_dir, f'{dir_name}_ocr_debug.txt'),
    'output_ocr_debug': config.get('output_ocr_debug', 'false').lower() == 'true',
    'ocr_language': config.get('OCR_LANGUAGE', 'default'),
    'current_dir': current_dir,
    'max_vertical_images': config.get('max_vertical_images')
}

# 导入本地化管理器
from lib.bootstrap import LocalizationManager
# 获取本地化管理器实例
loc_manager = LocalizationManager.get_instance()

# 创建文本处理加载器实例
text_processing_loader = TextProcessingLoader(loader_config)

# 运行处理流程
if not text_processing_loader.run():
    print(loc_manager.get_lang_data()['process_flow_fail'])
    sys.exit(1)

# 程序正常结束
print(loc_manager.get_lang_data()['process_complete'])