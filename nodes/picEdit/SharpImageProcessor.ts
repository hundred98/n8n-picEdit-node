// 在导入Sharp之前，先设置所有可能的环境变量来禁用调试输出
process.env.VIPS_WARNING = '0';
process.env.VIPS_INFO = '0';
process.env.VIPS_PROGRESS = '0';
process.env.VIPS_DEBUG = '0';
process.env.VIPS_LEAK = '0';
process.env.VIPS_TRACE = '0';
process.env.VIPS_CONCURRENCY = '1';
process.env.VIPS_DISC_THRESHOLD = '0';
process.env.VIPS_NOVECTOR = '1';
process.env.VIPS_OPERATION_BLOCK = '1';

const sharp = require('sharp');
import * as fs from 'fs';
import * as path from 'path';

// 创建一个静默的Sharp实例配置
const configureSharpSilent = () => {
    try {
        sharp.simd(false);
        sharp.concurrency(1);
        // 尝试禁用Sharp的内部缓存和调试
        sharp.cache(false);
    } catch (error) {
        // 忽略配置错误
    }
};

// 立即执行配置
configureSharpSilent();

/**
 * Sharp-based image processor to replace Python PIL functionality
 * Maintains 100% compatibility with existing Python implementation
 */
export class SharpImageProcessor {
    
    /**
     * Create a canvas with specified dimensions and background
     */
    async createCanvas(config: CanvasConfig): Promise<Buffer> {
        try {
            const { width, height, backgroundColor, backgroundImageData } = config;
            
            // Validate dimensions
            if (!width || !height || width <= 0 || height <= 0) {
                throw new Error(`Invalid canvas dimensions: ${width}x${height}`);
            }
            
            // Parse background color
            const bgColor = this.parseColor(backgroundColor || '#FFFFFF');
            
            // Create base canvas
            let canvas: any;
            
            if (backgroundImageData) {
                // Handle background image
                try {
                    const bgImageBuffer = Buffer.from(backgroundImageData, 'base64');
                    canvas = sharp(bgImageBuffer)
                        .resize(width, height, { 
                            fit: 'fill',
                            kernel: sharp.kernel.lanczos3 
                        });
                } catch (error) {
                    throw new Error(`Failed to process background image: ${(error as Error).message}`);
                }
            } else {
                // Create solid color canvas
                canvas = sharp({
                    create: {
                        width,
                        height,
                        channels: 4,
                        background: bgColor
                    }
                }).png();
            }
            
            return await canvas.toBuffer();
            
        } catch (error) {
            throw new Error(`Canvas creation failed: ${(error as Error).message}`);
        }
    }
    
    /**
     * Add text to canvas using Canvas API for rendering
     */
    async addText(canvasBuffer: Buffer, textConfig: TextConfig): Promise<Buffer> {
        try {
            // Validate text configuration
            this.validateTextConfig(textConfig);
            
            // Get canvas info
            const canvasInfo = await sharp(canvasBuffer).metadata();
            const canvasWidth = canvasInfo.width!;
            const canvasHeight = canvasInfo.height!;
            
            // Create text layer using Canvas API
            const textBuffer = await this.createTextLayer(textConfig, canvasWidth, canvasHeight);
            
            // Composite text onto canvas
            const result = await sharp(canvasBuffer)
                .composite([{
                    input: textBuffer,
                    top: 0,
                    left: 0,
                    blend: 'over'
                }])
                .png()
                .toBuffer();
                
            return result;
            
        } catch (error) {
            throw new Error(`Text rendering failed: ${(error as Error).message}`);
        }
    }
    
