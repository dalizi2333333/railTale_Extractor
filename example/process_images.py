import os
import sys
import time
import json
import requests
from pathlib import Path

# 获取必要路径
process_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
project_download_url = 'https://raw.githubusercontent.com/dalizi2333333/railTale_Extractor/main/'

# 创建lib目录（如果不存在）
lib_dir = os.path.join(parent_dir, 'lib')
os.makedirs(lib_dir, exist_ok=True)

# 检查bootstrap.py是否存在
bootstrap_path = os.path.join(lib_dir, 'bootstrap.py')
if not os.path.exists(bootstrap_path):
    print('Bootstrap module not found. Downloading...')
    try:
        # 下载bootstrap.py
        response = requests.get(f'{project_download_url}lib/bootstrap.py', timeout=10)
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

# 添加lib目录到Python路径
if lib_dir not in sys.path:
    sys.path.append(lib_dir)

# 尝试导入bootstrap功能
try:
    from bootstrap import bootstrap
    bootstrap_available = True
except ImportError:
    print('Failed to import bootstrap module even though file exists.')
    print('Program will exit.')
    sys.exit(1)

# 创建paths结构，仅在需要传递时封包
paths = {
    'process_dir': process_dir,
    'parent_dir': parent_dir,
    'project_download_url': project_download_url
}

# 初始化项目，传入paths
bootstrap(paths)

# process_images.py现在只负责确定paths并初始化项目
# 所有实际处理逻辑已移至bootstrap中
print('Image processing initialized through bootstrap.')
print('Processing will continue in bootstrap module...')

sys.exit(0)