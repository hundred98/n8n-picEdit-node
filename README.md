# n8n-nodes-picedit

![n8n](https://img.shields.io/badge/n8n-node-FF6D5A.svg)
![npm version](https://img.shields.io/npm/v/n8n-nodes-picedit.svg)
![license](https://img.shields.io/npm/l/n8n-nodes-picedit.svg)

A powerful n8n community node for image processing and generation. Create canvases, add text overlays, and composite images with full binary data support. Built with Sharp.js for high-performance image processing without external dependencies.

## 🚀 Features

- **Canvas Creation**: Create blank canvases or use existing images as backgrounds
- **Text Overlays**: Add customizable text with fonts, colors, rotation, and opacity
- **Image Composition**: Overlay images with scaling and rotation support
- **Binary Data Support**: Full integration with n8n's binary data workflow
- **Batch Processing**: Process multiple text elements from CSV files
- **Security**: Built-in path validation and security measures
- **Pure Node.js**: Built with Sharp.js - no Python or external dependencies required
- **High Performance**: Fast image processing with native Sharp library
- **Cross-Platform**: Works on Windows, macOS, and Linux
- **Unicode Support**: Full support for emoji and special characters

## 📦 Installation

### Community Installation

Install via n8n's community nodes feature:

1. Go to **Settings > Community Nodes**
2. Enter the package name: `n8n-nodes-picedit`
3. Click **Install**

### Manual Installation

```bash
# In your n8n installation directory
npm install n8n-nodes-picedit
```

### Prerequisites

- Node.js 16.10 or higher
- n8n 0.190.0 or higher

**No additional dependencies required!** The node uses Sharp.js which is automatically installed as a dependency.

## 🎯 Node Operations

### Create Canvas

Create a new image canvas as the foundation for your design.

**Options:**
- **Blank Canvas**: Custom dimensions with solid background color
- **From Image**: Use an existing image file as the canvas background

**Parameters:**
- `Width/Height`: Canvas dimensions in pixels
- `Background Color`: Hex color code (e.g., #FFFFFF)
- `Image Path`: Path to background image file (relative paths recommended)

### Add Text

Add text overlays to your canvas with extensive customization options.

**Input Methods:**
- **Manual**: Single text element with full customization
- **CSV File**: Batch process multiple text elements from a CSV file

**Text Properties:**
- Position (X, Y coordinates)
- Font size and type selection
- Color (hex format)
- Rotation angle
- Opacity (0-255)

**Font Selection:**
- **System Fonts**: Choose from 58 comprehensive Windows fonts (Arial, Times New Roman, Segoe UI, etc.)
- **Custom Fonts**: Use custom font files or font family names
- **Smart Fallback**: Automatic fallback to sans-serif if font unavailable

**CSV Format (Updated):**
```csv
text,position_x,position_y,font_size,color,font_type,font_value,rotation,opacity
Hello World,100,50,36,#FF0000,system,Arial,0,255
Welcome,200,120,28,#0066CC,system,Microsoft YaHei,15,230
Custom Font,300,180,24,#009900,custom,/fonts/custom.ttf,0,255
```

**Backward Compatibility:** The node maintains compatibility with the old CSV format using `font_name` column.

### Add Image

Overlay images onto your canvas with transformation options.

**Parameters:**
- `Image Path`: Path to overlay image file
- `Position`: X, Y coordinates for placement
- `Scale`: Scaling factor (1.0 = original size)
- `Rotation`: Rotation angle in degrees

## 🔄 Workflow Examples

### Example 1: Text Badge Generator

```
[Manual Trigger] → [PicEdit: Create Canvas] → [PicEdit: Add Text] → [Save Binary]
```

1. Create a 400x200 canvas with blue background
2. Add white text "APPROVED" in the center
3. Output as PNG binary data

### Example 2: Batch Certificate Generator

```
[CSV File] → [Split In Batches] → [PicEdit: Create Canvas] → [PicEdit: Add Text (CSV)] → [Email]
```

1. Load certificate template as canvas background
2. Process names from CSV file
3. Generate personalized certificates
4. Email each certificate

### Example 3: Social Media Post

```
[HTTP Request: Image] → [PicEdit: Add Text] → [PicEdit: Add Image] → [Post to Social]
```

1. Fetch background image from URL
2. Add title text overlay
3. Add logo watermark
4. Post to social media platforms

## ⚙️ Configuration

### Binary Data Fields

The node supports flexible binary data handling:

- **Input Binary Field**: Specify the field name containing input image data
- **Output Field Name**: Customize the output binary field name
- **Format Options**: PNG, JPEG, WebP with quality settings

### File Path Security

For security, file paths are validated to prevent:
- Directory traversal attacks (`../` patterns)
- Access to system directories
- Invalid or malicious paths

**Best Practices:**
- Use relative paths when possible
- Store assets in dedicated directories
- Avoid absolute system paths

### Output Formats

Choose from multiple output formats:
- **PNG**: Lossless, supports transparency
- **JPEG**: Compressed, adjustable quality (1-100)
- **WebP**: Modern format with excellent compression

## 🛠️ Advanced Usage

### Font Management

**Enhanced Font Selection System (v0.1.4+)**

The node now features a comprehensive font selection system:

**Font Type Selection:**
- **System Fonts**: Choose from 58 comprehensive Windows fonts including:
  - **Basic Fonts**: Arial, Times New Roman, Courier New, Verdana, Georgia, Tahoma, Impact
  - **Modern Fonts**: Segoe UI, Calibri, Cambria, Candara, Corbel, Constantia, Bahnschrift
  - **Monospace Fonts**: Consolas, Lucida Console, Cascadia Code, Cascadia Mono
  - **Script/Decorative**: Comic Sans MS, Trebuchet MS, Gabriola, Ink Free, Segoe Print, Segoe Script
  - **International**: Microsoft YaHei, SimHei, SimSun, DengXian, FangSong, KaiTi, Noto Sans SC
  - **UI Fonts**: Segoe UI, Microsoft Sans Serif, Leelawadee UI, Nirmala UI, Malgun Gothic
  - **Symbol Fonts**: Segoe UI Emoji, Segoe UI Symbol, Symbol, Webdings, Wingdings

- **Custom Fonts**: Use custom font files or font family names
  - Font file paths (./fonts/custom.ttf, ./fonts/custom.otf)
  - Font family names for web-safe fonts
  - Automatic fallback to system fonts if custom font unavailable

**Font Rendering Features:**
- Proper CSS font-family syntax with fallbacks
- SVG-based text rendering for precise typography
- Support for font weights and styles
- Unicode and emoji character support
- Cross-platform font compatibility

**Smart Fallback System:**
- Automatic fallback to sans-serif if specified font unavailable
- Font file validation and error handling
- Console warnings for missing custom fonts

### Error Handling

Comprehensive error handling with detailed messages:
- File not found errors
- Invalid image format detection
- Path security violations
- Font loading failures

### Performance Tips

- Use appropriate image sizes to avoid memory issues
- Optimize CSV files for batch processing
- Consider caching frequently used assets
- Use WebP format for smaller file sizes

## 🔧 Development

### Building from Source

```bash
git clone https://github.com/hundred98/n8n-picEdit-node.git
cd n8n-picEdit-node
npm install
npm run build
```

### Project Structure

```
n8n-nodes-picedit/
├── nodes/
│   └── picEdit/
│       ├── PicEdit.node.ts           # Main node implementation
│       ├── SharpImageProcessor.ts    # Sharp.js image processing engine
│       └── picEdit.svg               # Node icon
├── dist/                             # Compiled output
├── index.ts                          # Entry point
└── package.json
```

### Technical Architecture

The node is built with modern web technologies:

- **Sharp.js**: High-performance image processing library
- **SVG Composition**: Text rendering using SVG for precise typography
- **TypeScript**: Type-safe development with full IDE support
- **Zero Dependencies**: No external tools or Python scripts required
- **Memory Efficient**: Optimized for large image processing workflows

### Testing

```bash
npm run lint        # Code linting
npm run build       # Build project
npm run dev         # Development mode
```

## 🚨 Troubleshooting

### Common Issues

**"File not found" errors**
- Check file paths are correct and accessible
- Use relative paths when possible
- Verify file permissions

**"Invalid file path" errors**
- Path contains security violations
- Use safe, relative paths
- Avoid system directories

**Font rendering issues**
- Specify full font file paths
- Use system-available fonts
- Check font file accessibility

### Debug Information

The node provides detailed debug output including:
- Sharp.js processing status
- SVG text rendering information
- File path validations
- Image processing steps
- Font fallback mechanisms
- Error context and suggestions

## 📄 API Reference

### Node Properties

| Property | Type | Description |
|----------|------|-------------|
| operation | string | Operation type: createCanvas, addText, addImage |
| outputFormat | string | Output format: png, jpeg, webp |
| quality | number | Image quality for lossy formats (1-100) |
| fieldName | string | Binary output field name |

### Input Data Structure

```javascript
{
  json: {
    // Any JSON data
  },
  binary: {
    image: {
      data: "base64-encoded-image-data",
      mimeType: "image/png",
      fileName: "input.png"
    }
  }
}
```

### Output Data Structure

```javascript
{
  json: {
    success: true,
    message: "Canvas created successfully",
    fileInfo: {
      fileName: "generated-image.png",
      fileExtension: "png",
      mimeType: "image/png",
      fileSize: "15.6 KB"
    }
  },
  binary: {
    data: {
      data: "base64-encoded-result",
      mimeType: "image/png",
      fileName: "generated-image.png"
    }
  }
}
```

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📝 Changelog

### v0.1.4
- **Enhanced Font Selection System**: Comprehensive font type selection with 58 Windows fonts
- **Font Type UI**: Added hierarchical font selection menu (System Font / Custom Font)
- **System Font Support**: 58 comprehensive Windows fonts including Arial, Times New Roman, Segoe UI, Calibri, etc.
- **Custom Font Support**: Path-based custom font loading with fallback mechanisms
- **Updated CSV Format**: Added `font_type` and `font_value` columns for advanced font control
- **Backward Compatibility**: Maintains compatibility with old CSV format using `font_name` column
- **Font Rendering Fix**: Resolved font visibility issues with proper SVG font-family attributes
- **Documentation**: Added comprehensive font feature documentation and examples
- **Sample Files**: Added sample configuration files and system font detection script
- **Code Cleanup**: Removed test files and improved code organization

### v0.1.0
- Initial release with Sharp.js architecture
- Canvas creation and text overlay features
- Image composition capabilities
- CSV batch processing
- Binary data integration
- Security enhancements
- Improved error handling
- Pure Node.js implementation (no Python dependencies)
- SVG-based text rendering for precise typography
- Cross-platform compatibility
- Unicode and emoji support
- High-performance image processing

## 📜 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🔗 Links

- [n8n Community Nodes](https://docs.n8n.io/integrations/community-nodes/)
- [GitHub Repository](https://github.com/hundred98/n8n-picEdit-node)
- [npm Package](https://www.npmjs.com/package/n8n-nodes-picedit)
- [Issue Tracker](https://github.com/hundred98/n8n-picEdit-node/issues)

## 💬 Support

- Create an issue on [GitHub](https://github.com/hundred98/n8n-picEdit-node/issues)
- Join the [n8n Community](https://community.n8n.io/)
- Check the [n8n Documentation](https://docs.n8n.io/)

### 📱 WeChat Support | 微信支持

For any questions or suggestions, feel free to follow my WeChat Official Account for technical support:

如果您有任何问题或建议，欢迎关注我的微信公众号获取技术支持：

<div align="center">
  <img src="./assets/wechat-qr.jpg" alt="WeChat QR Code" width="200"/>
  <br>
  <em>Scan QR Code to Follow | 扫码关注微信公众号</em>
</div>

---

Made with ❤️ for the n8n community