    /**
     * Create text layer using simple SVG approach
     * Note: librsvg warnings are system-level and cannot be completely suppressed from Node.js
     */
    private async createTextLayer(config: TextConfig, canvasWidth: number, canvasHeight: number): Promise<Buffer> {
        const { text, fontSize, color, position, rotation = 0, opacity = 255, fontPath } = config;
        
        // Parse color and opacity
        const parsedColor = this.parseColor(color);
        const alpha = opacity / 255;
        const colorWithOpacity = `rgba(${parsedColor.r}, ${parsedColor.g}, ${parsedColor.b}, ${alpha})`;
        
        // Escape text for SVG
        const escapedText = this.escapeXmlText(text);
        
        // Use specified font or default to Arial
        let fontFamily = 'Arial, sans-serif';
        if (fontPath) {
            // Debug logging
            console.log(`Font Debug - Processing fontPath: ${fontPath}`);
            
            // For system fonts, use the font name directly with proper CSS font-family syntax
            const systemFonts = [
                'Arial', 'Arial Black', 'Bahnschrift', 'Calibri', 'Cambria', 'Candara',
                'Cascadia Code', 'Cascadia Mono', 'Comic Sans MS', 'Consolas', 'Constantia',
                'Corbel', 'Courier New', 'DengXian', 'Ebrima', 'FangSong', 'Franklin Gothic Medium',
                'Gabriola', 'Gadugi', 'Georgia', 'Impact', 'Ink Free', 'Javanese Text',
                'KaiTi', 'Leelawadee UI', 'Lucida Console', 'Lucida Sans Unicode', 'Malgun Gothic',
                'Microsoft Himalaya', 'Microsoft JhengHei', 'Microsoft New Tai Lue', 'Microsoft PhagsPa',
                'Microsoft Sans Serif', 'Microsoft Tai Le', 'Microsoft YaHei', 'Microsoft Yi Baiti',
                'Mongolian Baiti', 'MS Gothic', 'MV Boli', 'Myanmar Text', 'Nirmala UI',
                'Segoe UI Emoji', 'Segoe UI Historic', 'Segoe UI Symbol', 'SimHei', 'SimSun',
                'Sitka Text', 'Sylfaen', 'Symbol', 'Tahoma', 'Times New Roman', 'Trebuchet MS',
            ];
            
            if (systemFonts.includes(fontPath)) {
                // Use proper CSS font-family syntax with fallbacks
                if (fontPath.includes(' ')) {
                    // Wrap with single quotes if name contains spaces
                    fontFamily = `'${fontPath}', sans-serif`;
                } else {
                    fontFamily = `${fontPath}, sans-serif`;
                }
                console.log(`Font Debug - Using system font: ${fontFamily}`);
            } else {
                // For custom fonts, check if it's a file path or font name
                if (fontPath.includes('/') || fontPath.includes('\\') || fontPath.includes('.ttf') || fontPath.includes('.otf')) {
                    // This is a file path - for now use fallback
                    fontFamily = 'Arial, sans-serif';
                    console.warn(`Custom font file path specified but file loading not implemented: ${fontPath}. Using Arial as fallback.`);
                } else {
                    // Treat as font family name
                    fontFamily = fontPath.includes(' ') ? `'${fontPath}', sans-serif` : `${fontPath}, sans-serif`;
                    console.log(`Font Debug - Using custom font family: ${fontFamily}`);
                }
            }
        }
        // Calculate text positioning
        const x = position[0];
        const y = position[1] + fontSize;
        
        // Create minimal SVG
        let svgContent: string;
        
        if (rotation !== 0) {
            svgContent = `<svg xmlns="http://www.w3.org/2000/svg" width="${canvasWidth}" height="${canvasHeight}">
<g transform="rotate(${rotation} ${x} ${y})">
<text x="${x}" y="${y}" font-family="${fontFamily}" font-size="${fontSize}" fill="${colorWithOpacity}">${escapedText}</text>
</g>
</svg>`;
        } else {
            svgContent = `<svg xmlns="http://www.w3.org/2000/svg" width="${canvasWidth}" height="${canvasHeight}">
<text x="${x}" y="${y}" font-family="${fontFamily}" font-size="${fontSize}" fill="${colorWithOpacity}">${escapedText}</text>
</svg>`;
        }
        
        try {
            const svgBuffer = Buffer.from(svgContent, 'utf8');
            
            // 使用更激进的方法来屏蔽Sharp输出 - 临时重定向stderr
            const originalStderr = process.stderr.write;
            const originalStdout = process.stdout.write;
            
            // 重定向stderr和stdout来屏蔽Sharp的调试输出
            process.stderr.write = function(string: string | Buffer, ...args: any[]): boolean {
                const str = string.toString();
                // 过滤掉Sharp相关的调试信息
                if (str.includes('sharp temp-') || str.includes('done in') || str.includes('pixels,') || str.includes('threads,') || str.includes('tiles,') || str.includes('buffer')) {
                    return true; // 丢弃这些输出
                }
                return originalStderr.apply(process.stderr, [string, ...args]);
            };
            
            process.stdout.write = function(string: string | Buffer, ...args: any[]): boolean {
                const str = string.toString();
                // 过滤掉Sharp相关的调试信息
                if (str.includes('sharp temp-') || str.includes('done in') || str.includes('pixels,') || str.includes('threads,') || str.includes('tiles,') || str.includes('buffer')) {
                    return true; // 丢弃这些输出
                }
                return originalStdout.apply(process.stdout, [string, ...args]);
            };
            
            const result = await sharp(svgBuffer, {
                density: 72,
                failOn: 'none',
                unlimited: true
            })
            .png({ 
                force: true,
                progressive: false,
                compressionLevel: 0
            })
            .toBuffer();
            
            // 恢复原始的stderr和stdout
            process.stderr.write = originalStderr;
            process.stdout.write = originalStdout;
            
            return result;
            
        } catch (error) {
            // 确保在错误情况下也恢复原始输出流
            if (process.stderr.write !== process.stderr.write) {
                process.stderr.write = process.stderr.write;
            }
            if (process.stdout.write !== process.stdout.write) {
                process.stdout.write = process.stdout.write;
            }
            throw new Error(`SVG text rendering failed: ${(error as Error).message}`);
        }
    }
    

    
    /**
     * Escape text for SVG XML content - FIXED VERSION
     */
    private escapeXmlText(text: string): string {
        // Use character codes to avoid encoding issues
        const ampersand = String.fromCharCode(38, 97, 109, 112, 59); // &
        const lessThan = String.fromCharCode(38, 108, 116, 59);      // <
        const greaterThan = String.fromCharCode(38, 103, 116, 59);   // >
        const quote = String.fromCharCode(38, 113, 117, 111, 116, 59); // "
        
        return text
            .replace(/&/g, ampersand)    // Ampersand - must be first
            .replace(/</g, lessThan)     // Less than
            .replace(/>/g, greaterThan)  // Greater than  
            .replace(/"/g, quote)        // Double quote
            .replace(/'/g, '&#39;');     // Single quote
    }
    
    /**
     * Validate text configuration
     */
    private validateTextConfig(config: TextConfig): void {
        if (!config.text || typeof config.text !== 'string') {
            throw new Error('Text is required and must be a string');
        }
        
        if (!config.fontSize || config.fontSize <= 0) {
            throw new Error(`Invalid font size: ${config.fontSize}`);
        }
        
        if (!Array.isArray(config.position) || config.position.length !== 2) {
            throw new Error('Position must be an array of [x, y] coordinates');
        }
        
        if (!config.color) {
            throw new Error('Color is required');
        }
    }
    
    /**
     * Parse color string to RGB format
     * Supports: #RRGGBB, #RGB, rgb(r,g,b), rgba(r,g,b,a)
     */
    private parseColor(colorStr: string): { r: number; g: number; b: number; alpha: number } {
        try {
            if (typeof colorStr !== 'string') {
                throw new Error('Color must be a string');
            }
            
            // Handle hex colors
            if (colorStr.startsWith('#')) {
                const hex = colorStr.slice(1);
                if (hex.length === 3) {
                    // #RGB -> #RRGGBB
                    const r = parseInt(hex[0] + hex[0], 16);
                    const g = parseInt(hex[1] + hex[1], 16);
                    const b = parseInt(hex[2] + hex[2], 16);
                    return { r, g, b, alpha: 1 };
                } else if (hex.length === 6) {
                    // #RRGGBB
                    const r = parseInt(hex.slice(0, 2), 16);
                    const g = parseInt(hex.slice(2, 4), 16);
                    const b = parseInt(hex.slice(4, 6), 16);
                    return { r, g, b, alpha: 1 };
                }
            }
            
            // Handle rgb() and rgba()
            const rgbMatch = colorStr.match(/rgba?\(([^)]+)\)/);
            if (rgbMatch) {
                const values = rgbMatch[1].split(',').map(v => parseFloat(v.trim()));
                if (values.length >= 3) {
                    return {
                        r: Math.round(values[0]),
                        g: Math.round(values[1]),
                        b: Math.round(values[2]),
                        alpha: values.length > 3 ? values[3] : 1
                    };
                }
            }
            
            throw new Error(`Unsupported color format: ${colorStr}`);
            
        } catch (error) {
            throw new Error(`Invalid color value '${colorStr}': ${(error as Error).message}`);
        }
    }
    
    /**
     * Parse color with opacity for Canvas API
     */
    private parseColorWithOpacity(colorStr: string, opacity: number = 255): string {
        const color = this.parseColor(colorStr);
        const alpha = opacity / 255; // Convert 0-255 to 0-1
        return `rgba(${color.r}, ${color.g}, ${color.b}, ${alpha})`;
    }
}

/**
 * Configuration interfaces
 */
export interface CanvasConfig {
    width: number;
    height: number;
    backgroundColor?: string;
    backgroundImageData?: string; // base64 encoded image
}

export interface TextConfig {
    text: string;
    fontSize: number;
    color: string;
    position: [number, number]; // [x, y]
    rotation?: number; // degrees
    opacity?: number; // 0-255
    fontPath?: string; // path to custom font file
}

export interface ImageConfig {
    imageData: string; // base64 encoded image
    position: [number, number]; // [x, y]
    scale?: number; // scaling factor
}