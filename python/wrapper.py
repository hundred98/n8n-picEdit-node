from canvas_generator import Canvas
import sys
import json
import traceback
import os
import io
from path_utils import normalize_path

# 设置标准输出编码为UTF-8
if sys.platform == 'win32':
    # Windows平台设置控制台编码
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.detach())

def clean_error_message(message):
    """清理错误消息，处理中文字符编码问题"""
    try:
        # 确保消息是字符串类型
        if not isinstance(message, str):
            message = str(message)
        
        # 替换双反斜杠为单反斜杠
        cleaned = message.replace('\\\\', '\\')
        
        # 移除可能的编码错误字符
        cleaned = cleaned.replace('\udcae', '容')  # 修复常见的编码错误
        cleaned = cleaned.replace('\udcb9', '材')
        
        # 确保字符串是有效的UTF-8
        try:
            cleaned.encode('utf-8')
        except UnicodeEncodeError:
            # 如果编码失败，使用错误替换
            cleaned = cleaned.encode('utf-8', errors='replace').decode('utf-8')
        
        return cleaned
    except Exception as e:
        return f"Error processing message: {str(e)}"

def main():
    try:
        if len(sys.argv) < 2:
            print(json.dumps({"success": False, "error": "No command provided"}))
            return

        command = sys.argv[1]
        
        if command == "test_canvas_with_chinese_path":
            # 测试中文路径处理
            test_path = "E:\\测试\\中文目录\\test.png"
            normalized_path = normalize_path(test_path)
            print(json.dumps({
                "success": True, 
                "message": f"Path normalized: {test_path} -> {normalized_path}",
                "original": test_path,
                "normalized": normalized_path
            }))
            return
        
        # 解析参数
        if len(sys.argv) < 3:
            print(json.dumps({"success": False, "error": "Insufficient arguments"}))
            return
            
        params_json = sys.argv[2]
        params = json.loads(params_json)
        
        if command == "create_canvas":
            width = params.get('width', 800)
            height = params.get('height', 600)
            background_color = params.get('backgroundColor', '#FFFFFF')
            
            # 处理背景图片路径
            background_image = params.get('backgroundImage')
            if background_image:
                background_image = normalize_path(background_image)
            
            try:
                # 创建Canvas实例
                canvas = Canvas(width, height, background_color)
                
                # 如果有背景图片，设置背景图片
                if background_image:
                    canvas.set_background_image(background_image)
                
                # 渲染画布
                rendered_image = canvas.render(quiet=True)
                
                # 转换为base64
                import io
                import base64
                buffer = io.BytesIO()
                rendered_image.save(buffer, format='PNG')
                base64_string = base64.b64encode(buffer.getvalue()).decode('utf-8')
                
                result_data = {
                    "success": True,
                    "message": "Canvas created successfully",
                    "base64": base64_string,
                    "width": width,
                    "height": height
                }
                print(json.dumps(result_data, ensure_ascii=False))
                
            except Exception as e:
                error_msg = clean_error_message(str(e))
                result_data = {
                    "success": False,
                    "error": error_msg
                }
                print(json.dumps(result_data, ensure_ascii=False))
                
        elif command == "add_element":
            try:
                # 对于add_element，我们需要先有一个canvas实例
                width = params.get('width', 800)
                height = params.get('height', 600)
                background_color = params.get('backgroundColor', '#FFFFFF')
                canvas = Canvas(width, height, background_color)
                
                element_type = params.get('type')
                element_data = params.get('data', {})
                
                # 根据元素类型添加元素
                if element_type == 'text':
                    position = element_data.get('position', (0, 0))
                    text = element_data.get('text', '')
                    canvas.add_text(position, text, **{k: v for k, v in element_data.items() if k not in ['position', 'text']})
                elif element_type == 'image':
                    position = element_data.get('position', (0, 0))
                    image_path = element_data.get('path', '')
                    if image_path:
                        image_path = normalize_path(image_path)
                    canvas.add_image(position, image_path, **{k: v for k, v in element_data.items() if k not in ['position', 'path']})
                
                # 渲染画布
                rendered_image = canvas.render(quiet=True)
                
                # 转换为base64
                import io
                import base64
                buffer = io.BytesIO()
                rendered_image.save(buffer, format='PNG')
                base64_string = base64.b64encode(buffer.getvalue()).decode('utf-8')
                
                result_data = {
                    "success": True,
                    "message": "Element added successfully",
                    "base64": base64_string
                }
                print(json.dumps(result_data, ensure_ascii=False))
                
            except Exception as e:
                error_msg = clean_error_message(str(e))
                result_data = {
                    "success": False,
                    "error": error_msg
                }
                print(json.dumps(result_data, ensure_ascii=False))
        else:
            result_data = {"success": False, "error": f"Unknown command: {command}"}
            print(json.dumps(result_data, ensure_ascii=False))
            
    except Exception as e:
        error_msg = clean_error_message(str(e))
        result_data = {
            "success": False,
            "error": f"Wrapper error: {error_msg}",
            "traceback": traceback.format_exc()
        }
        print(json.dumps(result_data, ensure_ascii=False))

if __name__ == "__main__":
    main()