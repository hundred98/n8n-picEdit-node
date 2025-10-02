from PIL import Image, ImageDraw, ImageFont
import os
import sys
import re
from typing import Tuple, Dict, List, Optional, Union, Any
import json


def clean_error_path(error_message):
    """清理错误信息中的路径编码问题"""
    try:
        message = str(error_message)
        message = message.replace('\\\\', '\\')
        path_pattern = r"'([A-Z]:[^']*?)'"
        
        def fix_path(match):
            path = match.group(1)
            try:
                fixed_path = os.path.normpath(path)
                return f"'{fixed_path}'"
            except:
                return match.group(0)
        
        message = re.sub(path_pattern, fix_path, message)
        return message
    except Exception:
        return str(error_message)


class CanvasElement:
    """基础元素类，所有画布元素的父类"""
    
    def __init__(self, position: Tuple[int, int], z_index: int = 0):
        self.position = position
        self.z_index = z_index
        
    def render(self, canvas: Image.Image, quiet: bool = False) -> None:
        raise NotImplementedError("子类必须实现render方法")


class TextElement(CanvasElement):
    """文字元素类"""
    
    CHINESE_FONTS = [
        "C:/Windows/Fonts/arialuni.ttf",
        "C:/Windows/Fonts/msyh.ttc",
        "C:/Windows/Fonts/simhei.ttf",
        "C:/Windows/Fonts/simsun.ttc",
        "Arial Unicode.ttf",
        "msyh.ttc",
        "simhei.ttf",
    ]
    
    def __init__(
        self, 
        position: Tuple[int, int], 
        text: str, 
        font_size: int = 24,
        font_name: Optional[str] = None,
        color: Union[str, Tuple[int, int, int]] = "black",
        rotation: float = 0,
        opacity: int = 255,
        alignment: str = "left",
        z_index: int = 0
    ):
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
        
        # 尝试加载字体
        if self.font_name:
            try:
                font = ImageFont.truetype(self.font_name, self.font_size)
            except IOError:
                if not quiet:
                    print(f"警告: 找不到字体 '{self.font_name}'，将尝试其他字体")
        
        # 如果没有指定字体或指定字体加载失败，尝试加载中文字体
        if font is None:
            for chinese_font in self.CHINESE_FONTS:
                try:
                    if os.path.exists(chinese_font):
                        font = ImageFont.truetype(chinese_font, self.font_size)
                        break
                except IOError:
                    continue
        
        # 如果所有字体都加载失败，使用系统默认字体
        if font is None:
            try:
                font = ImageFont.load_default()
            except Exception as e:
                if not quiet:
                    print(f"无法加载任何字体: {e}")
                return
        
        # 创建透明图层用于旋转
        txt_layer = Image.new('RGBA', canvas.size, (0, 0, 0, 0))
        txt_draw = ImageDraw.Draw(txt_layer)
        
        # 解析颜色 - 先定义基本颜色映射
        COLOR_NAMES = {
            'black': (0, 0, 0), 'white': (255, 255, 255), 'red': (255, 0, 0),
            'green': (0, 255, 0), 'blue': (0, 0, 255), 'yellow': (255, 255, 0),
            'cyan': (0, 255, 255), 'magenta': (255, 0, 255), 'orange': (255, 165, 0),
            'purple': (128, 0, 128), 'brown': (165, 42, 42), 'pink': (255, 192, 203),
            'gray': (128, 128, 128), 'grey': (128, 128, 128),
        }
        color = self.color
        if isinstance(color, str) and color in COLOR_NAMES:
            color = COLOR_NAMES[color]
        
        # 计算文本尺寸
        try:
            text_bbox = txt_draw.textbbox((0, 0), self.text, font=font)
            text_width = text_bbox[2] - text_bbox[0]
            text_height = text_bbox[3] - text_bbox[1]
        except:
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
            try:
                txt_layer = txt_layer.rotate(self.rotation, resample=Image.Resampling.BICUBIC, expand=1)
            except AttributeError:
                try:
                    txt_layer = txt_layer.rotate(self.rotation, resample=Image.BICUBIC, expand=1)
                except AttributeError:
                    txt_layer = txt_layer.rotate(self.rotation, expand=1)
        
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
            img = self._image.copy()
            
            # 缩放图片
            if self.scale != 1.0:
                new_size = (
                    int(self._image.width * self.scale),
                    int(self._image.height * self.scale)
                )
                try:
                    img = self._image.resize(new_size, Image.Resampling.LANCZOS)
                except AttributeError:
                    try:
                        img = self._image.resize(new_size, Image.ANTIALIAS)
                    except AttributeError:
                        img = self._image.resize(new_size)
            
            # 旋转图片
            if self.rotation != 0:
                try:
                    img = img.rotate(self.rotation, resample=Image.Resampling.BICUBIC, expand=True)
                except AttributeError:
                    try:
                        img = img.rotate(self.rotation, resample=Image.ANTIALIAS, expand=True)
                    except AttributeError:
                        img = img.rotate(self.rotation, expand=True)
            
            # 将图片粘贴到画布上
            canvas.paste(img, self.position, img)
            
    def _load_image(self, quiet: bool = False) -> None:
        """加载图片"""
        if self._image is None:
            normalized_path = os.path.normpath(self.image_path)
            try:
                # 使用安全的图片打开方法
                try:
                    from .path_utils import safe_image_open
                    self._image = safe_image_open(normalized_path).convert("RGBA")
                except (ImportError, ValueError):
                    try:
                        from path_utils import safe_image_open
                        self._image = safe_image_open(normalized_path).convert("RGBA")
                    except ImportError:
                        self._image = Image.open(normalized_path).convert("RGBA")
            except Exception as e:
                if not quiet:
                    try:
                        error_str = str(e)
                        while '\\\\' in error_str:
                            error_str = error_str.replace('\\\\', '\\')
                        error_msg = f"无法加载图片 '{normalized_path}': {error_str}"
                        print(error_msg, file=sys.stderr, flush=True)
                    except UnicodeEncodeError:
                        safe_path = normalized_path.encode('ascii', 'replace').decode('ascii')
                        safe_error = str(e).replace('\\\\', '\\').encode('ascii', 'replace').decode('ascii')
                        print(f"无法加载图片 '{safe_path}': {safe_error}", file=sys.stderr)
                self._image = Image.new("RGBA", (100, 100), (255, 0, 0, 128))


