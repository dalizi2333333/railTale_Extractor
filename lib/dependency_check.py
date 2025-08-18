import sys
from bootstrap import LocalizationManager

class DependencyChecker:
    """依赖检查器，用于管理和检查项目依赖"""

    # 基础依赖定义（模块名:安装名）
    BASE_DEPENDENCIES = {
        'PIL': 'Pillow',
        'chardet': 'chardet',
        'requests': 'requests'
    }

    def __init__(self):
        # 获取本地化管理器实例
        self.loc_manager = LocalizationManager.get_instance()
        self.lang_data = self.loc_manager.get_lang_data()

        # 模块特定依赖映射
        self.module_dependencies = {}
        # 特殊依赖库映射 (安装名 -> (模块名, 安装名))
        self.special_dependencies = {}
        
    def load_requirements(self):
        """加载依赖库列表，仅使用代码中定义的BASE_DEPENDENCIES常量"""
        return list(self.BASE_DEPENDENCIES.items())
    
    def register_module_dependencies(self, module_name, dependencies):
        """注册特定模块的依赖
        
        Args:
            module_name: 模块名称
            dependencies: 依赖列表，每个元素为(module_name, install_name)元组
        """
        self.module_dependencies[module_name] = dependencies
        
    def register_special_dependency(self, install_name, module_name):
        """注册特殊依赖库的模块名和安装名映射
        
        Args:
            install_name: 依赖库的安装名 (如 'baidu-aip')
            module_name: 依赖库的模块名 (如 'aip')
        """
        self.special_dependencies[install_name] = (module_name, install_name)
        
    def check_module_dependencies(self, module_name, exit_on_error=True):
        """检查特定模块的依赖
        
        Args:
            module_name: 模块名称
            exit_on_error: 如果依赖缺失，是否退出程序
            
        Returns:
            bool: 如果依赖都满足，返回True；否则返回False
        """
        if module_name not in self.module_dependencies:
            print(self.lang_data.get('module_not_registered', '模块未注册: {}').format(module_name))
            return False
            
        dependencies = self.module_dependencies[module_name]
        missing_libraries = []
        
        for lib_name, pip_name in dependencies:
            try:
                __import__(lib_name)
                # 验证导入是否成功
                module = sys.modules.get(lib_name)
                if module is None:
                    raise ImportError(self.lang_data.get('module_load_fail', '无法加载模块 {}').format(lib_name))
                
                print(self.lang_data.get('lib_import_success', '成功导入 {}').format(lib_name))
            except ImportError as e:
                missing_libraries.append((lib_name, pip_name))
                print(self.lang_data.get('lib_import_fail', '导入失败 {}: {}').format(lib_name, str(e)))
        
        if missing_libraries:
            print(self.lang_data.get('missing_module_libs', '模块 {} 缺少必要的依赖库').format(module_name))
            # 打印Python环境信息
            print(self.lang_data.get('python_env_info', '当前Python解释器路径: {}\nPython版本: {}\nPython路径:').format(sys.executable, sys.version))
            for path in sys.path:
                print(f'  - {path}')
            
            for lib_name, pip_name in missing_libraries:
                print(self.lang_data.get('lib_install_prompt_line', '  - {} (推荐使用命令安装: pip install {{}})').format(lib_name, pip_name))
            
            # 准备镜像源安装命令
            mirror_commands = ''
            for _, pip_name in missing_libraries:
                mirror_commands += f'   pip install -i https://mirrors.aliyun.com/pypi/simple/ {pip_name}\n'
            
            # 准备sudo安装命令
            sudo_commands = ''
            for _, pip_name in missing_libraries:
                sudo_commands += f'   sudo pip install {pip_name}\n'
            
            # 打印安装提示
            print(self.lang_data.get('install_lib_prompt', '\n安装提示:\n1. 首先必须更新pip到最新版本:\n   python -m pip install --upgrade pip\n2. 如果安装失败，可能是网络问题，建议使用国内镜像源:\n{}\n3. Windows用户如果遇到权限问题，请以管理员身份运行命令提示符\n4. macOS/Linux用户如果遇到权限问题，尝试使用sudo:\n{}\n5. 确保使用的Python环境与安装库时的环境一致').format(mirror_commands.strip(), sudo_commands.strip()))
            
            if exit_on_error:
                sys.exit(1)
            return False
        
        return True
    
    def check_all_dependencies(self, exit_on_error=True):
        """检查所有依赖库是否安装
        
        Args:
            exit_on_error: 如果依赖缺失，是否退出程序
            
        Returns:
            bool: 如果依赖都满足，返回True；否则返回False
        """
        # 加载依赖库列表
        required_libraries = self.load_requirements()
        missing_libraries = []
        
        for lib_name, pip_name in required_libraries:
            try:
                __import__(lib_name)
                # 验证导入是否成功
                module = sys.modules.get(lib_name)
                if module is None:
                    raise ImportError(self.lang_data.get('module_load_fail', '无法加载模块 {}').format(lib_name))
                
                print(self.lang_data.get('lib_import_success', '成功导入 {}').format(lib_name))
            except ImportError as e:
                missing_libraries.append((lib_name, pip_name))
                print(self.lang_data.get('lib_import_fail', '导入失败 {}: {}').format(lib_name, str(e)))
        
        if missing_libraries:
            print(self.lang_data.get('missing_required_libs', '错误: 缺少必要的Python库'))
            # 打印Python环境信息
            print(self.lang_data.get('python_env_info', '当前Python解释器路径: {}\nPython版本: {}\nPython路径:').format(sys.executable, sys.version))
            for path in sys.path:
                print(f'  - {path}')
            
            for lib_name, pip_name in missing_libraries:
                print(self.lang_data.get('lib_install_prompt_line', '  - {} (推荐使用命令安装: pip install {{}})').format(lib_name, pip_name))
            
            # 准备镜像源安装命令
            mirror_commands = ''
            for _, pip_name in missing_libraries:
                mirror_commands += f'   pip install -i https://mirrors.aliyun.com/pypi/simple/ {pip_name}\n'
            
            # 准备sudo安装命令
            sudo_commands = ''
            for _, pip_name in missing_libraries:
                sudo_commands += f'   sudo pip install {pip_name}\n'
            
            # 打印安装提示
            print(self.lang_data.get('install_lib_prompt', '\n安装提示:\n1. 首先必须更新pip到最新版本:\n   python -m pip install --upgrade pip\n2. 如果安装失败，可能是网络问题，建议使用国内镜像源:\n{}\n3. Windows用户如果遇到权限问题，请以管理员身份运行命令提示符\n4. macOS/Linux用户如果遇到权限问题，尝试使用sudo:\n{}\n5. 确保使用的Python环境与安装库时的环境一致').format(mirror_commands.strip(), sudo_commands.strip()))
            
            if exit_on_error:
                sys.exit(1)
            return False
        
        return True
    
