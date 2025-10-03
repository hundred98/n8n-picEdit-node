#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Binary transmission version - no need to handle Chinese paths
Directly receive base64 image data
"""

import json
import sys
import os
import base64
import io
from PIL import Image, ImageDraw, ImageFont

def create_canvas_from_binary(config):
    """Create canvas from binary data"""
    try:
        canvas_config = config.get('canvas', {})
        width = canvas_config.get('width', 800)
        height = canvas_config.get('height', 600)
        bg_color = canvas_config.get('backgroundColor', '#FFFFFF')
        bg_image_data = canvas_config.get('backgroundImageData')
        
        # Create canvas
        canvas = Image.new('RGBA', (width, height), bg_color)
        
        # Handle background image data
        if bg_image_data:
            try:
                # Decode base64 image data
                image_data = base64.b64decode(bg_image_data)
                bg_image = Image.open(io.BytesIO(image_data)).convert('RGBA')
                bg_image = bg_image.resize((width, height))
                canvas.paste(bg_image, (0, 0))
            except Exception:
                pass  # Skip if background image processing fails
        
        # Process elements
        elements = config.get('elements', [])
        for element in elements:
            if element.get('type') == 'text':
                pos = element.get('position', [0, 0])
                text = element.get('text', '')
                size = element.get('fontSize', 24)
                color = element.get('color', '#000000')
                rotation = element.get('rotation', 0)
                opacity = element.get('opacity', 255)
                font_name = element.get('fontName')
                
                # Font loading logic
                font = None
                
                # Chinese font fallback list
                CHINESE_FONTS = [
                    "C:/Windows/Fonts/arialuni.ttf",      # Arial Unicode (best Chinese support)
                    "C:/Windows/Fonts/msyh.ttc",          # Microsoft YaHei
                    "C:/Windows/Fonts/simhei.ttf",        # SimHei
                    "C:/Windows/Fonts/simsun.ttc",        # SimSun
                    "Arial Unicode.ttf",                  # Relative path attempt
                    "msyh.ttc",
                    "simhei.ttf",
                ]
                
                # 1. Try user specified font
                if font_name:
                    try:
                        font = ImageFont.truetype(font_name, size)
                    except IOError:
                        pass
                
                # 2. If user font fails, try Chinese font list
                if font is None:
                    for chinese_font in CHINESE_FONTS:
                        try:
                            if os.path.exists(chinese_font):
                                font = ImageFont.truetype(chinese_font, size)
                                break
                        except IOError:
                            continue
                
                # 3. Finally use system default font
                if font is None:
                    try:
                        font = ImageFont.load_default()
                    except Exception:
                        continue  # Skip this text element
                
                # If there's rotation or opacity, need to create temporary layer
                if rotation != 0 or opacity != 255:
                    # Handle color transparency
                    if isinstance(color, str):
                        if color.startswith('#'):
                            # Convert hex color to RGB
                            color = color.lstrip('#')
                            if len(color) == 6:
                                r, g, b = tuple(int(color[i:i+2], 16) for i in (0, 2, 4))
                                color = (r, g, b, opacity)
                            else:
                                color = (0, 0, 0, opacity)
                        else:
                            color = (0, 0, 0, opacity)
                    elif isinstance(color, (tuple, list)) and len(color) >= 3:
                        color = (color[0], color[1], color[2], opacity)
                    else:
                        color = (0, 0, 0, opacity)
                    
                    # If rotation is needed, use text top-left corner as rotation point
                    if rotation != 0:
                        # Get text dimensions
                        try:
                            bbox = font.getbbox(text)
                            text_width = bbox[2] - bbox[0]
                            text_height = bbox[3] - bbox[1]
                        except:
                            # If getting dimensions fails, use estimated values
                            text_width = len(text) * size // 2
                            text_height = size
                        
                        # Create large enough temporary layer to contain rotated text
                        temp_size = max(text_width, text_height) * 2 + 100
                        txt_layer = Image.new('RGBA', (temp_size, temp_size), (0, 0, 0, 0))
                        txt_draw = ImageDraw.Draw(txt_layer)
                        
                        # Draw text at center of temporary layer
                        temp_pos = (temp_size // 2, temp_size // 2)
                        txt_draw.text(temp_pos, text, font=font, fill=color)
                        
                        # Rotate temporary layer
                        try:
                            rotated_layer = txt_layer.rotate(rotation, resample=Image.Resampling.BICUBIC, expand=0)
                        except AttributeError:
                            try:
                                rotated_layer = txt_layer.rotate(rotation, resample=1, expand=0)  # 1 = BICUBIC
                            except AttributeError:
                                rotated_layer = txt_layer.rotate(rotation, expand=0)
                        
                        # Calculate paste position so rotated text top-left corner corresponds to original position
                        paste_x = pos[0] - temp_size // 2
                        paste_y = pos[1] - temp_size // 2
                        
                        # Paste rotated text to canvas
                        canvas.paste(rotated_layer, (paste_x, paste_y), rotated_layer)
                    else:
                        # No rotation, directly draw text with transparency
                        draw = ImageDraw.Draw(canvas)
                        draw.text(pos, text, font=font, fill=color)
                else:
                    # No rotation and transparency, draw directly
                    draw = ImageDraw.Draw(canvas)
                    draw.text(pos, text, font=font, fill=color)
                
            elif element.get('type') == 'image':
                pos = element.get('position', [0, 0])
                image_data = element.get('imageData')
                scale = element.get('scale', 1.0)
                
                if image_data:
                    try:
                        # Decode base64 image data
                        img_data = base64.b64decode(image_data)
                        img = Image.open(io.BytesIO(img_data)).convert('RGBA')
                        
                        if scale != 1.0:
                            new_size = (int(img.width * scale), int(img.height * scale))
                            img = img.resize(new_size, Image.Resampling.LANCZOS)
                        
                        canvas.paste(img, pos, img)
                    except Exception:
                        pass  # Skip if image processing fails
        
        return canvas
        
    except Exception as e:
        raise Exception(f"Canvas creation failed: {str(e)}")

def main():
    """Main function"""
    try:
        # Read configuration from stdin
        data = sys.stdin.buffer.read().decode('utf-8')
        if not data.strip():
            print(json.dumps({"success": False, "error": "No input data"}))
            return
        
        config = json.loads(data)
        canvas = create_canvas_from_binary(config)
        
        # Convert to base64
        buffer = io.BytesIO()
        canvas.save(buffer, format='PNG')
        base64_str = base64.b64encode(buffer.getvalue()).decode('utf-8')
        
        result = {
            "success": True,
            "message": "Image processing completed successfully",
            "base64": base64_str,
            "width": canvas.width,
            "height": canvas.height
        }
        
        print(json.dumps(result, ensure_ascii=False))
        sys.stdout.flush()
        
    except Exception as e:
        error_result = {
            "success": False,
            "error": str(e)
        }
        print(json.dumps(error_result))
        sys.stdout.flush()

if __name__ == "__main__":
    main()