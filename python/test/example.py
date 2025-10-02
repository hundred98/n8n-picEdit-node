#!/usr/bin/env python3
"""
示例脚本，展示canvas_generator的所有功能
"""

import os
import sys

# 添加上级目录到Python路径，以便导入canvas_generator
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from canvas_generator import Canvas


def create_basic_example():
    """创建基本示例"""
    print("创建基本示例...")
    
    # 查找可用的中文字体
    chinese_font = find_chinese_font()
    
    # 创建画布
    canvas = Canvas(800, 600, background_color="lightblue")
    
    # 添加文字
    canvas.add_text(
        position=(400, 50),
        text="基本示例",
        font_size=48,
        color="darkblue",
        alignment="center",
        font_name=chinese_font
    )
    
    canvas.add_text(
        position=(400, 120),
        text="这是一个基本的文字示例",
        font_size=24,
        color="black",
        alignment="center",
        font_name=chinese_font
    )
    
    # 保存图像
    canvas.save("output_basic.png", quiet=True)
    print("基本示例已保存到 output_basic.png")


def create_advanced_example():
    """创建高级示例，包含旋转和透明度"""
    print("创建高级示例...")
    
    # 查找可用的中文字体
    chinese_font = find_chinese_font()
    
    # 创建画布
    canvas = Canvas(800, 600, background_color="white")
    
    # 添加普通文字
    canvas.add_text(
        position=(400, 50),
        text="高级示例",
        font_size=48,
        color="darkblue",
        alignment="center",
        font_name=chinese_font
    )
    
    # 添加旋转文字
    canvas.add_text(
        position=(200, 200),
        text="旋转文字 (45度)",
        font_size=32,
        color="red",
        rotation=45,
        alignment="center",
        font_name=chinese_font
    )
    
    # 添加半透明文字
    canvas.add_text(
        position=(600, 200),
        text="半透明文字",
        font_size=32,
        color="blue",
        opacity=128,  # 50% 透明度
        alignment="center",
        font_name=chinese_font
    )
    
    # 添加旋转且半透明的文字
    canvas.add_text(
        position=(400, 300),
        text="旋转且半透明",
        font_size=32,
        color="green",
        rotation=-30,
        opacity=192,  # 75% 不透明度
        alignment="center",
        font_name=chinese_font
    )
    
    # 保存图像
    canvas.save("output_advanced.png", quiet=True)
    print("高级示例已保存到 output_advanced.png")


def create_image_example():
    """创建包含图片的示例"""
    print("创建图片示例...")
    
    # 查找可用的中文字体
    chinese_font = find_chinese_font()
    
    # 创建画布
    canvas = Canvas(800, 600, background_color="lightyellow")
    
    # 添加标题
    canvas.add_text(
        position=(400, 50),
        text="图片示例",
        font_size=48,
        color="darkgreen",
        alignment="center",
        font_name=chinese_font
    )
    
    # 创建一个测试图片（如果不存在）
    create_test_image()
    
    # 添加普通图片
    canvas.add_image(
        position=(100, 150),
        image_path="test_image.png",
        scale=0.5
    )
    
    # 添加旋转图片
    canvas.add_image(
        position=(300, 150),
        image_path="test_image.png",
        scale=0.5,
        rotation=30
    )
    
    # 添加半透明图片
    canvas.add_image(
        position=(500, 150),
        image_path="test_image.png",
        scale=0.5,
        opacity=128  # 50% 透明度
    )
    
    # 添加旋转且半透明的图片
    canvas.add_image(
        position=(300, 350),
        image_path="test_image.png",
        scale=0.7,
        rotation=-45,
        opacity=192  # 75% 不透明度
    )
    
    # 保存图像
    canvas.save("output_with_images.png", quiet=True)
    print("图片示例已保存到 output_with_images.png")


def create_unicode_example():
    """创建Unicode字符示例，包括音标等特殊字符"""
    print("创建Unicode示例...")
    
    # 查找可用的中文字体（通常支持更多Unicode字符）
    chinese_font = find_chinese_font()
    
    # 创建画布
    canvas = Canvas(800, 600, background_color="lightgray")
    
    # 添加标题
    canvas.add_text(
        position=(400, 50),
        text="Unicode 字符示例",
        font_size=40,
        color="darkblue",
        alignment="center",
        font_name=chinese_font
    )
    
    # 添加音标字符示例
    canvas.add_text(
        position=(400, 120),
        text="音标示例: àáâãäåæçèéêëìíîïðñòóôõöøùúûüýþÿ",
        font_size=20,
        color="black",
        alignment="center",
        font_name=chinese_font
    )
    
    # 添加希腊字母示例
    canvas.add_text(
        position=(400, 170),
        text="希腊字母: Αα Ββ Γγ Δδ Εε Ζζ Ηη Θθ Ιι Κκ Λλ Μμ Νν Ξξ Οο Ππ Ρρ Σσ Ττ Υυ Φφ Χχ Ψψ Ωω",
        font_size=20,
        color="darkgreen",
        alignment="center",
        font_name=chinese_font
    )
    
    # 添加数学符号示例
    canvas.add_text(
        position=(400, 220),
        text="数学符号: ∀∂∃∅∇∈∉∋∏∑√∝∞∠∧∨∩∪∫∴∼≅≈≠≡≤≥",
        font_size=20,
        color="darkred",
        alignment="center",
        font_name=chinese_font
    )
    
    # 添加特殊符号示例
    canvas.add_text(
        position=(400, 270),
        text="特殊符号: ¡¢£¤¥¦§¨©ª«¬®¯°±²³´µ¶·¸¹º»¼½¾¿",
        font_size=20,
        color="purple",
        alignment="center",
        font_name=chinese_font
    )
    
    # 保存图像
    canvas.save("output_unicode.png", quiet=True)
    print("Unicode示例已保存到 output_unicode.png")


def create_test_image():
    """创建一个测试图片"""
    from PIL import Image, ImageDraw
    
    # 创建一个简单的测试图片
    img = Image.new('RGBA', (200, 200), (255, 200, 200, 255))
    draw = ImageDraw.Draw(img)
    
    # 绘制一个蓝色矩形
    draw.rectangle([50, 50, 150, 150], fill=(100, 100, 255, 255))
    
    # 绘制一个绿色圆圈
    draw.ellipse([75, 75, 125, 125], fill=(100, 255, 100, 255))
    
    # 保存图片
    img.save("test_image.png")


def find_chinese_font():
    """查找系统中的中文字体"""
    import platform
    
    system = platform.system()
    if system == "Windows":
        font_paths = [
            "C:/Windows/Fonts/msyh.ttc",      # 微软雅黑
            "C:/Windows/Fonts/simhei.ttf",    # 黑体
            "C:/Windows/Fonts/simsun.ttc",    # 宋体
            "C:/Windows/Fonts/msyhbd.ttc"     # 微软雅黑粗体
        ]
    elif system == "Darwin":  # macOS
        font_paths = [
            "/System/Library/Fonts/PingFang.ttc",
            "/System/Library/Fonts/STHeiti Light.ttc"
        ]
    else:  # Linux
        font_paths = [
            "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",
            "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc"
        ]
    
    for font_path in font_paths:
        if os.path.exists(font_path):
            return font_path
    
    return None


def main():
    """主函数"""
    print("开始运行示例脚本...")
    
    # 创建基本示例
    create_basic_example()
    
    # 创建高级示例
    create_advanced_example()
    
    # 创建图片示例
    create_image_example()
    
    # 创建Unicode示例（包含音标等特殊字符）
    create_unicode_example()
    
    print("所有示例已完成！")


if __name__ == "__main__":
    main()