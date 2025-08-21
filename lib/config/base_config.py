# 基本配置定义

# 主应用配置
APP_CONFIG_DEFINITIONS = {
    'OUTPUT_OCR_DEBUG': {
        'type': 'boolean',
        'options': ['true', 'false'],
        'default': 'false',
        'description': '是否输出OCR调试信息到独立文件',
        'required': False
    },
    'START_MARKERS': {
        'type': 'string',
        'subtype': 'non_empty',
        'default': '剧情梗概',
        'description': '开始标记: 当检测到这些文字块时开始记录每张图片内识别到的文本，多个标记用逗号分隔',
        'required': True
    },
    'STOP_MARKERS': {
        'type': 'string',
        'subtype': 'non_empty',
        'default': 'i,存在分支剧情选项,取消,×,⑧取消',
        'description': '结束标记: 当检测到这些文字块时停止记录每张图片内识别到的文本，多个标记用逗号分隔',
        'required': True
    },
    'OCR_MODULE': {
        'type': 'string',
        'subtype': 'option',
        'options': ['baidu'],
        'default': 'baidu',
        'description': 'OCR模块选择',
        'required': True
    },
    'MAX_VERTICAL_IMAGES': {
        'type': 'integer',
        'min_value': 1,
        'max_value': 10,
        'default': '4',
        'description': '纵向拼接识别的最大图片数量',
        'required': False
    },
    'OCR_LANGUAGE': {
        'type': 'string',
        'options': ['zh-cn', 'en', 'ja-jp'],
        'default': 'zh-cn',
        'description': 'OCR识别语言',
        'required': False
    }
}

# 模块配置注册表
MODULE_CONFIG_REGISTRY = {}

# 合并所有配置定义
CONFIG_DEFINITIONS = {**APP_CONFIG_DEFINITIONS}