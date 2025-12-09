#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OCR图片文字提取脚本
支持长图片文字识别
"""

import sys
from pathlib import Path

def ocr_with_pytesseract(image_path, output_file=None):
    """
    使用 pytesseract (Tesseract OCR) 进行文字识别
    需要安装: pip install pytesseract pillow --break-system-packages
    还需要系统安装 tesseract-ocr
    """
    try:
        import pytesseract
        from PIL import Image
    except ImportError:
        print("错误: 缺少依赖库")
        print("请运行: pip install pytesseract pillow --break-system-packages")
        print("并确保系统已安装 tesseract-ocr")
        return None
    
    print(f"正在使用 Tesseract OCR 读取图片: {image_path}")
    
    # 打开图片
    image = Image.open(image_path)
    print(f"图片尺寸: {image.size}")
    
    # 进行OCR识别,支持中文
    # lang='chi_sim' 是简体中文, 'eng' 是英文
    # 如果需要同时识别中英文,使用 'chi_sim+eng'
    text = pytesseract.image_to_string(image, lang='chi_sim+eng')
    
    print(f"\n识别完成,共提取 {len(text)} 个字符\n")
    print("=" * 50)
    print(text)
    print("=" * 50)
    
    # 保存到文件
    if output_file:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(text)
        print(f"\n结果已保存到: {output_file}")
    
    return text


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


def ocr_with_paddleocr(image_path, output_file=None):
    """
    使用 PaddleOCR 进行文字识别
    需要安装: pip install paddlepaddle paddleocr --break-system-packages
    优点: 中文识别准确率高,国产开源
    """
    try:
        from paddleocr import PaddleOCR
    except ImportError:
        print("错误: 缺少 paddleocr 库")
        print("请运行: pip install paddlepaddle paddleocr --break-system-packages")
        return None

    print(f"正在使用 PaddleOCR 读取图片: {image_path}")

    # 创建OCR对象
    # use_textline_orientation=True 用于文本方向检测
    ocr = PaddleOCR(use_textline_orientation=True, lang='ch')

    # 进行OCR识别
    # 修复: 使用 predict() 替代 ocr(), 移除 cls 参数
    result = ocr.predict(str(image_path))

    # 提取文字
    text_lines = []
    if result and result[0]:
        for line in result[0]:
            # line 的结构: [bbox, (text, confidence)]
            text_lines.append(line[1][0])

    full_text = '\n'.join(text_lines)

    print(f"\n识别完成,共提取 {len(text_lines)} 行文字\n")
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
        print("用法: python ocr_image.py <图片路径> [输出文件] [方法]")
        print("\n可选方法:")
        print("  tesseract  - 使用 Tesseract OCR (默认)")
        print("  easyocr    - 使用 EasyOCR (推荐)")
        print("  paddleocr  - 使用 PaddleOCR (中文准确率高)")
        print("\n示例:")
        print("  python ocr_image.py image.png")
        print("  python ocr_image.py image.png output.txt")
        print("  python ocr_image.py image.png output.txt easyocr")
        sys.exit(1)
    
    image_path = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 and not sys.argv[2] in ['tesseract', 'easyocr', 'paddleocr'] else None
    method = sys.argv[-1] if sys.argv[-1] in ['tesseract', 'easyocr', 'paddleocr'] else 'tesseract'
    
    if not Path(image_path).exists():
        print(f"错误: 图片文件不存在: {image_path}")
        sys.exit(1)
    
    # 如果没有指定输出文件,自动生成
    if not output_file:
        output_file = Path(image_path).stem + '_ocr.txt'
    
    print(f"使用方法: {method}")
    
    # 根据选择的方法进行OCR
    if method == 'easyocr':
        ocr_with_easyocr(image_path, output_file)
    elif method == 'paddleocr':
        ocr_with_paddleocr(image_path, output_file)
    else:
        ocr_with_pytesseract(image_path, output_file)


if __name__ == '__main__':
    main()
