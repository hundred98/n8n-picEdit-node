#!/usr/bin/env python3
"""
音标测试脚本，专门测试各种音标字符的显示
"""

import sys
import os

# 添加上级目录到Python路径，以便导入canvas_generator
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from canvas_generator import Canvas

def test_diacritics():
    """测试各种音标字符"""
    print("创建音标测试...")
    
    # 创建画布
    canvas = Canvas(1000, 800, background_color="white")
    
    # 添加标题
    canvas.add_text(
        position=(500, 50),
        text="音标字符测试",
        font_size=40,
        color="darkblue",
        alignment="center"
    )
    
    # 测试拉丁字母变音符号
    canvas.add_text(
        position=(500, 120),
        text="拉丁字母变音符号:",
        font_size=24,
        color="black",
        alignment="center"
    )
    
    canvas.add_text(
        position=(500, 160),
        text="ÀÁÂÃÄÅÆÇÈÉÊËÌÍÎÏÐÑÒÓÔÕÖØÙÚÛÜÝÞßàáâãäåæçèéêëìíîïðñòóôõöøùúûüýþÿ",
        font_size=20,
        color="darkred",
        alignment="center"
    )
    
    # 测试重音符号
    canvas.add_text(
        position=(500, 220),
        text="重音符号示例:",
        font_size=24,
        color="black",
        alignment="center"
    )
    
    canvas.add_text(
        position=(500, 260),
        text="ČčĎďĚěĞğŇňŘřŠšŤťŮůŽž",
        font_size=20,
        color="darkgreen",
        alignment="center"
    )
    
    # 测试西里尔字母
    canvas.add_text(
        position=(500, 320),
        text="西里尔字母:",
        font_size=24,
        color="black",
        alignment="center"
    )
    
    canvas.add_text(
        position=(500, 360),
        text="АБВГДЕЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯабвгдежзийклмнопрстуфхцчшщъыьэюя",
        font_size=20,
        color="purple",
        alignment="center"
    )
    
    # 测试IPA音标
    canvas.add_text(
        position=(500, 420),
        text="IPA音标示例:",
        font_size=24,
        color="black",
        alignment="center"
    )
    
    canvas.add_text(
        position=(500, 460),
        text="θ ð ʃ ʒ ŋ ɡ ʔ ʍ ɾ ɽ ɸ β ɦ ɣ ɰ ɹ ɻ ɭ ʎ ʟ ʦ ʣ ʧ ʤ ʘ ǀ ǂ ǁ ǂ ǃ ʘ ǁ",
        font_size=20,
        color="orange",
        alignment="center"
    )
    
    # 测试其他特殊字符
    canvas.add_text(
        position=(500, 520),
        text="其他特殊字符:",
        font_size=24,
        color="black",
        alignment="center"
    )
    
    canvas.add_text(
        position=(500, 560),
        text="€£¥¢©®™§¶†‡•‰‱′″‴‹›«»",
        font_size=20,
        color="darkcyan",
        alignment="center"
    )
    
    # 保存图像
    canvas.save("diacritics_test_output.png")
    print("音标测试完成，结果保存为 diacritics_test_output.png")

def main():
    """主函数"""
    print("开始音标字符测试...")
    test_diacritics()
    print("测试结束!")

if __name__ == "__main__":
    main()