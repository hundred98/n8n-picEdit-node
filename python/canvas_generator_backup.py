from PIL import Image, ImageDraw, ImageFont
import os
import sys
import re
from typing import Tuple, Dict, List, Optional, Union, Any
import json


def clean_error_path(error_message):
    """清理错误信息中的路径编码问题"""
    try:
        # 将错误消息转换为字符串
        message = str(error_message)
        
        # 修复双反斜杠问题
        message = message.replace('\\\\', '\\')
        
        # 使用正则表达式查找并修复路径模式
        # 匹配类似 'E:\\\\内容\\\\素材\\\\' 的模式
        path_pattern = r"'([A-Z]:[^']*?)'"
        
        def fix_path(match):
            path = match.group(1)
            # 规范化路径
            try:
                fixed_path = os.path.normpath(path)
                return f"'{fixed_path}'"
            except:
                return match.group(0)
        
        # 应用路径修复
        message = re.sub(path_pattern, fix_path, message)
        
        return message
    except Exception:
        # 如果清理失败，返回原始消息
        return str(error_message)

class CanvasElement:
    """基础元素类，所有画布元素的父类"""
    
    def __init__(self, position: Tuple[int, int], z_index: int = 0):
        """
        初始化画布元素
        
        Args:
            position: 元素位置的(x, y)坐标
            z_index: 元素的层级，数值越大越靠前
        """
        self.position = position
        self.z_index = z_index
        
    def render(self, canvas: Image.Image, quiet: bool = False) -> None:
        """
        在画布上渲染元素
        
        Args:
            canvas: PIL Image对象，表示要渲染到的画布
            quiet: 是否静默模式，不打印日志
        """
        raise NotImplementedError("子类必须实现render方法")


