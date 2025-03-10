# PDF 解析工具

这是一个功能强大的 PDF 解析工具，集成了多个优秀的开源库和工具，可以实现：
- PDF 文档的 OCR 处理
- 文本内容提取
- 图片提取和优化
- 表格识别和提取
- 结构化内容解析

## 环境要求

### Python 依赖
所有 Python 依赖都已在 `requirements.txt` 中列出，可以通过以下命令安装：
```bash
pip install -r requirements.txt
```

### 系统依赖
本工具依赖以下系统工具：
- Tesseract OCR (用于 OCR)
- GraphicsMagick (用于图片处理)
- Ghostscript (用于 PDF 处理)

在 macOS 上可以通过 Homebrew 安装这些依赖：
```bash
brew install tesseract
brew install graphicsmagick
brew install ghostscript
```

在 Linux 上可以通过 apt 安装：
```bash
sudo apt-get install tesseract-ocr
sudo apt-get install graphicsmagick
sudo apt-get install ghostscript
```

在 Windows 上，建议通过官方网站下载安装程序。

## 使用方法

### 命令行界面

```bash
# 基本用法
python cli.py --input your_pdf_file.pdf --output output_directory

# 指定操作
python cli.py --input your_pdf_file.pdf --output output_directory --ocr --extract-text --extract-images --extract-tables
```

### 图形界面

```bash
python main.py --gui
```

或者直接运行：

```bash
python gui.py
```

### 编程接口

```python
from pdf_parser import PDFParser

# 初始化解析器
parser = PDFParser("your_pdf_file.pdf")

# OCR 处理
ocr_pdf = parser.perform_ocr()

# 提取文本
text = parser.extract_text_with_pdfminer()

# 提取图片
images_dir = parser.extract_images()

# 提取表格
tables_path = parser.extract_tables()

# 提取结构化内容
elements = parser.extract_structured_content()

# 清理临时文件
parser.cleanup()
```

## 功能说明

### OCR 处理
使用 `ocrmypdf` 进行 OCR 处理，支持中英文识别。对于已有文本的页面会自动跳过，提高处理效率。

### 文本提取
使用 `pdfminer.six` 提取文本内容，保持文本的格式和顺序。

### 图片提取
使用 `PyMuPDF` 提取图片，并通过 GraphicsMagick 进行优化处理。

### 表格提取
使用 `tabula-py` 识别和提取表格，并将结果保存为 Excel 文件。

### 结构化内容
使用 `unstructured` 库进行结构化内容解析，可以识别文档的不同部分（标题、段落、列表等）。

## 生成示例 PDF

本工具提供了一个生成示例 PDF 的功能，可以用于测试：

```bash
python main.py --generate-sample --output sample.pdf
```

## 注意事项

1. 确保所有系统依赖都已正确安装
2. 对于大型 PDF 文件，处理可能需要较长时间
3. OCR 处理需要足够的系统内存
4. 图片和表格的提取效果可能受 PDF 文件质量影响

## 许可证

本项目采用 MIT 许可证。详见 [LICENSE](LICENSE) 文件。