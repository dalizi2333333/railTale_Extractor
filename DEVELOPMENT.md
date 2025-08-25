# 开发文档

## 项目入口脚本说明

### 运行流程
项目的主要入口是`example/process_images.py`，该脚本通过调用`lib/bootstrap.py`中的`bootstrap`方法来初始化并运行项目。

### 关键调用部分
```python
# 初始化项目，传入paths
bootstrap(paths)
```

### 路径参数
`paths`参数包含以下关键信息：
```python
paths = {
    'process_dir': process_dir,  # 当前处理目录
    'parent_dir': parent_dir,    # 父目录
    'project_download_url': project_download_url  # 项目下载URL
}
```

这意味着你可以通过修改`project_download_url`来支持自定义分支：
```python
# 默认值
project_download_url = 'https://raw.githubusercontent.com/dalizi2333333/railTale_Extractor/main/'

# 修改为自定义分支
project_download_url = 'https://raw.githubusercontent.com/your_username/railTale_Extractor/your_branch/'
```

### Bootstrap方法返回值
`bootstrap`方法返回以下值，可用于调试或进一步开发：
```python
return {
    'config_manager': config_manager,
    'lang_manager': lang_manager,
    'paths': paths,
    'exists_config': exists_config,
    'text': text
}
```
比如利用返回值text来直接丢进TTS项目跑语音生成，然后生成语音识别字幕生成剪映项目一气呵成什么的

## OCR模块开发指南

### 模块结构
每个OCR模块必须包含`module_bootstrap.py`文件，并实现以下五个方法：

1. `get_required_dependencies`
2. `get_required_config_items`
3. `has_mandatory_config`
4. `complete_module`
5. `get_module_class`

### 方法定义

#### get_required_dependencies
```
返回模块需要的额外依赖
这些依赖不会被自动安装，需要用户手动安装或通过依赖管理工具安装

Returns:
    dict: 包含依赖信息的字典，格式为:
```
```python
{
    import_name: {
        'install_name': install_name, 
        'version': version
    }
}
```

#### complete_module
```
补全模块的方式
负责初始化模块所需的语言文件和其他资源

Returns:
    bool: 是否补全成功
```

#### get_required_config_items
```
返回模块需要的配置项
这些配置项将被添加到配置文件中

Returns:
    dict: 包含配置项名称、类型、默认值和描述的字典，格式为:
```

```python
{
    'EXAMPLE_1': {
        'type': 'bool',
        'options': ['True', 'False'],
        'default': 'False',
        'description_key': 'example_1_desc', # 配置描述的本地化键，可以在模块的本地化文件中添加
        'required': False,
        'cannot_use_default': False #这一项会在加载配置文件中时被检测，如果为True，那么在加载配置文件时如果发现这个配置项的值为默认值时就会报错
    },
    'EXAMPLE_2': {
        'type': 'string',
        'subtype': 'non_empty',
        'default': 'any_non_empty_str',
        'description_key': 'example_2_desc',
        'required': True,
        'cannot_use_default': False
    },
    'EXAMPLE_3': {
        'type': 'string',
        'subtype': 'option',
        'options': ['example_3_option_1','example_3_option_2'],
        'default': 'example_3_option_1',
        'description_key': 'example_3_desc',
        'required': True,
        'cannot_use_default': False
    },
    'EXAMPLE_4': {
        'type': 'integer',
        'min_value': 1,
        'max_value': 10,
        'default': '4',
        'description_key': 'example_4_desc',
        'required': False,
        'cannot_use_default': False
    },
    'EXAMPLE_5': {
        'type': 'string',
        'default': 'your_secret_key',
        'description_key': 'example_5_desc',
        'cannot_use_default': True
    }
}
```
好吧我承认配置系统可能设计的有点过于健壮了，反正他是先检测有没有'cannot_use_default': True，然后无论你是啥类型实际上都是存成了字符串，你不按照上面的标准写倒是也没啥问题
#### has_mandatory_config
```
返回模块是否有不可为默认值的配置项
如果返回True，当根据complete_module方法补全模块后，程序会退出并提醒用户修改配置

Returns:
    bool: 是否有不可为默认值的配置项
```

