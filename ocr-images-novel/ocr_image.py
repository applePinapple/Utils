#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OCR图片文字提取脚本
支持长图片文字识别
"""

import sys
from pathlib import Path

def ocr_with_easyocr(image_path, output_file=None):
    """
    使用 EasyOCR 进行文字识别
    需要安装: pip install easyocr --break-system-packages
    优点: 安装简单,不需要额外系统依赖,准确率较高
    """
    try:
        import easyocr
    except ImportError:
        print("错误: 缺少 easyocr 库")
        print("请运行: pip install easyocr --break-system-packages")
        return None
    
    print(f"正在使用 EasyOCR 读取图片: {image_path}")
    print("首次运行会下载模型文件,请稍候...")
    
    # 创建reader,支持中文和英文
    reader = easyocr.Reader(['ch_sim', 'en'], gpu=False)
    
    # 进行OCR识别
    results = reader.readtext(image_path)
    
    # 提取文字
    text_lines = []
    for (bbox, text, prob) in results:
        text_lines.append(text)
    
    full_text = '\n'.join(text_lines)
    
    print(f"\n识别完成,共提取 {len(results)} 行文字\n")
    print("=" * 50)
    print(full_text)
    print("=" * 50)
    
    # 保存到文件
    if output_file:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(full_text)
        print(f"\n结果已保存到: {output_file}")
    
    return full_text


def main():
    if len(sys.argv) < 2:
        print("用法: python ocr_image.py <图片路径> [输出文件]")
        print("\n示例:")
        print("  python ocr_image.py image.png")
        print("  python ocr_image.py image.png output.txt")
        sys.exit(1)
    
    image_path = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    if not Path(image_path).exists():
        print(f"错误: 图片文件不存在: {image_path}")
        sys.exit(1)
    
    # 如果没有指定输出文件,自动生成
    if not output_file:
        output_file = Path(image_path).stem + '_ocr.txt'
    
    ocr_with_easyocr(image_path, output_file)


if __name__ == '__main__':
    main()