class TextElement(CanvasElement):
    """文字元素类"""
    
    # 常见字体列表，按优先级排序，支持更多Unicode字符
    CHINESE_FONTS = [
        # Windows系统字体 - 支持中文字体且Unicode覆盖较全
        "C:/Windows/Fonts/arialuni.ttf",    # Arial Unicode MS（完整Unicode支持）
        "C:/Windows/Fonts/msyh.ttc",        # 微软雅黑
        "C:/Windows/Fonts/msyhbd.ttc",      # 微软雅黑粗体
        "C:/Windows/Fonts/simhei.ttf",      # 黑体
        "C:/Windows/Fonts/simsun.ttc",      # 宋体
        "C:/Windows/Fonts/simkai.ttf",      # 楷体
        "C:/Windows/Fonts/simfang.ttf",     # 仿宋
        "C:/Windows/Fonts/Dengb.ttf",       # 等线
        "C:/Windows/Fonts/STZHONGS.TTF",    # 华文中宋
        
        # Windows系统字体 - 支持更多Unicode字符
        "C:/Windows/Fonts/Arial.ttf",       # Arial（支持较多Unicode）
        "C:/Windows/Fonts/Times.ttf",       # Times New Roman
        "C:/Windows/Fonts/Cambria.ttf",     # Cambria
        "C:/Windows/Fonts/Georgia.ttf",     # Georgia
        
        # macOS系统字体
        "/System/Library/Fonts/Arial Unicode.ttf",          # Arial Unicode
        "/System/Library/Fonts/PingFang.ttc",               # 苹方
        "/System/Library/Fonts/Helvetica.ttc",              # Helvetica
        "/System/Library/Fonts/STHeiti Light.ttc",          # 华文黑体
        "/System/Library/Fonts/STHeiti Medium.ttc",         # 华文黑体
        "/System/Library/Fonts/Songti.ttc",                 # 宋体
        "/System/Library/Fonts/Kaiti.ttc",                  # 楷体
        
        # Linux系统字体
        "/usr/share/fonts/truetype/noto/NotoSansCJK.ttc",   # Noto Sans CJK（Google的全字符支持字体）
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",  # DejaVu Sans（良好Unicode支持）
        "/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf",  # Droid Sans Fallback
        "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",   # 文泉驿微米黑
        "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc",     # 文泉驿正黑
        
        # 其他可能的字体路径
        "Arial Unicode.ttf",
        "arialuni.ttf",
        "msyh.ttc",
        "simhei.ttf",
        "simsun.ttc",
        "DoulosSIL-Regular.ttf",
        "/usr/share/fonts/truetype/doulos/DoulosSIL-Regular.ttf",
        "/Library/Fonts/DoulosSIL-Regular.ttf",
    ]
    
    def __init__(
        self, 
        position: Tuple[int, int], 
        text: str, 
        font_size: int = 24,
        font_name: Optional[str] = None,  # 默认为None，会自动查找合适的字体
        color: Union[str, Tuple[int, int, int]] = "black",
        rotation: float = 0,
        opacity: int = 255,
        alignment: str = "left",
        z_index: int = 0
    ):
        """
        初始化文字元素
        
        Args:
            position: 文字位置的(x, y)坐标
            text: 要显示的文字内容
            font_size: 字体大小
            font_name: 字体名称或路径
            color: 字体颜色，可以是颜色名称或RGB元组
            rotation: 旋转角度（度）
            opacity: 不透明度 (0-255)
            alignment: 对齐方式 ('left', 'center', 'right')
            z_index: 层级
        """
        super().__init__(position, z_index)
        self.text = text
        self.font_size = font_size
        self.font_name = font_name
        self.color = color
        self.rotation = rotation
        self.opacity = opacity
        self.alignment = alignment
        
    def render(self, canvas: Image.Image, quiet: bool = False) -> None:
        """在画布上渲染文字"""
        font = None
        font_name_used = None
        
        # 如果指定了字体，尝试加载
        if self.font_name:
            try:
                # 首先尝试直接加载（可能是完整路径或系统字体）
                font = ImageFont.truetype(self.font_name, self.font_size)
                font_name_used = self.font_name
            except IOError:
                # 如果失败，尝试在项目目录中查找
                try:
                    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                    project_font_path = os.path.join(project_root, self.font_name)
                    if os.path.exists(project_font_path):
                        font = ImageFont.truetype(project_font_path, self.font_size)
                        font_name_used = project_font_path
                    else:
                        # 特殊处理DoulosSIL-Regular.ttf
                        doulos_font_path = os.path.join(project_root, "DoulosSIL-Regular.ttf")
                        if os.path.exists(doulos_font_path):
                            font = ImageFont.truetype(doulos_font_path, self.font_size)
                            font_name_used = doulos_font_path
                        else:
                            raise IOError(f"Font file not found: {self.font_name}")
                except IOError:
                    if not quiet:
                        print(f"警告: 找不到字体 '{self.font_name}'，将尝试其他字体")
        
        # 如果没有指定字体或指定字体加载失败，尝试加载中文字体
        if font is None:
            for chinese_font in self.CHINESE_FONTS:
                try:
                    # 如果是相对路径，尝试在项目目录中查找
                    if not os.path.isabs(chinese_font):
                        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                        project_font_path = os.path.join(project_root, chinese_font)
                        if os.path.exists(project_font_path):
                            font = ImageFont.truetype(project_font_path, self.font_size)
                            font_name_used = project_font_path
                        else:
                            # 尝试作为系统字体加载
                            font = ImageFont.truetype(chinese_font, self.font_size)
                            font_name_used = chinese_font
                    else:
                        # 绝对路径，直接尝试加载
                        if os.path.exists(chinese_font):
                            font = ImageFont.truetype(chinese_font, self.font_size)
                            font_name_used = chinese_font
                        else:
                            continue
                    if not quiet:
                        print(f"使用字体: {font_name_used}")
                    break
                except IOError:
                    continue
        
        # 如果所有字体都加载失败，尝试使用系统字体
        if font is None:
            try:
                # 尝试使用系统默认字体
                font = ImageFont.load_default()
                font_name_used = "default"
                if not quiet:
                    print("使用系统默认字体")
            except Exception as e:
                if not quiet:
                    print(f"无法加载任何字体: {e}")
                return
        
        # 创建透明图层用于旋转
        txt_layer = Image.new('RGBA', canvas.size, (0, 0, 0, 0))
        txt_draw = ImageDraw.Draw(txt_layer)
        
        # 解析颜色
        # 注意：这里我们假设父级Canvas对象存在，实际使用中需要确保这一点
        # 或者将颜色解析方法移到全局工具函数中
        color = self.color
        if isinstance(color, str) and color in Canvas.COLOR_NAMES:
            color = Canvas.COLOR_NAMES[color]
        
        # 计算文本尺寸
        try:
            # 新版本Pillow使用textbbox
            text_bbox = txt_draw.textbbox((0, 0), self.text, font=font)
            text_width = text_bbox[2] - text_bbox[0]
            text_height = text_bbox[3] - text_bbox[1]
        except AttributeError:
            try:
                # 旧版本Pillow使用textsize
                text_width, text_height = txt_draw.textsize(self.text, font=font)
            except:
                # 最后备选方案
                text_width, text_height = (len(self.text) * self.font_size, self.font_size)
        except:
            # 其他异常情况
            text_width, text_height = (len(self.text) * self.font_size, self.font_size)
        
        # 根据对齐方式调整位置
        x, y = self.position
        if self.alignment == "center":
            x -= text_width // 2
        elif self.alignment == "right":
            x -= text_width
            
        # 绘制文本
        txt_draw.text((x, y), self.text, font=font, fill=color)
        
        # 如果需要旋转
        if self.rotation != 0:
            # 兼容不同版本的Pillow
            try:
                txt_layer = txt_layer.rotate(self.rotation, resample=Image.Resampling.BICUBIC, expand=1)
            except AttributeError:
                # 旧版本Pillow
                txt_layer = txt_layer.rotate(self.rotation, resample=Image.BICUBIC, expand=1)
        
        # 如果需要调整透明度
        if self.opacity < 255:
            if txt_layer.mode != 'RGBA':
                txt_layer = txt_layer.convert('RGBA')
            try:
                txt_layer.putalpha(txt_layer.getchannel('A').point(lambda x: x * self.opacity // 255))
            except:
                # 备选方案
                txt_layer.putalpha(Image.eval(txt_layer.getchannel('A'), lambda a: a * self.opacity // 255))
        
        # 将文本图层合并到画布
        canvas.paste(txt_layer, (0, 0), txt_layer)


class ImageElement(CanvasElement):
    """图片元素类"""
    
    def __init__(
        self, 
        position: Tuple[int, int], 
        image_path: str,
        scale: float = 1.0,
        rotation: float = 0,
        opacity: int = 255,
        z_index: int = 0
    ):
        """
        初始化图片元素
        
        Args:
            position: 图片位置的(x, y)坐标
            image_path: 图片文件路径
            scale: 缩放比例
            rotation: 旋转角度（度）
            opacity: 不透明度 (0-255)
            z_index: 层级
        """
        super().__init__(position, z_index)
        self.image_path = image_path
        self.scale = scale
        self.rotation = rotation
        self.opacity = opacity
        self._image = None
        
    def render(self, canvas: Image.Image, quiet: bool = False) -> None:
        """在画布上渲染图片"""
        self._load_image(quiet)
        if self._image:
            # 缩放图片
            if self.scale != 1.0:
                new_size = (
                    int(self._image.width * self.scale),
                    int(self._image.height * self.scale)
                )
                # 兼容不同版本的Pillow
                try:
                    img = self._image.resize(new_size, Image.Resampling.LANCZOS)
                except AttributeError:
                    # 旧版本Pillow
                    img = self._image.resize(new_size, Image.ANTIALIAS)
            else:
                img = self._image.copy()
            
            # 旋转图片
            if self.rotation != 0:
                # 兼容不同版本的Pillow
                try:
                    img = img.rotate(self.rotation, resample=Image.Resampling.BICUBIC, expand=True)
                except AttributeError:
                    # 旧版本Pillow
                    img = img.rotate(self.rotation, resample=Image.ANTIALIAS, expand=True)
            
            # 调整透明度
            if self.opacity < 255:
                img.putalpha(Image.eval(img.getchannel('A'), lambda a: a * self.opacity // 255))
            
            # 将图片粘贴到画布上
            canvas.paste(img, self.position, img)
            
    def _load_image(self, quiet: bool = False) -> None:
        """加载图片"""
        if self._image is None:
            # 预处理路径，避免双反斜杠问题
            normalized_path = os.path.normpath(self.image_path)
            try:
                # 使用安全的图片打开方法
                try:
                    from path_utils import safe_image_open
                    self._image = safe_image_open(normalized_path).convert("RGBA")
                except ImportError:
                    # 如果导入失败，使用标准方法
                    self._image = Image.open(normalized_path).convert("RGBA")
            except Exception as e:
                if not quiet:
                    # 安全地输出中文路径错误信息，清理错误消息中的编码问题
                    try:
                        # 直接处理异常消息中的路径编码问题
                        error_str = str(e)
                        # 修复异常消息中的双反斜杠问题 - 使用更强力的替换
                        while '\\\\' in error_str:
                            error_str = error_str.replace('\\\\', '\\')
                        
                        error_msg = f"无法加载图片 '{normalized_path}': {error_str}"
                        print(error_msg, file=sys.stderr, flush=True)
                    except UnicodeEncodeError:
                        # 如果仍然有编码问题，使用ASCII安全的方式
                        safe_path = normalized_path.encode('ascii', 'replace').decode('ascii')
                        safe_error = str(e).replace('\\\\', '\\').encode('ascii', 'replace').decode('ascii')
                        print(f"无法加载图片 '{safe_path}': {safe_error}", file=sys.stderr)
                # 创建一个小的红色占位图
                self._image = Image.new("RGBA", (100, 100), (255, 0, 0, 128))


class Canvas:
    """画布类，管理所有元素并生成最终图像"""
    
    # 支持的颜色名称映射
    COLOR_NAMES = {
        # 标准颜色
        'black': (0, 0, 0),
        'white': (255, 255, 255),
        'red': (255, 0, 0),
        'green': (0, 255, 0),
        'blue': (0, 0, 255),
        'yellow': (255, 255, 0),
        'cyan': (0, 255, 255),
        'magenta': (255, 0, 255),
        'orange': (255, 165, 0),
        'purple': (128, 0, 128),
        'brown': (165, 42, 42),
        'pink': (255, 192, 203),
        'gray': (128, 128, 128),
        'grey': (128, 128, 128),
        
        # 深色变体
        'darkred': (139, 0, 0),
        'darkgreen': (0, 100, 0),
        'darkblue': (0, 0, 139),
        'darkcyan': (0, 139, 139),
        'darkmagenta': (139, 0, 139),
        'darkyellow': (139, 139, 0),
        'darkorange': (255, 140, 0),
        'darkpurple': (75, 0, 130),
        'darkpink': (199, 21, 133),
        'darkgray': (169, 169, 169),
        'darkgrey': (169, 169, 169),
        
        # 浅色变体
        'lightred': (255, 128, 128),
        'lightgreen': (144, 238, 144),
        'lightblue': (173, 216, 230),
        'lightcyan': (224, 255, 255),
        'lightmagenta': (255, 128, 255),
        'lightyellow': (255, 255, 224),
        'lightorange': (255, 218, 185),
        'lightpurple': (230, 230, 250),
        'lightpink': (255, 182, 193),
        'lightgray': (211, 211, 211),
        'lightgrey': (211, 211, 211),
    }
    
    def __init__(
        self, 
        width: int, 
        height: int, 
        background_color: Union[str, Tuple[int, int, int]] = "white",
        background_image: Optional[str] = None
    ):
        """
        初始化画布
        
        Args:
            width: 画布宽度
            height: 画布高度
            background_color: 背景颜色
            background_image: 背景图片路径（可选）
        """
        self.width = width
        self.height = height
        self.background_color = self._parse_color(background_color)
        self.background_image = None
        self.elements: List[CanvasElement] = []
        
        # 如果提供了背景图片路径，则加载
        if background_image:
            self._load_background_image(background_image)
    
    def _parse_color(self, color: Union[str, Tuple[int, int, int]]) -> Union[str, Tuple[int, int, int]]:
        """
        解析颜色值
        
        Args:
            color: 颜色名称或RGB元组
            
        Returns:
            解析后的颜色值
        """
        if isinstance(color, str) and color in self.COLOR_NAMES:
            return self.COLOR_NAMES[color]
        return color
    
    def _load_background_image(self, image_path: str) -> None:
        """加载背景图片"""
        # 预处理路径，避免双反斜杠问题
        normalized_path = os.path.normpath(image_path)
        try:
            # 使用安全的图片打开方法
            try:
                from path_utils import safe_image_open
                self.background_image = safe_image_open(normalized_path).convert("RGBA")
            except ImportError:
                # 如果导入失败，使用标准方法
                self.background_image = Image.open(normalized_path).convert("RGBA")
            # 调整背景图片大小以适应画布
            self.background_image = self.background_image.resize((self.width, self.height))
        except Exception as e:
            # 安全地输出中文路径错误信息，清理错误消息中的编码问题
            try:
                # 直接处理异常消息中的路径编码问题
                error_str = str(e)
                # 修复异常消息中的双反斜杠问题 - 使用更强力的替换
                while '\\\\' in error_str:
                    error_str = error_str.replace('\\\\', '\\')
                
                error_msg = f"无法加载背景图片 '{normalized_path}': {error_str}"
                print(error_msg, file=sys.stderr, flush=True)
            except UnicodeEncodeError:
                # 如果仍然有编码问题，使用ASCII安全的方式
                safe_path = normalized_path.encode('ascii', 'replace').decode('ascii')
                safe_error = str(e).replace('\\\\', '\\').encode('ascii', 'replace').decode('ascii')
                print(f"无法加载背景图片 '{safe_path}': {safe_error}", file=sys.stderr, flush=True)
            self.background_image = None
    
    def set_background_image(self, image_path: str, mode: str = "resize") -> None:
        """
        设置背景图片
        
        Args:
            image_path: 图片路径
            mode: 背景图片模式，可选值:
                - "resize": 调整图片大小以适应画布
                - "tile": 平铺图片
                - "center": 居中显示图片
        """
        # 预处理路径，避免双反斜杠问题
        normalized_path = os.path.normpath(image_path)
        try:
            # 使用安全的图片打开方法
            try:
                from path_utils import safe_image_open
                img = safe_image_open(normalized_path).convert("RGBA")
            except ImportError:
                # 如果导入失败，使用标准方法
=======
    def set_background_image(self, image_path: str, mode: str = "resize") -> None:
        """
        设置背景图片
        
        Args:
            image_path: 图片路径
            mode: 背景图片模式，可选值:
                - "resize": 调整图片大小以适应画布
                - "tile": 平铺图片
                - "center": 居中显示图片
        """
        # 预处理路径，避免双反斜杠问题
        normalized_path = os.path.normpath(image_path)
        try:
            # 使用安全的图片打开方法
            try:
                from path_utils import safe_image_open
                img = safe_image_open(normalized_path).convert("RGBA")
            except ImportError:
                # 如果导入失败，使用标准方法
=======
    def set_background_image(self, image_path: str, mode: str = "resize") -> None:
        """
        设置背景图片
        
        Args:
            image_path: 图片路径
            mode: 背景图片模式，可选值:
                - "resize": 调整图片大小以适应画布
                - "tile": 平铺图片
                - "center": 居中显示图片
        """
        # 预处理路径，避免双反斜杠问题
        normalized_path = os.path.normpath(image_path)
        try:
            # 使用安全的图片打开方法
            try:
                from path_utils import safe_image_open
                img = safe_image_open(normalized_path).convert("RGBA")
            except ImportError:
                # 如果导入失败，使用标准方法
                img = Image.open(normalized_path).convert("RGBA")


class Canvas:
    """画布类，管理所有元素并生成最终图像"""
    
    # 支持的颜色名称映射
    COLOR_NAMES = {
        # 标准颜色
        'black': (0, 0, 0),
        'white': (255, 255, 255),
        'red': (255, 0, 0),
        'green': (0, 255, 0),
        'blue': (0, 0, 255),
        'yellow': (255, 255, 0),
        'cyan': (0, 255, 255),
        'magenta': (255, 0, 255),
        'orange': (255, 165, 0),
        'purple': (128, 0, 128),
        'brown': (165, 42, 42),
        'pink': (255, 192, 203),
        'gray': (128, 128, 128),
        'grey': (128, 128, 128),
        
        # 深色变体
        'darkred': (139, 0, 0),
        'darkgreen': (0, 100, 0),
        'darkblue': (0, 0, 139),
        'darkcyan': (0, 139, 139),
        'darkmagenta': (139, 0, 139),
        'darkyellow': (139, 139, 0),
        'darkorange': (255, 140, 0),
        'darkpurple': (75, 0, 130),
        'darkpink': (199, 21, 133),
        'darkgray': (169, 169, 169),
        'darkgrey': (169, 169, 169),
        
        # 浅色变体
        'lightred': (255, 128, 128),
        'lightgreen': (144, 238, 144),
        'lightblue': (173, 216, 230),
        'lightcyan': (224, 255, 255),
        'lightmagenta': (255, 128, 255),
        'lightyellow': (255, 255, 224),
        'lightorange': (255, 218, 185),
        'lightpurple': (230, 230, 250),
        'lightpink': (255, 182, 193),
        'lightgray': (211, 211, 211),
        'lightgrey': (211, 211, 211),
    }
    
    def __init__(
        self, 
        width: int, 
        height: int, 
        background_color: Union[str, Tuple[int, int, int]] = "white",
        background_image: Optional[str] = None
    ):
        """
        初始化画布
        
        Args:
            width: 画布宽度
            height: 画布高度
            background_color: 背景颜色
            background_image: 背景图片路径（可选）
        """
        self.width = width
        self.height = height
        self.background_color = self._parse_color(background_color)
        self.background_image = None
        self.elements: List[CanvasElement] = []
        
        # 如果提供了背景图片路径，则加载
        if background_image:
            self._load_background_image(background_image)
    
    def _parse_color(self, color: Union[str, Tuple[int, int, int]]) -> Union[str, Tuple[int, int, int]]:
        """
        解析颜色值
        
        Args:
            color: 颜色名称或RGB元组
            
        Returns:
            解析后的颜色值
        """
        if isinstance(color, str) and color in self.COLOR_NAMES:
            return self.COLOR_NAMES[color]
        return color
    
    def _load_background_image(self, image_path: str) -> None:
        """加载背景图片"""
        # 预处理路径，避免双反斜杠问题
        normalized_path = os.path.normpath(image_path)
        try:
            # 使用安全的图片打开方法
            try:
                from path_utils import safe_image_open
                self.background_image = safe_image_open(normalized_path).convert("RGBA")
            except ImportError:
                # 如果导入失败，使用标准方法
                self.background_image = Image.open(normalized_path).convert("RGBA")
            # 调整背景图片大小以适应画布
            self.background_image = self.background_image.resize((self.width, self.height))
        except Exception as e:
            # 安全地输出中文路径错误信息，清理错误消息中的编码问题
            try:
                # 直接处理异常消息中的路径编码问题
                error_str = str(e)
                # 修复异常消息中的双反斜杠问题 - 使用更强力的替换
                while '\\\\' in error_str:
                    error_str = error_str.replace('\\\\', '\\')
                
                error_msg = f"无法加载背景图片 '{normalized_path}': {error_str}"
                print(error_msg, file=sys.stderr, flush=True)
            except UnicodeEncodeError:
                # 如果仍然有编码问题，使用ASCII安全的方式
                safe_path = normalized_path.encode('ascii', 'replace').decode('ascii')
                safe_error = str(e).replace('\\\\', '\\').encode('ascii', 'replace').decode('ascii')
                print(f"无法加载背景图片 '{safe_path}': {safe_error}", file=sys.stderr, flush=True)
            self.background_image = None
    
    def set_background_image(self, image_path: str, mode: str = "resize") -> None:
        """
        设置背景图片
        
        Args:
            image_path: 图片路径
            mode: 背景图片模式，可选值:
                - "resize": 调整图片大小以适应画布
                - "tile": 平铺图片
                - "center": 居中显示图片
        """
        try:
            # 使用安全的图片打开方法
            try:
                from path_utils import safe_image_open
            except ImportError:
                # 如果导入失败，使用标准方法
                safe_image_open = Image.open
            img = safe_image_open(image_path).convert("RGBA")
            
            if mode == "resize":
                # 兼容不同版本的Pillow
                try:
                    self.background_image = img.resize((self.width, self.height), Image.Resampling.LANCZOS)
                except AttributeError:
                    # 旧版本Pillow
                    self.background_image = img.resize((self.width, self.height), Image.ANTIALIAS)
            elif mode == "tile":
                # 创建平铺背景
                tiled = Image.new("RGBA", (self.width, self.height))
                for y in range(0, self.height, img.height):
                    for x in range(0, self.width, img.width):
                        tiled.paste(img, (x, y))
                self.background_image = tiled
            elif mode == "center":
                # 居中显示
                self.background_image = Image.new("RGBA", (self.width, self.height), (0, 0, 0, 0))
                paste_x = (self.width - img.width) // 2
                paste_y = (self.height - img.height) // 2
                self.background_image.paste(img, (paste_x, paste_y), img)
            else:
                print(f"不支持的背景模式: {mode}，使用resize模式")
                # 兼容不同版本的Pillow
                try:
                    self.background_image = img.resize((self.width, self.height), Image.Resampling.LANCZOS)
                except AttributeError:
                    # 旧版本Pillow
                    self.background_image = img.resize((self.width, self.height), Image.ANTIALIAS)
                
        except Exception as e:
            # 安全地输出中文路径错误信息
            try:
                # 处理异常消息中的双反斜杠问题
                error_str = str(e)
                while '\\\\' in error_str:
                    error_str = error_str.replace('\\\\', '\\')
                error_msg = f"无法加载背景图片 '{normalized_path}': {error_str}"
                print(error_msg, file=sys.stderr)
            except UnicodeEncodeError:
                # 如果仍然有编码问题，使用ASCII安全的方式
                safe_path = normalized_path.encode('ascii', 'replace').decode('ascii')
                safe_error = str(e).replace('\\\\', '\\')
                print(f"无法加载背景图片 '{safe_path}': {safe_error}", file=sys.stderr)
            self.background_image = None
    
    def add_element(self, element: CanvasElement) -> None:
        """
        添加元素到画布
        
        Args:
            element: 要添加的画布元素
        """
        self.elements.append(element)
        # 按z-index排序元素，确保正确的渲染顺序
        self.elements.sort(key=lambda e: e.z_index)
    
    def add_text(self, position: Tuple[int, int], text: str, **kwargs) -> TextElement:
        """
        添加文本元素到画布
        
        Args:
            position: 文本位置
            text: 文本内容
            **kwargs: 传递给TextElement的其他参数
            
        Returns:
            添加的TextElement对象
        """
        text_element = TextElement(position, text, **kwargs)
        self.add_element(text_element)
        return text_element
    
    def add_image(self, position: Tuple[int, int], image_path: str, **kwargs) -> ImageElement:
        """
        添加图片元素到画布
        
        Args:
            position: 图片位置
            image_path: 图片路径
            **kwargs: 传递给ImageElement的其他参数
            
        Returns:
            添加的ImageElement对象
        """
        image_element = ImageElement(position, image_path, **kwargs)
        self.add_element(image_element)
        return image_element
    
    def render(self, quiet: bool = False) -> Image.Image:
        """
        渲染画布及其所有元素
        
        Returns:
            渲染后的PIL Image对象
        """
        # 创建画布
        if self.background_image:
            canvas = self.background_image.copy()
        else:
            canvas = Image.new("RGBA", (self.width, self.height), self.background_color)
        
        # 渲染所有元素
        for element in self.elements:
            element.render(canvas, quiet)
            
        return canvas
    
    def save(self, file_path: str, quality: int = 95, quiet: bool = False) -> None:
        """
        保存画布为图片文件
        
        Args:
            file_path: 保存路径
            quality: JPEG质量 (1-100)
            quiet: 是否静默模式，不打印日志
        """
        image = self.render(quiet)
        
        # 确保目录存在
        os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
        
        # 根据文件扩展名保存
        file_ext = os.path.splitext(file_path)[1].lower()
        if file_ext == '.jpg' or file_ext == '.jpeg':
            # JPEG不支持透明度，需要用白色背景
            if image.mode == 'RGBA':
                background = Image.new('RGB', image.size, (255, 255, 255))
                background.paste(image, mask=image.split()[3])  # 使用alpha通道作为mask
                background.save(file_path, quality=quality)
            else:
                image.save(file_path, quality=quality)
        else:
            # 其他格式如PNG，保持透明度
            image.save(file_path)
            
        if not quiet:
            print(f"图片已保存到: {file_path}")


class Template:
    """模板类，用于管理预定义的画布模板"""
    
    def __init__(self, name: str, width: int, height: int, background: Union[str, Tuple[int, int, int], Dict[str, Any]] = "white"):
        """
        初始化模板
        
        Args:
            name: 模板名称
            width: 画布宽度
            height: 画布高度
            background: 背景颜色或背景图片配置
        """
        self.name = name
        self.width = width
        self.height = height
        self.background = background
        self.elements_config = []
        
    def add_text_config(self, position: Tuple[int, int], text: str, **kwargs) -> None:
        """
        添加文本配置到模板
        
        Args:
            position: 文本位置
            text: 默认文本
            **kwargs: 文本属性
        """
        config = {
            "type": "text",
            "position": position,
            "text": text,
            **kwargs
        }
        self.elements_config.append(config)
        
    def add_image_config(self, position: Tuple[int, int], image_path: str, **kwargs) -> None:
        """
        添加图片配置到模板
        
        Args:
            position: 图片位置
            image_path: 默认图片路径
            **kwargs: 图片属性
        """
        config = {
            "type": "image",
            "position": position,
            "image_path": image_path,
            **kwargs
        }
        self.elements_config.append(config)
        
    def apply_to_canvas(self, canvas: Optional[Canvas] = None) -> Canvas:
        """
        将模板应用到画布
        
        Args:
            canvas: 现有画布，如果为None则创建新画布
            
        Returns:
            应用模板后的画布
        """
        if canvas is None:
            canvas = Canvas(self.width, self.height)
        
        # 设置背景
        if isinstance(self.background, dict):
            # 如果背景是字典配置，假设它包含图片路径
            canvas.set_background_image(
                self.background.get("image_path", ""),
                self.background.get("mode", "resize")
            )
        else:
            # 否则假设它是颜色
            canvas.background_color = self.background
            canvas.background_image = None
            
        # 添加元素
        for config in self.elements_config:
            if config["type"] == "text":
                text = config.pop("text")
                position = config.pop("position")
                config.pop("type")
                canvas.add_text(position, text, **config)
            elif config["type"] == "image":
                image_path = config.pop("image_path")
                position = config.pop("position")
                config.pop("type")
                canvas.add_image(position, image_path, **config)
                
        return canvas
    
    def save_to_json(self, file_path: str) -> None:
        """
        将模板保存为JSON文件
        
        Args:
            file_path: 保存路径
        """
        template_data = {
            "name": self.name,
            "width": self.width,
            "height": self.height,
            "background": self.background,
            "elements": self.elements_config
        }
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(template_data, f, indent=2, ensure_ascii=False)
            
        print(f"模板已保存到: {file_path}")
    
    @classmethod
    def load_from_json(cls, file_path: str) -> 'Template':
        """
        从JSON文件加载模板
        
        Args:
            file_path: JSON文件路径
            
        Returns:
            加载的模板对象
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        template = cls(
            name=data.get("name", "Unnamed Template"),
            width=data.get("width", 800),
            height=data.get("height", 600),
            background=data.get("background", "white")
        )
        
        for element_config in data.get("elements", []):
            if element_config.get("type") == "text":
                template.add_text_config(
                    element_config.get("position", (0, 0)),
                    element_config.get("text", ""),
                    **{k: v for k, v in element_config.items() 
                       if k not in ["type", "position", "text"]}
                )
            elif element_config.get("type") == "image":
                template.add_image_config(
                    element_config.get("position", (0, 0)),
                    element_config.get("image_path", ""),
                    **{k: v for k, v in element_config.items() 
                       if k not in ["type", "position", "image_path"]}
                )
                
        return template


class TemplateManager:
    """模板管理器，用于管理多个模板"""
    
    def __init__(self, templates_dir: str = "templates", quiet: bool = False):
        """
        初始化模板管理器
        
        Args:
            templates_dir: 模板目录
            quiet: 是否静默模式，不打印日志
        """
        self.templates_dir = templates_dir
        self.templates = {}
        self.quiet = quiet
        
        # 确保模板目录存在
        os.makedirs(templates_dir, exist_ok=True)
        
        # 加载现有模板
        self.load_templates()
        
    def load_templates(self) -> None:
        """加载模板目录中的所有模板"""
        if not os.path.exists(self.templates_dir):
            return
            
        for filename in os.listdir(self.templates_dir):
            if filename.endswith('.json'):
                try:
                    file_path = os.path.join(self.templates_dir, filename)
                    template = Template.load_from_json(file_path)
                    self.templates[template.name] = template
                except Exception as e:
                    if not self.quiet:
                        print(f"加载模板 '{filename}' 失败: {e}")
    
    def add_template(self, template: Template) -> None:
        """
        添加模板
        
        Args:
            template: 要添加的模板
        """
        self.templates[template.name] = template
        
        # 保存模板到文件
        file_path = os.path.join(self.templates_dir, f"{template.name}.json")
        template.save_to_json(file_path)
        
    def get_template(self, name: str) -> Optional[Template]:
        """
        获取指定名称的模板
        
        Args:
            name: 模板名称
            
        Returns:
            模板对象，如果不存在则返回None
        """
        return self.templates.get(name)
    
    def list_templates(self) -> List[str]:
        """
        列出所有可用的模板名称
        
        Returns:
            模板名称列表
        """
        return list(self.templates.keys())