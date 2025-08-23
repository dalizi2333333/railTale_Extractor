import os
import sys
from lib.config.config_manager import ConfigManager
from lib.lang_manager import LangManager

class ProjectProcessor:
    """项目处理器类，负责项目的实际业务处理流程"""
    @staticmethod
    def process():
        """处理项目
        """
        # 确保配置管理器已初始化
        if not hasattr(ConfigManager, '_initialized') or not ConfigManager._initialized:
            raise Exception('ConfigManager not initialized')

        # 从配置管理器获取必要路径
        parent_dir = ConfigManager.get_parent_dir()
        process_dir = ConfigManager.get_process_dir()

        # 获取项目配置
        project_config = ConfigManager.get_config()

        # 目录名称（用于结果文件命名）
        dir_name = os.path.basename(process_dir)

        # 准备配置参数
        loader_config = {
            'output_file': os.path.join(parent_dir, f'{dir_name}.txt'),
            'debug_output_file': os.path.join(parent_dir, f'{dir_name}_ocr_debug.txt'),
            'output_ocr_debug': project_config.get('output_ocr_debug', 'false').lower() == 'true',
            'ocr_language': project_config.get('OCR_LANGUAGE', 'default'),
            'current_dir': process_dir,
            'max_vertical_images': project_config.get('max_vertical_images')
        }

        # 导入文本处理加载器
        from lib.text_processing_loader import TextProcessingLoader

        # 创建文本处理加载器实例
        text_processing_loader = TextProcessingLoader(loader_config)

        # 运行处理流程
        loc_manager = LangManager.get_instance()
        if not text_processing_loader.run():
            print(loc_manager.get_lang_data().get('process_flow_fail', 'Processing failed'))
            sys.exit(1)

        # 程序正常结束
        print(loc_manager.get_lang_data().get('process_complete', 'Processing complete'))