# 创建全局依赖检查器实例
dependency_checker = DependencyChecker()

# 全局依赖检查器实例已创建，可直接使用 dependency_checker.check_all_dependencies()

# 注：模块依赖和特殊依赖映射应通过各模块自身初始化时注册，而非在此硬编码

if __name__ == '__main__':
    # 如果直接运行此文件，提供一个简单的测试
    test_lang_data = {
        'lib_import_success': '成功导入 {}',
        'lib_import_fail': '导入失败 {}: {}',
        'missing_required_libs': '错误: 缺少必要的Python库',
        'python_env_info': '当前Python解释器路径: {}\nPython版本: {}\nPython路径:',
        'lib_install_prompt_line': '  - {} (推荐使用命令安装: pip install {})',
        'install_lib_prompt': '\n安装提示:\n1. 首先必须更新pip到最新版本:\n   python -m pip install --upgrade pip\n2. 如果安装失败，可能是网络问题，建议使用国内镜像源:\n{}\n3. Windows用户如果遇到权限问题，请以管理员身份运行命令提示符\n4. macOS/Linux用户如果遇到权限问题，尝试使用sudo:\n{}\n5. 确保使用的Python环境与安装库时的环境一致',
        'module_load_fail': '无法加载模块 {}',
        'module_not_registered': '模块未注册: {}',
        'missing_module_libs': '模块 {} 缺少必要的依赖库',
    }
    
    # 测试检查所有依赖
    print("=== 测试检查所有依赖 ===")
    dependency_checker.check_all_dependencies()
    
    # 测试检查模块依赖 (使用测试模块名)
    print("\n=== 测试检查模块依赖 ===")
    # 注册一个测试模块依赖用于演示
    test_module = 'test_module'
    test_deps = [('requests', 'requests')]
    dependency_checker.register_module_dependencies(test_module, test_deps)
    dependency_checker.check_module_dependencies(test_module, exit_on_error=False)
    
    print("\n所有测试完成!")