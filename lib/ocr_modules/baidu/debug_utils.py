import json

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
    def generate_debug_entry(file_name, use_custom_font, text, lang_data, debug_info):
        """生成完整的OCR调试信息条目"""
        # 使用语言文件中的标题格式
        debug_entry = lang_data.get('ocr_debug_header', '=== Image {} OCR recognition results ===').format(file_name) + '\n'
        
        # 识别模式
        recognition_mode = lang_data.get('high_precision_mode', 'High precision') if use_custom_font else lang_data.get('general_mode', 'General')
        debug_entry += f"{lang_data.get('recognition_mode', 'Recognition mode')}: {recognition_mode}\n"
        
        if debug_info:
            # 识别类型
            language_type = debug_info.get('options', {}).get('language_type', lang_data.get('unknown', 'Unknown'))
            debug_entry += f"{lang_data.get('recognition_type', 'Recognition type')}: {language_type}\n"
            
            # 识别文本
            debug_entry += f"{lang_data.get('recognized_text', 'Recognized text')}: {text}\n"
            
            # 添加额外的模块特定调试信息
            if 'result' in debug_info:
                api_status = lang_data.get('success', 'Success') if 'words_result' in debug_info['result'] else lang_data.get('failure', 'Failure')
                debug_entry += f"{lang_data.get('api_status', 'API return status')}: {api_status}\n"
                if 'error_msg' in debug_info['result']:
                    debug_entry += f"{lang_data.get('error_message', 'Error message')}: {debug_info['result']['error_msg']}\n"
            
            # 添加原始识别结果
            if 'raw_result_str' in debug_info:
                debug_entry += f"{lang_data.get('raw_recognition_result', 'Raw recognition result')}: {debug_info['raw_result_str']}\n"
            
            # 添加字块详情
            if 'blocks' in debug_info:
                debug_entry += f"{lang_data.get('block_details', 'Block details')}:\n"
                for block in debug_info['blocks']:
                    debug_entry += f"  {lang_data.get('block', 'Block')} {block['index']}: {lang_data.get('content', 'Content')}=\"{block['content']}\""
                    if block['confidence'] is not None:
                        debug_entry += f", {lang_data.get('confidence', 'Confidence')}={block['confidence']}\n"
                    else:
                        debug_entry += "\n"
                    # 添加默认处理说明
                    debug_entry += f"  {lang_data.get('processing', 'Processing')}: {lang_data.get('keep', 'Keep')}\n"
        else:
            debug_entry += f"{lang_data.get('recognition_type', 'Recognition type')}: {lang_data.get('unknown', 'Unknown')}\n"
            debug_entry += f"{lang_data.get('recognized_text', 'Recognized text')}: {text}\n"
        
        return debug_entry