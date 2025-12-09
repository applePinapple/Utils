# OCR 图片文字提取工具使用说明

## 三种OCR方案对比

### 1. EasyOCR (⭐推荐)
- **优点**: 
  - 安装简单,无需额外系统依赖
  - 中文识别准确率高
  - 支持长图片
  - 自动下载模型
- **缺点**: 首次运行需要下载模型(约100MB)
- **安装**: `pip install easyocr --break-system-packages`

### 2. PaddleOCR
- **优点**: 
  - 中文识别准确率最高
  - 国产开源,针对中文优化
- **缺点**: 依赖较多,包体积较大
- **安装**: `pip install paddlepaddle paddleocr --break-system-packages`

### 3. Tesseract OCR
- **优点**: 
  - 老牌OCR引擎,社区支持好
- **缺点**: 
  - 需要安装系统级依赖
  - 中文识别准确率相对较低
- **安装**: 
  ```bash
  # Ubuntu/Debian
  sudo apt-get install tesseract-ocr tesseract-ocr-chi-sim
  pip install pytesseract pillow --break-system-packages
  ```

## 快速开始

### 方案一: 使用简化脚本 (推荐新手)

1. **安装依赖**:
   ```bash
   pip install easyocr --break-system-packages
   ```

2. **修改脚本**:
   打开 `ocr_simple.py`,将 `image_path` 改为你的图片路径:
   ```python
   image_path = '你的图片.png'
   ```

3. **运行**:
   ```bash
   python ocr_simple.py
   ```

### 方案二: 使用完整脚本 (支持多种OCR引擎)

1. **安装依赖** (选择一种):
   ```bash
   # 选择 EasyOCR (推荐)
   pip install easyocr --break-system-packages
   
   # 或选择 PaddleOCR
   pip install paddlepaddle paddleocr --break-system-packages
   
   # 或选择 Tesseract
   sudo apt-get install tesseract-ocr tesseract-ocr-chi-sim
   pip install pytesseract pillow --break-system-packages
   ```

2. **运行**:
   ```bash
   # 使用 EasyOCR (推荐)
   python ocr_image.py your_image.png output.txt easyocr
   
   # 使用 PaddleOCR
   python ocr_image.py your_image.png output.txt paddleocr
   
   # 使用 Tesseract
   python ocr_image.py your_image.png output.txt tesseract
   ```

## 针对你的长图片 (1920×5986)

你的图片尺寸较大,所有三种方案都能处理,但推荐:

1. **EasyOCR** - 最佳平衡,准确率高且易用
2. **PaddleOCR** - 如果需要最高的中文识别准确率

### 示例命令:

```bash
# 1. 安装 EasyOCR
pip install easyocr --break-system-packages

# 2. 运行OCR
python ocr_image.py 你的长图片.png 提取的文字.txt easyocr
```

## 注意事项

1. **首次运行**: EasyOCR 和 PaddleOCR 首次运行会下载模型文件,需要等待
2. **内存占用**: 长图片OCR会占用较多内存,建议至少2GB可用内存
3. **识别时间**: 1920×5986的图片大约需要1-3分钟完成识别
4. **输出格式**: 识别结果会按照文本块的顺序输出,每行一个文本块

## 常见问题

**Q: 识别准确率不高怎么办?**
A: 
- 确保图片清晰,分辨率足够
- 尝试不同的OCR引擎
- 图片中的文字应该水平方向,避免倾斜

**Q: 某些文字识别不出来?**
A: 
- 检查图片中的文字是否过小或模糊
- 尝试使用 PaddleOCR,它对中文的识别率更高

**Q: 脚本运行很慢?**
A: 这是正常的,长图片OCR需要较长时间,请耐心等待

## 输出示例

运行后,文字会:
1. 在控制台显示
2. 保存到指定的文本文件中 (默认: `output.txt`)

每个文本块占一行,按照图片中从上到下的顺序排列。
