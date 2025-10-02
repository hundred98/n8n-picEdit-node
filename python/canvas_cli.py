#!/usr/bin/env python3
"""
命令行工具，用于创建和操作画布
"""

import argparse
import json
import os
import sys

# 添加上级目录到Python路径，以便导入canvas_generator
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from canvas_generator import Canvas


def create_canvas(args):
    """创建画布"""
    print(f"创建画布: {args.output}")
    
    # 创建画布
    canvas = Canvas(args.width, args.height, args.background)
    
    # 添加文字元素
    if args.texts:
        for text_args in args.texts:
            # 解析文本参数
            parts = text_args.split(',', 8)  # 最多分割成9部分
            if len(parts) >= 3:
                position = (int(parts[0]), int(parts[1]))
                text = parts[2]
                
                # 设置可选参数
                kwargs = {}
                if len(parts) > 3 and parts[3]:
                    kwargs['font_size'] = int(parts[3])
                if len(parts) > 4 and parts[4]:
                    kwargs['color'] = parts[4]
                if len(parts) > 5 and parts[5]:
                    kwargs['font_name'] = parts[5]
                if len(parts) > 6 and parts[6]:
                    kwargs['alignment'] = parts[6]
                if len(parts) > 7 and parts[7]:
                    kwargs['rotation'] = float(parts[7])
                if len(parts) > 8 and parts[8]:
                    kwargs['opacity'] = int(parts[8])
                
                canvas.add_text(position, text, **kwargs)
    
    # 添加图片元素
    if args.images:
        for image_args in args.images:
            # 解析图片参数
            parts = image_args.split(',', 5)  # 最多分割成6部分
            if len(parts) >= 2:
                position = (int(parts[0]), int(parts[1]))
                image_path = parts[2] if len(parts) > 2 else ""
                
                # 设置可选参数
                kwargs = {}
                if len(parts) > 3 and parts[3]:
                    kwargs['scale'] = float(parts[3])
                if len(parts) > 4 and parts[4]:
                    kwargs['rotation'] = float(parts[4])
                if len(parts) > 5 and parts[5]:
                    kwargs['opacity'] = int(parts[5])
                
                if os.path.exists(image_path):
                    canvas.add_image(position, image_path, **kwargs)
                else:
                    print(f"警告: 图片文件不存在: {image_path}")
    
    # 保存画布
    canvas.save(args.output, quiet=args.quiet)
    print(f"画布已保存到: {args.output}")


def create_example_config(args):
    """创建示例配置文件"""
    print(f"创建示例配置文件: {args.output}")
    
    config = {
        "canvas": {
            "width": 800,
            "height": 600,
            "background_color": "white"
        },
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
            },
            {
                "position": [200, 300],
                "text": "旋转文字",
                "font_size": 32,
                "color": "red",
                "rotation": 45
            },
            {
                "position": [600, 300],
                "text": "半透明文字",
                "font_size": 32,
                "color": "blue",
                "opacity": 128
            }
        ],
        "images": [
            {
                "position": [300, 400],
                "image_path": "example_image.jpg",
                "scale": 0.5,
                "rotation": 0,
                "opacity": 255
            }
        ]
    }
    
    with open(args.output, 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=2)
    
    print(f"示例配置文件已保存到: {args.output}")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="画布生成器命令行工具")
    parser.add_argument('--quiet', action='store_true', help='静默模式，不输出日志')
    
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # 创建画布命令
    create_parser = subparsers.add_parser('create', help='创建画布')
    create_parser.add_argument('--width', type=int, default=800, help='画布宽度 (默认: 800)')
    create_parser.add_argument('--height', type=int, default=600, help='画布高度 (默认: 600)')
    create_parser.add_argument('--background', default='white', help='背景颜色 (默认: white)')
    create_parser.add_argument('--texts', nargs='*', help='文字元素，格式: x,y,text,font_size,color,font_name,alignment,rotation,opacity')
    create_parser.add_argument('--images', nargs='*', help='图片元素，格式: x,y,image_path,scale,rotation,opacity')
    create_parser.add_argument('--output', required=True, help='输出文件路径')
    create_parser.set_defaults(func=create_canvas)
    
    # 创建示例配置文件命令
    config_parser = subparsers.add_parser('create-example-config', help='创建示例配置文件')
    config_parser.add_argument('--output', default='example_config.json', help='输出文件路径 (默认: example_config.json)')
    config_parser.set_defaults(func=create_example_config)
    
    # 解析命令行参数
    args = parser.parse_args()
    
    if hasattr(args, 'func'):
        args.func(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()