#### get_module_class
```
返回模块的主类
这个方法会被ModuleBootstraper调用，用于注册模块

Returns:
    class: 模块的主类
```

### 模块主类
模块主类必须继承自`OCRModuleInterface`，并实现以下抽象方法：

```python
class OCRModuleInterface(ABC):
    @abstractmethod
    def init_ocr_client(self):
        """初始化OCR客户端

        Returns:
            bool: 初始化成功返回True，失败返回False
        """
        pass

    @abstractmethod
    def recognize_text(self, image_path):
        """识别图片中的文本

        Args:
            image_path (str): 图片文件路径

        Returns:
            str: 识别出的文本，失败时返回None
        """
        pass

    @abstractmethod
    def get_recognition_debug_info(self):
        """获取上一次OCR识别的完整调试信息条目

        Returns:
            str: 格式化的调试信息字符串，包含文件名、识别模式、识别文本和详细调试信息
        """
        pass

    @abstractmethod
    def get_api_delay(self):
        """获取API调用之间的延迟时间(秒)

        Returns:
            float: API调用之间的延迟时间(秒)
        """
        pass

    @abstractmethod
    def get_max_width(self):
        """获取OCR模块支持的最大图片宽度(像素)

        Returns:
            int: 支持的最大图片宽度(像素)
        """
        pass

    @abstractmethod
    def get_max_height(self):
        """获取OCR模块支持的最大图片高度(像素)

        Returns:
            int: 支持的最大图片高度(像素)
        """
        pass
```

## 系统使用说明

### 本地化系统 (LangManager)

LangManager类提供以下方法用于获取本地化文本：

```python
class LangManager:
    @classmethod
    def get_lang(cls, key):
        """
        获取基础语言文本，如果键不存在则返回键本身

        Args:
            key (str): 语言键

        Returns:
            str: 语言文本或键本身
        """
        return cls()._lang_data.get(key, key)

    @classmethod
    def get_module_lang(cls, key):
        """
        获取模块语言文本，如果键不存在则返回键本身

        Args:
            key (str): 模块语言键

        Returns:
            str: 模块语言文本或键本身
        """
        return cls()._module_lang_data.get(key, key)
```
使用例：
```python
# 导入LangManager类
from lang_manager import LangManager

# 获取基础语言文本
base_text = LangManager.get_lang('hello')
print(base_text)  # 输出: '你好'

# 获取模块语言文本
module_text = LangManager.get_module_lang('module_hello')
print(module_text)  # 输出: '模块的你好'
```
也提供了将语言文件注册进语言系统的方法，如果需要的话：
```python
class LangManager:
    @classmethod
    def load_module_language_file(cls, module_path):
        """加载子模块文件夹里lang文件夹内的子语言文件到模块语言数据表中

        Args:
            module_path (str): 模块路径

        Returns:
            bool: 是否成功加载
        """
```
你问为什么是注册进模块语言数据表？啊。。。因为bootstrap.py会在语言系统没有初始化的时候就使用到主语言文件，所以在bootstrap里其实已经读取过主语言文件了，并会在初始化语言系统时直接将读取主语言文件得到的语言文本注册进语言系统，所以压根没有将语言文件注册进主语言数据表的方法
### 配置系统 (ConfigManager)

ConfigManager提供以下方法用于管理配置：
1. 配置获取