class Canvas:
    """画布类，管理所有元素并生成最终图像"""
    
    COLOR_NAMES = {
        'black': (0, 0, 0), 'white': (255, 255, 255), 'red': (255, 0, 0),
        'green': (0, 255, 0), 'blue': (0, 0, 255), 'yellow': (255, 255, 0),
        'cyan': (0, 255, 255), 'magenta': (255, 0, 255), 'orange': (255, 165, 0),
        'purple': (128, 0, 128), 'brown': (165, 42, 42), 'pink': (255, 192, 203),
        'gray': (128, 128, 128), 'grey': (128, 128, 128),
    }
    
    def __init__(
        self, 
        width: int, 
        height: int, 
        background_color: Union[str, Tuple[int, int, int]] = "white",
        background_image: Optional[str] = None
    ):
        self.width = width
        self.height = height
        self.background_color = self._parse_color(background_color)
        self.background_image = None
        self.elements: List[CanvasElement] = []
        
        if background_image:
            self._load_background_image(background_image)
    
    def _parse_color(self, color: Union[str, Tuple[int, int, int]]) -> Union[str, Tuple[int, int, int]]:
        if isinstance(color, str) and color in self.COLOR_NAMES:
            return self.COLOR_NAMES[color]
        return color
    
    def _load_background_image(self, image_path: str) -> None:
        """加载背景图片"""
        normalized_path = os.path.normpath(image_path)
        try:
            try:
                from .path_utils import safe_image_open
                self.background_image = safe_image_open(normalized_path).convert("RGBA")
            except (ImportError, ValueError):
                try:
                    from path_utils import safe_image_open
                    self.background_image = safe_image_open(normalized_path).convert("RGBA")
                except ImportError:
                    self.background_image = Image.open(normalized_path).convert("RGBA")
            self.background_image = self.background_image.resize((self.width, self.height))
        except Exception as e:
            try:
                error_str = str(e)
                while '\\\\' in error_str:
                    error_str = error_str.replace('\\\\', '\\')
                error_msg = f"无法加载背景图片 '{normalized_path}': {error_str}"
                print(error_msg, file=sys.stderr, flush=True)
            except UnicodeEncodeError:
                safe_path = normalized_path.encode('ascii', 'replace').decode('ascii')
                safe_error = str(e).replace('\\\\', '\\').encode('ascii', 'replace').decode('ascii')
                print(f"无法加载背景图片 '{safe_path}': {safe_error}", file=sys.stderr, flush=True)
            self.background_image = None
    
    def set_background_image(self, image_path: str, mode: str = "resize") -> None:
        """设置背景图片"""
        normalized_path = os.path.normpath(image_path)
        try:
            try:
                from .path_utils import safe_image_open
                img = safe_image_open(normalized_path).convert("RGBA")
            except (ImportError, ValueError):
                try:
                    from path_utils import safe_image_open
                    img = safe_image_open(normalized_path).convert("RGBA")
                except ImportError:
                    img = Image.open(normalized_path).convert("RGBA")
            
            if mode == "resize":
                try:
                    self.background_image = img.resize((self.width, self.height), Image.Resampling.LANCZOS)
                except AttributeError:
                    try:
                        self.background_image = img.resize((self.width, self.height), Image.ANTIALIAS)
                    except AttributeError:
                        self.background_image = img.resize((self.width, self.height))
            elif mode == "tile":
                tiled = Image.new("RGBA", (self.width, self.height))
                for y in range(0, self.height, img.height):
                    for x in range(0, self.width, img.width):
                        tiled.paste(img, (x, y))
                self.background_image = tiled
            elif mode == "center":
                self.background_image = Image.new("RGBA", (self.width, self.height), (0, 0, 0, 0))
                paste_x = (self.width - img.width) // 2
                paste_y = (self.height - img.height) // 2
                self.background_image.paste(img, (paste_x, paste_y), img)
                
        except Exception as e:
            try:
                error_str = str(e)
                while '\\\\' in error_str:
                    error_str = error_str.replace('\\\\', '\\')
                error_msg = f"无法设置背景图片 '{normalized_path}': {error_str}"
                print(error_msg, file=sys.stderr, flush=True)
            except UnicodeEncodeError:
                safe_path = normalized_path.encode('ascii', 'replace').decode('ascii')
                safe_error = str(e).replace('\\\\', '\\').encode('ascii', 'replace').decode('ascii')
                print(f"无法设置背景图片 '{safe_path}': {safe_error}", file=sys.stderr, flush=True)
            self.background_image = None
    
    def add_element(self, element: CanvasElement) -> None:
        self.elements.append(element)
        self.elements.sort(key=lambda e: e.z_index)
    
    def add_text(self, position: Tuple[int, int], text: str, **kwargs) -> TextElement:
        text_element = TextElement(position, text, **kwargs)
        self.add_element(text_element)
        return text_element
    
    def add_image(self, position: Tuple[int, int], image_path: str, **kwargs) -> ImageElement:
        image_element = ImageElement(position, image_path, **kwargs)
        self.add_element(image_element)
        return image_element
    
    def render(self, quiet: bool = False) -> Image.Image:
        if self.background_image:
            canvas = self.background_image.copy()
        else:
            canvas = Image.new("RGBA", (self.width, self.height), self.background_color)
        
        for element in self.elements:
            element.render(canvas, quiet)
            
        return canvas
    
    def save(self, file_path: str, quality: int = 95, quiet: bool = False) -> None:
        image = self.render(quiet)
        os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
        
        file_ext = os.path.splitext(file_path)[1].lower()
        if file_ext in ['.jpg', '.jpeg']:
            if image.mode == 'RGBA':
                background = Image.new('RGB', image.size, (255, 255, 255))
                background.paste(image, mask=image.split()[3])
                background.save(file_path, quality=quality)
            else:
                image.save(file_path, quality=quality)
        else:
            image.save(file_path)
            
        if not quiet:
            print(f"图片已保存到: {file_path}")