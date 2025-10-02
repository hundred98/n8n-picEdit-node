#!/usr/bin/env python3
"""
Test script for wrapper.py
"""

import json
import subprocess
import sys
import os

# Add the parent directory to the Python path to import canvas_generator
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from canvas_generator import Canvas


def test_basic_config():
    """Test basic configuration mode"""
    print("Testing basic configuration mode...")
    
    config = {
        "mode": "config",
        "canvas": {
            "width": 600,
            "height": 400,
            "backgroundColor": "lightblue"
        },
        "elements": [
            {
                "type": "text",
                "position": [300, 50],
                "text": "Hello, World!",
                "fontSize": 36,
                "color": "darkblue",
                "alignment": "center"
            },
            {
                "type": "text",
                "position": [300, 120],
                "text": "This is a test image",
                "fontSize": 24,
                "color": "black",
                "alignment": "center"
            }
        ],
        "outputPath": "./test/output_basic.png"
    }
    
    # Run the wrapper script
    result = run_wrapper(config)
    print(f"Result: {result}")
    return result


def test_image_elements():
    """Test with image elements"""
    print("\nTesting with image elements...")
    
    # First create a simple test image
    create_test_image()
    
    config = {
        "mode": "config",
        "canvas": {
            "width": 600,
            "height": 400,
            "backgroundColor": "white"
        },
        "elements": [
            {
                "type": "text",
                "position": [300, 50],
                "text": "Image Test",
                "fontSize": 36,
                "color": "darkblue",
                "alignment": "center"
            },
            {
                "type": "image",
                "position": [200, 150],
                "imagePath": "./test/test_image.png",
                "scale": 0.5,
                "rotation": 15
            }
        ],
        "outputPath": "./test/output_with_image.png"
    }
    
    # Run the wrapper script
    result = run_wrapper(config)
    print(f"Result: {result}")
    return result


def test_template_mode():
    """Test template mode"""
    print("\nTesting template mode...")
    
    config = {
        "mode": "template",
        "templateName": "简单卡片",
        "templatesDir": "../../templates",
        "outputPath": "./test/output_from_template.png",
        "customizations": {
            "elements": [
                {"text": "Custom Title"},
                {"text": "Custom content from test", "color": "red"}
            ]
        }
    }
    
    # Run the wrapper script
    result = run_wrapper(config)
    print(f"Result: {result}")
    return result


def create_test_image():
    """Create a simple test image for overlay testing"""
    from PIL import Image, ImageDraw
    
    # Create a simple test image
    img = Image.new('RGB', (100, 100), color='lightgreen')
    d = ImageDraw.Draw(img)
    d.text((10, 10), "Test", fill='black')
    
    # Save the test image
    img.save("./test/test_image.png")
    print("Created test image: ./test/test_image.png")


def run_wrapper(config):
    """Run the wrapper script with given config"""
    try:
        # Convert config to JSON string
        config_json = json.dumps(config)
        
        # Run the wrapper script as a subprocess
        wrapper_script = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'wrapper.py')
        
        # Use shell=False for better cross-platform compatibility
        process = subprocess.Popen(
            [sys.executable, wrapper_script],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # Set working directory to python folder
        )
        
        # Send input and get output
        stdout, stderr = process.communicate(input=config_json)
        
        # Print debug information
        print(f"Subprocess return code: {process.returncode}")
        print(f"Subprocess stdout: {stdout}")
        if stderr:
            print(f"Subprocess stderr: {stderr}")
        
        if process.returncode == 0:
            if stdout.strip():
                # Extract JSON from output (in case there are other messages)
                lines = stdout.strip().split('\n')
                json_line = None
                for line in reversed(lines):  # Look for JSON from the end
                    line = line.strip()
                    if line.startswith('{') and line.endswith('}'):
                        try:
                            json.loads(line)
                            json_line = line
                            break
                        except json.JSONDecodeError:
                            continue
                
                if json_line:
                    try:
                        result = json.loads(json_line)
                        return result
                    except json.JSONDecodeError:
                        return {
                            "success": False,
                            "error": f"Failed to parse JSON output: {json_line}"
                        }
                else:
                    return {
                        "success": False,
                        "error": f"No valid JSON found in output: {stdout}"
                    }
            else:
                return {
                    "success": False,
                    "error": "No output from wrapper script"
                }
        else:
            return {
                "success": False,
                "error": stderr or "Process failed with return code != 0"
            }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def main():
    """Main test function"""
    print("Running wrapper tests...")
    
    # Make sure test output directory exists
    test_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'test')
    os.makedirs(test_dir, exist_ok=True)
    
    # Run tests
    result1 = test_basic_config()
    result2 = test_image_elements()
    result3 = test_template_mode()
    
    print("\n" + "="*50)
    print("Test Summary:")
    print("="*50)
    print(f"Basic Config Test: {'PASS' if result1.get('success') else 'FAIL'}")
    print(f"Image Elements Test: {'PASS' if result2.get('success') else 'FAIL'}")
    print(f"Template Mode Test: {'PASS' if result3.get('success') else 'FAIL'}")


if __name__ == "__main__":
    main()