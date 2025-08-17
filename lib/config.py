import os
import sys
import requests

def read_config(lang_data):
    # 配置文件路径
    config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'example', 'config.txt')
    
    # 检查配置文件是否存在，如果不存在则尝试从GitHub获取
    if not os.path.exists(config_path):
        print(lang_data['config_not_found'])
        
        # GitHub原始文件URL
        github_url = 'https://raw.githubusercontent.com/dalizi2333333/railTale_Extractor/main/example/config.txt.example'
        
        try:
            # 下载配置文件
            response = requests.get(github_url, timeout=10)
            response.raise_for_status()  # 检查请求是否成功
            
            # 将下载的内容保存为config.txt
            with open(config_path, 'w', encoding='utf-8') as f:
                f.write(response.text)
            
            print(lang_data['config_download_success'].format(config_path))
            sys.exit(1)
        except requests.exceptions.RequestException as e:
            print(lang_data['config_download_fail'].format(str(e), github_url))
            sys.exit(1)
    
    # 读取配置文件
    config = {}
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            for line in f:
                # 跳过注释和空行
                if line.strip().startswith('#') or not line.strip():
                    continue
                # 解析配置项
                if '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip().strip("'").strip('"')
                    config[key] = value
    except Exception as e:
        print(lang_data['config_read_error'].format(str(e)))
        sys.exit(1)
    
    # 检查必要的配置项是否存在
    required_keys = ['APP_ID', 'API_KEY', 'SECRET_KEY']
    for key in required_keys:
        if key not in config:
            print(lang_data['missing_required_config'].format(key))
            sys.exit(1)
    
    return config