```python
@classmethod
def get(cls, key, default=None):
    """获取配置项

    Args:
        key (str): 配置项键名
        default: 默认值

    Returns:
        配置项值或默认值
    """
```
使用例：
```python
# 导入ConfigManager类
from config.config_manager import ConfigManager

# 获取string类型的配置项
string = ConfigManager.get('EXAMPLE_1')
print(string)  # 输出: 'default_value'

# 因为实际上从配置文件里读取的配置都存成了字符串，所以如果要获取其他类型的配置项，需要进行类型转换

# 获取integer类型的配置项
integer = int(ConfigManager.get('EXAMPLE_4'))
for i in range(integer):
    print(i)  # 输出: 0 1 2 3 4

# 获取boolean类型的配置项
boolean = ConfigManager.get('EXAMPLE_6').lower() == 'true'
if boolean:
    print('EXAMPLE_6 is true')  # 输出: EXAMPLE_6 is true

```
2. 配置设置
```python
@classmethod
def set(cls, key, value):
    """设置配置项

    Args:
        key (str): 配置项键名
        value: 配置项值
    """
```
使用例：
```python
# 导入ConfigManager类
from config.config_manager import ConfigManager

# 设置配置项
ConfigManager.set('EXAMPLE_1', 'new_value')

# 验证配置项是否已更新
print(ConfigManager.get('EXAMPLE_1'))  # 输出: 'new_value'
```
3. 完整配置获取
```python
@classmethod
def get_config(cls):
    """获取完整配置

    Returns:
        dict: 配置字典
    """
```
使用例：
```python
# 导入ConfigManager类
from config.config_manager import ConfigManager

# 获取完整配置
config = ConfigManager.get_config()
print(config)  # 输出: 完整的配置字典
```
4. 路径获取
```python
@classmethod
def get_process_dir(cls):
    """获取处理目录路径

    Returns:
        str: 处理目录路径
    """
```
使用例：
```python
# 导入ConfigManager类
from config.config_manager import ConfigManager

# 获取处理目录路径
process_dir = ConfigManager.get_process_dir()
print(process_dir)  # 输出: 处理目录路径
```
5. 父目录获取
```python
@classmethod
def get_parent_dir(cls):
    """获取父目录路径

    Returns:
        str: 父目录路径
    """
```
使用例：
```python
# 导入ConfigManager类
from config.config_manager import ConfigManager

# 获取父目录路径
parent_dir = ConfigManager.get_parent_dir()
print(parent_dir)  # 输出: 父目录路径
```
6. 项目下载URL获取
```python
@classmethod
def get_project_download_url(cls):
    """获取项目下载URL

    Returns:
        str: 项目下载URL
    """
```
使用例：
```python
# 导入ConfigManager类
from config.config_manager import ConfigManager

# 获取项目下载URL
project_download_url = ConfigManager.get_project_download_url()
print(project_download_url)  # 输出: 项目下载URL
```
7. OCR模块目录获取
```python
@classmethod
def get_ocr_module_dir(cls, module_name):
    """获取OCR模块目录路径

    Args:
        module_name (str): OCR模块名称

    Returns:
        tuple: (模块目录路径, 是否为新创建的目录)
    """
```
这个方法用于获取指定OCR模块的目录路径。如果目录不存在，则会创建一个新目录。
因为会自主新建目录，所以返回值中包含了布尔值以辨别该目录是否是新建的。
毕竟新建的目录里肯定是没有文件的嘛
使用例：
```python
# 导入ConfigManager类
from config.config_manager import ConfigManager

# 获取OCR模块目录路径
module_dir, is_new = ConfigManager.get_ocr_module_dir('tessocr')
print(module_dir)  # 输出: OCR模块目录路径
print(is_new)  # 输出: 是否为新创建的目录
```
### 字体增强识别 (FontEnhancementDetector)
简单来说就是项目在进行OCR识别前会检测输入文件夹有没有字体文件，在部分OCR API中，主动指定字体文件可以极大的增加图片识别准确率，然后往配置系统里存入四个变量：
```python
ConfigManager.set('USE_CUSTOM_FONT', use_custom_font) # 是否使用自定义字体(Bool)
ConfigManager.set('CUSTOM_FONT_PATH', font_path) # 自定义字体路径(Any)
ConfigManager.set('OCR_LANGUAGE', ocr_language) # OCR语言(Litarel)
ConfigManager.set('FIND_FONTS', found_fonts) # 找到的字体列表(list)
```
这些变量不是读配置文件读的，所以可以不经过转换直接使用，直接用ConfigManager.get()获取即可
```python
# 导入ConfigManager类
from config.config_manager import ConfigManager

use_custom_font = ConfigManager.get('USE_CUSTOM_FONT') # 获取是否使用自定义字体(Bool)
font_path = ConfigManager.get('CUSTOM_FONT_PATH') # 获取自定义字体路径(Any)
ocr_language = ConfigManager.get('OCR_LANGUAGE') # 获取OCR语言(Litarel)
found_fonts = ConfigManager.get('FIND_FONTS') # 获取找到的字体列表(list)
```
而FontEnhancementDetector确定字体增强的逻辑如下：
## FontEnhancementDetector初始化
首先他会加载`supported_fonts.json`：
```json
{
    "language_to_font": {
        "zh-cn": "zh-cn.ttf",
        "zh-tw": "zh-tw.ttf",
        "ja": "ja-jp.ttf",
        "en": "zh-cn.ttf"
    },
    "font_to_language": {
        "zh-cn.ttf": "zh-cn",
        "zh-tw.ttf": "zh-tw",
        "ja-jp.ttf": "ja",
        "en.ttf": "en"
    }    
}
```
这个表你可以自己改改，从而支持更多语言或字体
你可能会好奇为什么正着要写一遍，倒着也要写一遍，我只能说对象查询不用遍历，复杂度是O(1)，所以就这么用了
然后会再读取配置文件里的`OCR_LANGUAGE`项
```python
from config.config_manager import ConfigManager
original_ocr_language = ConfigManager.get('OCR_LANGUAGE', 'default')
```
`OCR_LANGUAGE`在默认配置文件里的定义是：
```python
'OCR_LANGUAGE': {
    'type': 'string',
    'options': ['zh-cn', 'zh-tw', 'en', 'ja-jp','default'],
    'default': 'default',
    'description_key': 'config_ocr_language',
    'required': False
}
```
所以:
## 指定OCR_LANGUAGE
当你指定了一个类似`'zh-cn'`的非默认`OCR_LANGUAGE`时，他会根据`"language_to_font"`的映射来找你的`process_dir`有没有`zh-cn.ttf`，没有的话，就会设置
```python
USE_CUSTOM_FONT=False
CUSTOM_FONT_PATH=None
OCR_LANGUAGE='zh-cn'
FIND_FONTS=[]
```
但如果你的`process_dir`里有`zh-cn.ttf`，他会自动设置为
```python
USE_CUSTOM_FONT=True
CUSTOM_FONT_PATH=<process_dir>/zh-cn.ttf
OCR_LANGUAGE='zh-cn'
FIND_FONTS=['zh-cn.ttf']
```
## 不指定OCR_LANGUAGE
当你的`OCR_LANGUAGE`为默认值`default`时，FontEnhancementDetector会先查看你当前使用的是什么语言，然后赋值：
```python
ocr_language = LangManager.get_lang('language_mapping')  # 想不到吧，语言文件里直接有个键来指示当前启用的是哪个语言文件
```
在使用`zh-cn.json`时，这个语言键的键值就是`zh-cn`，这样就又能根据`"language_to_font"`来找有没有字体了
但这时，如果没有找到字体文件，他不会直接设置`USE_CUSTOM_FONT=False`，而是查找`"font_to_language"`里记录的所有字体
如果有且仅有一个，那就设置`CUSTOM_FONT_PATH`为该字体的路径，设置`OCR_LANGUAGE`为`"font_to_language"`里对应的语言
但如果有多个字体文件的话，他就不会启用任何字体文件的字体加强了