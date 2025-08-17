import sys

# 必要的库
required_libraries = [
    ('PIL', 'Pillow'),
    ('chardet', 'chardet'),
    ('aip', 'baidu-aip'),
    ('requests', 'requests'),
]

def check_dependencies(lang_data):
    """检查必要的依赖库是否安装"""
    missing_libraries = []
    for lib_name, pip_name in required_libraries:
        try:
            __import__(lib_name)
            # 验证导入是否成功
            module = sys.modules.get(lib_name)
            if module is None:
                raise ImportError(f"无法加载模块 {lib_name}")
            print(lang_data['lib_import_success'].format(lib_name))  # 调试信息
        except ImportError as e:
            missing_libraries.append((lib_name, pip_name))
            print(lang_data['lib_import_fail'].format(lib_name, str(e)))  # 调试信息

    if missing_libraries:
        print(lang_data['missing_required_libs'])
        # 打印Python环境信息
        print(lang_data['python_env_info'].format(sys.executable, sys.version))
        for path in sys.path:
            print(f'  - {path}')
        
        for lib_name, pip_name in missing_libraries:
            print(lang_data['lib_install_prompt_line'].format(lib_name, pip_name))
        
        # 准备镜像源安装命令
        mirror_commands = ''
        for _, pip_name in missing_libraries:
            mirror_commands += f'   pip install -i https://mirrors.aliyun.com/pypi/simple/ {pip_name}\n'
        
        # 准备sudo安装命令
        sudo_commands = ''
        for _, pip_name in missing_libraries:
            sudo_commands += f'   sudo pip install {pip_name}\n'
        
        # 打印安装提示
        print(lang_data['install_lib_prompt'].format(mirror_commands.strip(), sudo_commands.strip()))
        sys.exit(1)

    return True

if __name__ == '__main__':
    # 如果直接运行此文件，提供一个简单的测试
    test_lang_data = {
        'lib_import_success': '成功导入 {}',
        'lib_import_fail': '导入失败 {}: {}',
        'missing_required_libs': '错误: 缺少必要的Python库',
        'python_env_info': '当前Python解释器路径: {}\nPython版本: {}\nPython路径:',
        'lib_install_prompt_line': '  - {} (推荐使用命令安装: pip install {})',
        'install_lib_prompt': '\n安装提示:\n1. 首先必须更新pip到最新版本:\n   python -m pip install --upgrade pip\n2. 如果安装失败，可能是网络问题，建议使用国内镜像源:\n{}\n3. Windows用户如果遇到权限问题，请以管理员身份运行命令提示符\n4. macOS/Linux用户如果遇到权限问题，尝试使用sudo:\n{}\n5. 确保使用的Python环境与安装库时的环境一致'
    }
    check_dependencies(test_lang_data)