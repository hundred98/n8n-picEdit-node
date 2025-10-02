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
                from path_utils import safe_image_open
                img = safe_image_open(normalized_path).convert("RGBA")
            except ImportError:
                img = Image.open(normalized_path).convert("RGBA")
            
            if mode == "resize":
                try:
                    self.background_image = img.resize((self.width, self.height), Image.Resampling.LANCZOS)
                except AttributeError:
                    self.background_image = img.resize((self.width, self.height), Image.ANTIALIAS)
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