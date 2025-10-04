import sharp from 'sharp';
import { createCanvas, loadImage, registerFont } from 'canvas';
import * as fs from 'fs';
import * as path from 'path';

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
            let canvas: sharp.Sharp;
            
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
                    throw new Error(`Failed to process background image: ${error.message}`);
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
            throw new Error(`Canvas creation failed: ${error.message}`);
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
            throw new Error(`Text rendering failed: ${error.message}`);
        }
    }
    
    /**
     * Create text layer using Canvas API
     */
    private async createTextLayer(config: TextConfig, canvasWidth: number, canvasHeight: number): Promise<Buffer> {
        const { text, fontSize, color, position, rotation = 0, opacity = 255, fontPath } = config;
        
        // Create canvas for text rendering
        const canvas = createCanvas(canvasWidth, canvasHeight);
        const ctx = canvas.getContext('2d');
        
        // Set transparent background
        ctx.clearRect(0, 0, canvasWidth, canvasHeight);
        
        // Load custom font if specified
        if (fontPath) {
            try {
                if (!fs.existsSync(fontPath)) {
                    throw new Error(`Font file not found: ${fontPath}`);
                }
                
                // Register the font
                const fontName = `custom_font_${Date.now()}`;
                registerFont(fontPath, { family: fontName });
                ctx.font = `${fontSize}px "${fontName}"`;
            } catch (error) {
                throw new Error(`Font loading failed: ${error.message}`);
            }
        } else {
            // Use default font
            ctx.font = `${fontSize}px Arial`;
        }
        
        // Parse and set color with opacity
        const textColor = this.parseColorWithOpacity(color, opacity);
        ctx.fillStyle = textColor;
        
        // Set text baseline to match PIL behavior (top-left positioning)
        ctx.textBaseline = 'top';
        ctx.textAlign = 'left';
        
        // Handle rotation
        if (rotation !== 0) {
            ctx.save();
            ctx.translate(position[0], position[1]);
            ctx.rotate((rotation * Math.PI) / 180);
            
            // Draw text at origin after rotation
            ctx.fillText(text, 0, 0);
            ctx.restore();
        } else {
            // Draw text directly
            ctx.fillText(text, position[0], position[1]);
        }
        
        // Convert canvas to buffer
        return canvas.toBuffer('image/png');
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
            throw new Error(`Invalid color value '${colorStr}': ${error.message}`);
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