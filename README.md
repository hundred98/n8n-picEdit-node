# 自定义画布生成器

 这是一个用Python实现的自定义画布生成工具，可以在画布上放置文字和图片。

## 功能特点

- 创建自定义尺寸的画布
- 添加文字元素，支持自定义字体、大小、颜色、对齐方式、旋转角度和透明度等
- 添加图片元素，支持缩放、旋转、透明度调整
- 命令行工具，方便快速使用

## 安装依赖

本工具依赖于Python的Pillow库，请先安装依赖：

```bash
pip install pillow
```

## 使用方法

### 1. 使用示例脚本

运行示例脚本可以快速了解基本功能：

```bash
python photo_test.py
python doulos_example.py
```

这将生成示例图片：
- `output_basic.png` - 基本画布示例
- `output_with_images.png` - 包含图片叠加的示例

### 2. 使用命令行工具

#### 创建画布

```bash
python canvas_cli.py create --width 800 --height 600 --background "lightblue" --output "my_canvas.png"
```

使用配置文件创建画布：

```bash
# 先创建示例配置文件
python canvas_cli.py create-example-config --output my_config.json

# 编辑配置文件，然后使用它创建画布
python canvas_cli.py create --config my_config.json --output "my_canvas.png"
```

### 3. 在Python代码中使用

```python
from canvas_generator import Canvas

# 创建画布
canvas = Canvas(800, 600, background_color="white")

# 添加文字
canvas.add_text(
    position=(400, 100),
    text="Hello, World!",
    font_size=48,
    color="blue",
    alignment="center",
    rotation=0,      # 旋转角度（度）
    opacity=255      # 透明度（0-255，0为完全透明）
)

# 添加图片
canvas.add_image(
    position=(300, 200),
    image_path="my_image.jpg",
    scale=0.5
)

# 保存画布
canvas.save("output.png")
```

## 配置文件格式

配置文件使用JSON格式，包含文字和图片元素的定义：

```json
{
  "texts": [
    {
      "position": [400, 100],
      "text": "示例标题",
      "font_size": 48,
      "color": "navy",
      "alignment": "center"
    },
    {
      "position": [400, 200],
      "text": "这是一个示例说明文本",
      "font_size": 24,
      "color": "black",
      "alignment": "center"
    }
  ],
  "images": [
    {
      "position": [300, 250],
      "image_path": "example_image.jpg",
      "scale": 0.5,
      "rotation": 0,
      "opacity": 255
    }
  ]
}
```

## 高级用法

### 自定义字体

要使用自定义字体，只需指定字体文件的路径：

```python
canvas.add_text(
    position=(400, 100),
    text="自定义字体",
    font_size=48,
    font_name="path/to/font.ttf",
    color="black",
    alignment="center",
    rotation=0,      # 旋转角度（度）
    opacity=255      # 透明度（0-255，0为完全透明）
)
```

### 图片透明度和旋转

```python
canvas.add_image(
    position=(300, 200),
    image_path="my_image.jpg",
    scale=0.5,
    rotation=45,  # 旋转45度
    opacity=128   # 半透明
)
```

### 层级管理

通过`z_index`参数控制元素的层级顺序：

```python
# 这个元素会显示在z_index较小的元素上面
canvas.add_text(
    position=(400, 300),
    text="前景文字",
    font_size=36,
    color="red",
    z_index=10  # 较高的z_index
)

# 这个元素会显示在z_index较大的元素下面
canvas.add_text(
    position=(400, 300),
    text="背景文字",
    font_size=48,
    color="gray",
    z_index=5  # 较低的z_index
)
```

## 注意事项

- 文字渲染需要字体文件，如果指定的字体不存在，将使用默认字体
- 支持文字旋转功能，通过rotation参数设置旋转角度（以度为单位）
- 支持文字透明度调节，通过opacity参数设置透明度值（0-255，0为完全透明）
- 图片路径必须正确，否则会显示错误提示或占位图
- 保存为JPG格式会丢失透明度信息，建议使用PNG格式保存

# N8N Nodes for Image Generation

