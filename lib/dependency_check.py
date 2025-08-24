import os
import sys
import subprocess
import importlib
from lib.lang_manager import LangManager
from lib.config.config_manager import ConfigManager


def check_dependencies(required_deps):
    """
    检查模块依赖是否满足

    Args:
        required_deps (dict): 从模块bootstrap获取的依赖信息，格式为
                              {import_name: {'install_name': install_name, 'version': version}}

    Returns:
        bool: 依赖是否满足
    """
    # 基础依赖定义（模块名:安装名）
    BASE_DEPENDENCIES = {
        'PIL': {'install_name': 'Pillow', 'version': '>=9.0.0'},
        'chardet': {'install_name': 'chardet', 'version': '>=4.0.0'},
        'requests': {'install_name': 'requests', 'version': '>=2.25.0'}
    }
    
    # 合并基础依赖和模块特定依赖
    all_deps = {**BASE_DEPENDENCIES, **required_deps}
    
    missing_deps = []
    install_commands = []

    # 检查每个依赖
    for import_name, dep_info in all_deps.items():
        install_name = dep_info['install_name']
        version = dep_info['version']

        try:
            # 尝试导入模块
            importlib.import_module(import_name)
            # 这里可以添加版本检查逻辑
        except ImportError:
            missing_deps.append(install_name)
            # 构建安装命令
            install_commands.append(f"pip install {install_name}{version}")

    # 如果有缺失的依赖
    if missing_deps:
        print(LangManager.get_lang_data()['dependency_missing'].format(', '.join(missing_deps)))

        # 尝试安装依赖
        success = False
        try:
            print(LangManager.get_lang_data()['trying_install_deps'])
            for cmd in install_commands:
                print(f"{LangManager.get_lang_data()['executing']}: {cmd}")
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                if result.returncode != 0:
                    print(f"{LangManager.get_lang_data()['install_failed']}: {cmd}")
                    print(f"{LangManager.get_lang_data()['error_info']}: {result.stderr}")
                else:
                    print(f"{LangManager.get_lang_data()['install_success']}: {cmd}")
            success = True
        except Exception as e:
            print(f"{LangManager.get_lang_data()['install_exception']}: {str(e)}")

        # 生成依赖安装提示文件
        process_dir = ConfigManager.get_process_dir()
        if not process_dir:
            process_dir = os.getcwd()

        guide_file = os.path.join(process_dir, "dependency_installation_guide.txt")
        with open(guide_file, 'w', encoding='utf-8') as f:
            f.write(LangManager.get_lang_data()['dependency_guide_title'] + '\n\n')
            f.write(LangManager.get_lang_data()['missing_deps_list'] + '\n')
            for dep in missing_deps:
                f.write(f"- {dep}\n")
            f.write('\n' + LangManager.get_lang_data()['install_commands_title'] + '\n')
            for cmd in install_commands:
                f.write(f"{cmd}\n")
            f.write('\n' + LangManager.get_lang_data()['restart_note'])

        print(LangManager.get_lang_data()['guide_file_created'].format(guide_file))
        print(LangManager.get_lang_data()['restart_program'])
        return False

    # 所有依赖都满足
    return True