# N8N PicEdit Node

这是一个功能强大的 N8N 自定义节点，用于图片处理和生成，支持画布创建、文字添加和图片叠加等功能。

## 功能特点

- **创建画布**：支持自定义尺寸和背景色，或从二进制图片数据创建画布
- **添加文字**：支持自定义字体、大小、颜色、旋转角度和透明度
- **添加图片**：支持图片叠加、缩放和旋转
- **二进制数据处理**：完全支持 N8N 的二进制数据传递
- **灵活的输入输出**：支持从工作流中的任意字段读取二进制图片数据

## 安装

### 开发环境安装

```bash
git clone <repo-url>
cd picEdit
npm install
npm run build
```

### 依赖要求

- Node.js (版本 12 或更高)
- Python (版本 3.6 或更高)
- Pillow 库

安装 Python 依赖：

```bash
pip install pillow
```

## 使用方法

### 节点操作类型

PicEdit 节点提供三种操作类型：

#### 1. Create Canvas (创建画布)

创建新的画布，支持两种模式：
- **纯色背景**：指定宽度、高度和背景颜色
- **背景图片**：从指定路径加载图片作为背景

**参数：**
- Canvas Type: 选择 "Blank Canvas" 或 "Background Image"
- Width/Height: 画布尺寸（像素）
- Background Color: 背景颜色（十六进制格式，如 #FFFFFF）
- Image Path: 背景图片路径（仅在选择 Background Image 时）

#### 2. Add Text (添加文字)

在画布上添加文字，支持丰富的自定义选项。

**输入源：**
- **Manual Input**: 手动输入单个文字
- **CSV File**: 从 CSV 文件批量添加多个文字

**参数：**
- Input Binary Field Name: 输入的二进制图片字段名（可选）
- Text Source: 选择 "Manual Input" 或 "CSV File"

**Manual Input 参数：**
- Text: 文字内容
- Position X/Y: 文字位置坐标
- Font Size: 字体大小（像素）
- Color: 文字颜色（十六进制格式）
- Font Name: 字体名称（可选，支持系统字体路径）
- Rotation: 旋转角度（度，以文字左上角为旋转点）
- Opacity: 透明度（0-255，0为完全透明）

**CSV File 格式：**

节点会自动跳过第一行标题行，从第二行开始读取数据。节点支持UTF-8编码，可以正确处理中文字符。

```csv
text,position_x,position_y,font_size,color,font_name,rotation,opacity
Hello World,100,50,36,#FF0000,Arial,0,255
Welcome Message,200,120,28,#0066CC,Microsoft YaHei,15,230
Subtitle Text,150,200,20,#333333,Calibri,0,200
Footer Info,300,350,16,#666666,,0,180
中文测试,300,500,36,#00FF00,C:\Windows\Fonts\msyh.ttc,0,255
```

**CSV 模板文件：**
项目中提供了标准的 CSV 模板文件：`templates/text_template.csv`，包含中文示例。你可以复制并修改这个文件来创建自己的文字配置。

**CSV 编码注意事项：**
- 节点支持UTF-8编码的CSV文件，可以正确显示中文字符
- 如果使用Windows记事本编辑CSV，请选择"另存为" → 编码选择"UTF-8"
- 推荐使用VS Code、Notepad++等编辑器，可以确保UTF-8编码保存

#### 3. Add Image (添加图片)

在画布上叠加图片。

**参数：**
- Input Binary Field Name: 输入的二进制图片字段名（可选）
- Image Path: 要叠加的图片路径
- Position X/Y: 图片位置坐标
- Scale: 缩放比例（1.0 = 原尺寸）
- Rotation: 旋转角度（度）

### 工作流示例

#### 示例 1：创建简单的文字图片

1. 添加 "Pic Edit" 节点
2. 选择 "Create Canvas" 操作
3. 设置画布尺寸和背景色
4. 添加另一个 "Pic Edit" 节点
5. 选择 "Add Text" 操作
6. 配置文字属性
7. 连接节点

#### 示例 2：处理现有图片并添加文字

1. 使用其他节点获取图片数据（如 HTTP Request）
2. 添加 "Pic Edit" 节点，选择 "Add Text" 操作
3. 在 "Input Binary Field Name" 中指定图片数据的字段名
4. 配置文字属性
5. 节点将自动从二进制数据读取图片并添加文字