This package provides N8N nodes for generating images with text and image overlays.

## Features

- Create blank canvases or load existing images
- Add text with customizable font, size, color, and alignment
- Add multiple texts from CSV file
- Overlay images with scaling and rotation
- Return images as Base64-encoded binary data

## 安装

### 社区节点安装

```bash
npm install n8n-nodes-picEdit
```

### 开发环境安装

```bash
git clone <repo-url>
cd n8n-nodes-picEdit
npm install
npm run build
```

## 使用

在 N8N 中，您可以在节点面板中找到 "Generate Photo" 节点，该节点提供了以下操作：

1. **Create Canvas** - 创建一个新的画布
2. **Add Text** - 在画布上添加文本
3. **Add Image** - 在画布上添加图像

### Create Canvas

创建一个新的画布，可以选择纯色背景或使用背景图像。

### Add Text

在画布上添加文本，支持多种自定义选项：
- 文本内容
- 位置 (X, Y)
- 字体大小
- 颜色
- 字体名称
- 对齐方式

### Add Image

在画布上添加图像，支持多种自定义选项：
- 图像路径
- 位置 (X, Y)
- 缩放比例
- 旋转角度

## 运行测试工作流

```bash
n8n execute --file test-workflow.json
```

## 构建自己的节点

```bash
npm run build
```

## Node Types

### 1. Generate Photo

This is the main node that provides all image generation capabilities.

#### Operations

1. **Create Canvas**
   - Create a blank canvas with specified dimensions and background color
   - Load an existing image as the base canvas

2. **Add Text**
   - Add text to the canvas with customizable properties:
     - Text content
     - Position (X, Y)
     - Font size
     - Color
     - Font name
     - Alignment (left, center, right)
   - **CSV Support**: Load multiple texts from a CSV file with the following columns:
     - `text`: Text content
     - `position_x`: X position
     - `position_y`: Y position
     - `font_size`: Font size (optional, defaults to 24)
     - `color`: Text color (optional, defaults to black)
     - `font_name`: Font name (optional)
     - `alignment`: Text alignment (optional, defaults to left)
     - `rotation`: Rotation angle in degrees (optional, defaults to 0)
     - `opacity`: Text opacity (0-255, optional, defaults to 255)

3. **Add Image**
   - Overlay an image on the canvas with customizable properties:
     - Image path
     - Position (X, Y)
     - Scale factor
     - Rotation angle

## Usage

### Basic Workflow

1. Start with a "Create Canvas" operation to create your base image
2. Add text or images using the respective operations
3. Each operation builds on the previous one, passing the image data through
4. The final node outputs the Base64-encoded image data

### Example: Create an Image with Text

1. Add a "Generate Photo" node
2. Set operation to "Create Canvas"
3. Configure canvas dimensions and background color
4. Add another "Generate Photo" node
5. Set operation to "Add Text"
6. Configure text properties
7. Connect the nodes in sequence

### Example: Create an Image with Multiple Texts from CSV

1. Create a CSV file with the required columns:
   ```csv
   text,position_x,position_y,font_size,color,font_name,alignment
   Hello World,100,50,36,#FF0000,Arial,center
   This is a subtitle,100,100,24,#0000FF,Arial,left
   ```
2. Add a "Generate Photo" node
3. Set operation to "Create Canvas"
4. Configure canvas dimensions and background color
5. Add another "Generate Photo" node
6. Set operation to "Add Text"
7. Select "CSV File" as text source
8. Provide the path to your CSV file
9. Connect the nodes in sequence

## Requirements

- Node.js (version 12 or higher)
- Python (version 3.6 or higher)
- Pillow library for Python

## Development

### Building the Project

```bash
npm run build
```

### Running in Development Mode

```bash
npm run dev
```

## Python Component

This N8N node package uses a Python component for image processing. The Python component is located in the `python` directory and includes:

- `canvas_generator.py`: The main image generation library
- `wrapper.py`: A wrapper script that interfaces with the N8N node
- `requirements.txt`: Python dependencies

To install the Python dependencies:

```bash
pip install -r python/requirements.txt
```

## License

MIT