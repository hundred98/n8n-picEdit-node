#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
路径处理工具模块
处理中文路径和图片文件打开的相关问题
"""

import os
import sys
from PIL import Image


def normalize_path(path_str):
    """
    规范化路径，处理中文字符
    """
    if not path_str:
        return path_str
    
    try:
        # 确保路径是字符串类型
        if not isinstance(path_str, str):
            path_str = str(path_str)
        
        # 规范化路径分隔符
        normalized_path = os.path.normpath(path_str)
        
        # 在Windows系统下，确保路径编码正确
        if sys.platform.startswith('win'):
            # 尝试使用短路径名来避免中文路径问题
            try:
                import ctypes
                from ctypes import wintypes
                
                # 获取短路径名
                GetShortPathNameW = ctypes.windll.kernel32.GetShortPathNameW
                GetShortPathNameW.argtypes = [wintypes.LPCWSTR, wintypes.LPWSTR, wintypes.DWORD]
                GetShortPathNameW.restype = wintypes.DWORD
                
                # 检查文件是否存在
                if os.path.exists(normalized_path):
                    # 分配缓冲区
                    buffer_size = 260  # MAX_PATH
                    buffer = ctypes.create_unicode_buffer(buffer_size)
                    
                    # 获取短路径
                    result = GetShortPathNameW(normalized_path, buffer, buffer_size)
                    if result > 0 and result < buffer_size:
                        short_path = buffer.value
                        if short_path and os.path.exists(short_path):
                            return short_path
            except Exception:
                # 如果获取短路径失败，继续使用原路径
                pass
        
        return normalized_path
    except Exception as e:
        print(f"Warning: Path normalization failed for '{path_str}': {e}", file=sys.stderr)
        return path_str


def safe_image_open(image_path):
    """
    安全地打开图片文件，处理中文路径问题
    """
    try:
        # 首先尝试直接打开
        return Image.open(image_path)
    except Exception as e:
        # 如果直接打开失败，尝试使用规范化路径
        try:
            normalized_path = normalize_path(image_path)
            return Image.open(normalized_path)
        except Exception as e2:
            # 如果仍然失败，在Windows下尝试使用原始字节方式
            if sys.platform.startswith('win'):
                try:
                    # 使用二进制模式读取文件，然后用BytesIO包装
                    import io
                    with open(image_path, 'rb') as f:
                        return Image.open(io.BytesIO(f.read()))
                except Exception as e3:
                    pass
            
            # 所有方法都失败，抛出最后一个异常
            raise e2