#### 示例 3：批量处理 CSV 文字

1. 准备 CSV 文件包含多个文字信息
2. 添加 "Pic Edit" 节点，选择 "Create Canvas"
3. 添加另一个 "Pic Edit" 节点，选择 "Add Text"
4. 选择 "CSV File" 作为文字源
5. 指定 CSV 文件路径

## 高级功能

### 字体系统

节点支持完整的字体加载系统：

1. **用户指定字体**：在 Font Name 中指定字体路径或名称
2. **自动回退**：如果指定字体加载失败，自动尝试系统字体
3. **调试信息**：提供详细的字体加载日志

**支持的字体格式：**
- Windows 系统字体路径（如：C:/Windows/Fonts/arial.ttf）
- 字体名称（如：Arial、Microsoft YaHei）
- 相对路径字体文件

### 旋转功能

- **文字旋转**：以文字左上角为旋转点，支持任意角度
- **图片旋转**：以图片中心为旋转点

### 透明度支持

- **文字透明度**：0-255范围，0为完全透明
- **图片透明度**：支持 PNG 格式的透明通道

### 二进制数据处理

节点完全支持 N8N 的二进制数据传递：

1. **输入**：可以从工作流中任意字段读取二进制图片数据
2. **输出**：生成的图片以二进制格式输出，可被其他节点使用
3. **格式支持**：PNG、JPG 等常见图片格式

## 输出格式

节点输出包含：

```json
{
  "success": true,
  "message": "Binary transmission successful. Font used: Arial",
  "fileInfo": {
    "fileName": "generated_image.png",
    "fileExtension": "png",
    "mimeType": "image/png",
    "fileSize": "15.6 KB"
  },
  "debug": {
    "font_info": "Received font name: 'Arial'",
    "font_loading": "Successfully loaded user font: 'Arial'"
  }
}
```

## 故障排除

### 字体问题

如果字体显示不正确：
1. 检查字体路径是否正确
2. 查看节点输出的调试信息
3. 确保字体文件存在且可读
4. 查看执行日志中的字体加载信息

### 图片处理问题

如果图片处理失败：
1. 确认图片格式支持（PNG、JPG、GIF等）
2. 检查图片文件路径是否正确
3. 验证二进制数据字段名是否正确
4. 确保文件路径指向文件而不是目录

### CSV 文件问题

如果CSV文件无法正确读取：
1. 确保CSV文件以UTF-8编码保存
2. 检查CSV文件路径是否正确
3. 验证CSV文件格式符合模板要求
4. 确保第一行是标题行，数据从第二行开始

### 中文字符显示问题

如果中文字符显示为小方块：
1. 确保CSV文件以UTF-8编码保存
2. 使用支持UTF-8的编辑器（VS Code、Notepad++）
3. 检查字体是否支持中文字符（如Microsoft YaHei）

### 文件路径错误

如果遇到"EISDIR"错误：
1. 确保提供的是文件路径而不是目录路径
2. 检查文件是否存在
3. 验证文件权限是否可读

### Python 环境

确保 Python 环境正确配置：
```bash
python --version  # 应该是 3.6+
pip install pillow
```

## 开发信息

### 项目结构

```
picEdit/
├── nodes/
│   └── picEdit/
│       └── PicEdit.node.ts    # 主节点文件
├── python/
│   ├── wrapper_binary.py      # Python 图片处理脚本
│   ├── canvas_generator.py    # 画布生成库
│   └── example.py             # 使用示例
├── dist/                      # 编译输出
└── package.json
```

### 构建项目

```bash
npm run build
```

### 开发模式

```bash
npm run dev
```

## 版本历史

### v1.0.0
- ✅ 基础的画布创建、文字添加、图片叠加功能
- ✅ 支持二进制数据输入输出
- ✅ 完整的字体系统和调试信息
- ✅ CSV 批量文字处理（UTF-8编码支持）
- ✅ 文字旋转和透明度支持（以文字左上角为旋转点）
- ✅ 智能字体回退机制
- ✅ 文件路径验证（防止目录读取错误）
- ✅ 中文字符完整支持
- ✅ 详细的调试输出和错误处理
- ✅ CSV模板文件和使用示例
- ✅ 全面的功能测试完成

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request 来改进这个项目。

## 联系方式

如有问题或建议，请通过 GitHub Issues 联系。