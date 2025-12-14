#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OCR图片文字提取脚本 - 优化版
专门针对长图片进行优化处理
"""

import sys
import os
import tempfile
from pathlib import Path
from PIL import Image
import numpy as np

def split_long_image(image_path, chunk_height=2000, overlap=200):
    """
    将长图片分割成多个重叠的块
    
    Args:
        image_path: 图片路径
        chunk_height: 每块的高度
        overlap: 块之间的重叠像素，用于避免文字被切断
    
    Returns:
        切割后的图片块列表和对应的y坐标
    """
    img = Image.open(image_path)
    width, height = img.size
    
    print(f"原始图片尺寸: {width}×{height}")
    
    chunks = []
    positions = []
    
    y = 0
    chunk_index = 0
    while y < height:
        # 计算当前块的范围
        y_end = min(y + chunk_height, height)
        
        # 裁剪图片块
        chunk = img.crop((0, y, width, y_end))
        chunks.append(chunk)
        positions.append(y)
        
        chunk_index += 1
        print(f"切割块 {chunk_index}: y={y} 到 y={y_end}, 高度={y_end-y}")
        
        # 移动到下一块，考虑重叠
        if y_end >= height:
            break
        y = y_end - overlap
    
    print(f"共切割成 {len(chunks)} 块\n")
    return chunks, positions, img.size


def preprocess_image(img, enhance=True):
    """
    图片预处理：增强对比度、二值化等
    
    Args:
        img: PIL Image对象
        enhance: 是否进行增强处理
    """
    if not enhance:
        return img
    
    from PIL import ImageEnhance, ImageFilter
    
    # 转换为灰度图
    img = img.convert('L')
    
    # 增强对比度
    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(2.0)
    
    # 锐化
    img = img.filter(ImageFilter.SHARPEN)
    
    return img


def remove_duplicate_lines(lines, positions, overlap=200):
    """
    去除重叠区域的重复文本
    
    Args:
        lines: 每个块识别出的文本行列表
        positions: 每个块的y坐标
        overlap: 重叠像素
    """
    if len(lines) <= 1:
        return lines[0] if lines else []
    
    result = []
    result.extend(lines[0])  # 第一块全部保留
    
    for i in range(1, len(lines)):
        current_lines = lines[i]
        
        # 估算重叠区域的行数（粗略估计）
        overlap_lines = max(1, overlap // 30)  # 假设每行约30像素高
        
        # 跳过重叠区域的行
        result.extend(current_lines[overlap_lines:])
    
    return result


def ocr_with_easyocr_optimized(image_path, output_file=None, chunk_height=2000, 
                                 overlap=200, enhance=True):
    """
    使用 EasyOCR 进行优化的文字识别
    
    Args:
        image_path: 图片路径
        output_file: 输出文件路径
        chunk_height: 分块高度
        overlap: 重叠像素
        enhance: 是否进行图片增强
    """
    try:
        import easyocr
    except ImportError:
        print("错误: 缺少 easyocr 库")
        print("请运行: pip install easyocr --break-system-packages")
        return None
    
    print(f"正在处理图片: {image_path}")
    print(f"配置: 块高度={chunk_height}, 重叠={overlap}, 增强={enhance}\n")
    
    # 分割长图片
    chunks, positions, original_size = split_long_image(image_path, chunk_height, overlap)
    
    # 创建reader
    print("初始化 EasyOCR (首次运行会下载模型)...")
    reader = easyocr.Reader(['ch_sim', 'en'], gpu=False)
    
    all_text_lines = []
    all_results = []
    
    # 逐块识别
    for i, chunk in enumerate(chunks):
        print(f"\n处理块 {i+1}/{len(chunks)}...")
        
        # 预处理
        if enhance:
            chunk = preprocess_image(chunk, enhance=True)
        
        # 保存临时图片用于识别
        fd, temp_path = tempfile.mkstemp(suffix=f"_chunk_{i}.png")
        os.close(fd)
        
        try:
            chunk.save(temp_path)
            
            # OCR识别
            results = reader.readtext(temp_path, paragraph=False)
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)
        
        # 提取文字
        text_lines = [text for (bbox, text, prob) in results]
        all_text_lines.append(text_lines)
        all_results.extend(results)
        
        print(f"  识别到 {len(text_lines)} 行文字")
    
    # 去重处理
    print("\n合并结果并去除重复...")
    final_lines = remove_duplicate_lines(all_text_lines, positions, overlap)
    full_text = '\n'.join(final_lines)
    
    print(f"\n识别完成!")
    print(f"原始图片: {original_size[0]}×{original_size[1]}")
    print(f"共识别 {len(final_lines)} 行文字\n")
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
    使用 PaddleOCR 进行文字识别（替代方案）
    安装: pip install paddlepaddle paddleocr --break-system-packages
    优点: 对中文支持更好，识别速度快
    """
    try:
        from paddleocr import PaddleOCR
    except ImportError:
        print("错误: 缺少 paddleocr 库")
        print("请运行: pip install paddlepaddle paddleocr --break-system-packages")
        return None
    
    print(f"正在使用 PaddleOCR 读取图片: {image_path}")
    
    # 初始化PaddleOCR
    ocr = PaddleOCR(use_angle_cls=True, lang='ch', show_log=False)
    
    # 进行OCR识别
    result = ocr.ocr(image_path, cls=True)
    
    # 提取文字
    text_lines = []
    if result and result[0]:
        for line in result[0]:
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
    if len(sys.argv) < 3:
        print("用法: python ocr_image_multi.py <图片文件夹路径> <目标文件夹路径> [目标文件名称初始坐标] [选项]")
        print("示例: python ocr_image_multi.py ./images ./output 1 --paddle")
        print("\n参数:")
        print("  <图片文件夹路径>         包含图片的文件夹路径")
        print("  <目标文件夹路径>         结果输出文件夹路径")
        print("  [目标文件名称初始坐标]   输出文件名的起始数字 (默认: 1)，格式为 stage-{坐标}.txt")
        print("\n选项:")
        print("  --chunk-height <高度>    指定切片高度 (默认: 2000)")
        print("  --overlap <像素>         指定切片重叠像素 (默认: 200)")
        print("  --no-enhance             禁用图像增强预处理")
        print("  --paddle                 使用 PaddleOCR 引擎 (默认: EasyOCR)")
        sys.exit(1)
    
    input_folder = sys.argv[1]
    output_folder = sys.argv[2]
    
    if not Path(input_folder).exists():
        print(f"错误: 图片文件夹不存在: {input_folder}")
        sys.exit(1)
        
    # 创建输出文件夹
    if not Path(output_folder).exists():
        try:
            os.makedirs(output_folder)
            print(f"已创建输出文件夹: {output_folder}")
        except Exception as e:
            print(f"错误: 无法创建输出文件夹: {e}")
            sys.exit(1)

    # 解析初始坐标
    start_index = 1
    arg_idx = 3
    if len(sys.argv) > 3 and not sys.argv[3].startswith('--'):
        try:
            start_index = int(sys.argv[3])
            arg_idx = 4
        except ValueError:
            print(f"警告: 第三个参数 '{sys.argv[3]}' 不是有效的整数，将使用默认起始坐标 1")
            
    # 解析选项参数
    chunk_height = 2000
    overlap = 200
    enhance = True
    use_paddle = False
    
    i = arg_idx
    while i < len(sys.argv):
        arg = sys.argv[i]
        if arg == '--chunk-height' and i + 1 < len(sys.argv):
            chunk_height = int(sys.argv[i + 1])
            i += 2
        elif arg == '--overlap' and i + 1 < len(sys.argv):
            overlap = int(sys.argv[i + 1])
            i += 2
        elif arg == '--no-enhance':
            enhance = False
            i += 1
        elif arg == '--paddle':
            use_paddle = True
            i += 1
        else:
            print(f"忽略未知参数: {arg}")
            i += 1

    # 获取并排序图片文件
    supported_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.webp', '.tiff'}
    image_files = []
    for f in os.listdir(input_folder):
        if Path(f).suffix.lower() in supported_extensions:
            image_files.append(f)
    
    # 简单排序，如果需要更智能的数字排序可以后续优化
    image_files.sort()
    
    if not image_files:
        print(f"警告: 在 {input_folder} 中未找到支持的图片文件")
        sys.exit(0)
        
    print(f"找到 {len(image_files)} 张图片，准备处理...")
    print(f"输出目录: {output_folder}")
    print(f"起始文件名: stage-{start_index}.txt")
    print("-" * 50)
    
    # 循环处理图片
    current_index = start_index
    for idx, filename in enumerate(image_files):
        image_path = os.path.join(input_folder, filename)
        output_filename = f"stage-{current_index}.txt"
        output_path = os.path.join(output_folder, output_filename)
        
        print(f"\n[{idx+1}/{len(image_files)}] 正在处理: {filename} -> {output_filename}")
        
        try:
            if use_paddle:
                ocr_with_paddleocr(image_path, output_path)
            else:
                ocr_with_easyocr_optimized(image_path, output_path, chunk_height, overlap, enhance)
            
            print(f"完成: {output_filename}")
        except Exception as e:
            print(f"处理图片 {filename} 时发生错误: {e}")
            import traceback
            traceback.print_exc()
            
        current_index += 1
        
    print("\n" + "=" * 50)
    print("所有任务处理完成！")


if __name__ == '__main__':
    main()