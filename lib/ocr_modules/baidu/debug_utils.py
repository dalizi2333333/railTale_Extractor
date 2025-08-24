import json
from lib.lang_manager import LangManager

class BaiduOCRDebugUtils:
    """百度OCR调试工具类"""

    @staticmethod
    def get_recognition_debug_info(last_recognition_debug_info):
        """获取OCR识别的调试信息，包括原始结果和字块详情"""
        debug_info = last_recognition_debug_info.copy()
        
        # 如果有识别结果，处理字块详情
        if 'result' in debug_info and 'words_result' in debug_info['result']:
            result = debug_info['result']
            
            # 添加原始识别结果的JSON字符串
            debug_info['raw_result_str'] = json.dumps(result, ensure_ascii=False, indent=2)
            
            # 处理字块详情
            blocks = []
            for i, word in enumerate(result['words_result']):
                block = {
                    'index': i + 1,
                    'content': word['words'],
                    'confidence': word['probability']['average'] if 'probability' in word else None
                }
                blocks.append(block)
            
            debug_info['blocks'] = blocks
        
        return debug_info

    @staticmethod
    def generate_debug_entry(file_name, use_custom_font, text, debug_info):
        """生成完整的OCR调试信息条目

        Args:
            file_name (str): 图片文件名
            use_custom_font (bool): 是否使用自定义字体
            text (str): OCR识别结果文本
            debug_info (dict): OCR识别的调试信息字典

        Returns:
            str: 格式化的调试信息字符串，包含文件名、识别模式、识别文本和详细调试信息
        """
        # 使用语言文件中的标题格式
        debug_entry = LangManager.get_module_lang_data()['ocr_debug_header'].format(file_name) + '\n'
        
        # 识别模式
        recognition_mode = LangManager.get_module_lang_data()['high_precision_mode'] if use_custom_font else LangManager.get_module_lang_data()['general_mode']
        debug_entry += f"{LangManager.get_module_lang_data()['recognition_mode']}: {recognition_mode}\n"
        
        if debug_info:
            # 识别类型
            language_type = debug_info.get('options', {}).get('language_type', LangManager.get_module_lang_data()['unknown'])
            debug_entry += f"{LangManager.get_module_lang_data()['recognition_type']}: {language_type}\n"
            
            # 识别文本
            debug_entry += f"{LangManager.get_module_lang_data()['recognized_text']}: {text}\n"
            
            # 添加额外的模块特定调试信息
            if 'result' in debug_info:
                api_status = LangManager.get_module_lang_data()['success'] if 'words_result' in debug_info['result'] else LangManager.get_module_lang_data()['failure']
                debug_entry += f"{LangManager.get_module_lang_data()['api_status']}: {api_status}\n"
                if 'error_msg' in debug_info['result']:
                    debug_entry += f"{LangManager.get_module_lang_data()['error_message']}: {debug_info['result']['error_msg']}\n"  
            
            # 添加原始识别结果
            if 'raw_result_str' in debug_info:
                debug_entry += f"{LangManager.get_module_lang_data()['raw_recognition_result']}: {debug_info['raw_result_str']}\n"
            
            # 添加字块详情
            if 'blocks' in debug_info:
                debug_entry += f"{LangManager.get_module_lang_data()['block_details']}:\n"
                for block in debug_info['blocks']:
                    debug_entry += f"  {LangManager.get_module_lang_data()['block']} {block['index']}: {LangManager.get_module_lang_data()['content']}=\"{block['content']}\""
                    if block['confidence'] is not None:
                        debug_entry += f", {LangManager.get_module_lang_data()['confidence']}={block['confidence']}\n"
                    else:
                        debug_entry += "\n"
                    # 添加默认处理说明
                    debug_entry += f"  {LangManager.get_module_lang_data()['processing']}: {LangManager.get_module_lang_data()['keep']}\n"
        else:
            debug_entry += f"{LangManager.get_module_lang_data()['recognition_type']}: {LangManager.get_module_lang_data()['unknown']}\n"
            debug_entry += f"{LangManager.get_module_lang_data()['recognized_text']}: {text}\n"
        
        return debug_entry