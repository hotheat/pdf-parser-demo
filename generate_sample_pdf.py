#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from pathlib import Path
import tempfile
import logging
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from PIL import Image as PILImage
import numpy as np

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 尝试注册中文字体
try:
    # 在不同操作系统上查找中文字体
    font_paths = [
        # macOS
        "/System/Library/Fonts/PingFang.ttc",
        # Windows
        "C:/Windows/Fonts/simhei.ttf",
        # Linux
        "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc"
    ]
    
    font_registered = False
    for font_path in font_paths:
        if os.path.exists(font_path):
            try:
                pdfmetrics.registerFont(TTFont('Chinese', font_path))
                font_registered = True
                break
            except Exception as e:
                logger.warning(f"注册字体失败: {str(e)}")
    
    if not font_registered:
        logger.warning("未能找到合适的中文字体，将使用默认字体")
except Exception as e:
    logger.warning(f"字体注册过程出错: {str(e)}")

def generate_sample_image(width=400, height=300):
    """生成示例图片"""
    # 创建一个彩色渐变图像
    array = np.zeros((height, width, 3), dtype=np.uint8)
    
    # 创建渐变效果
    for i in range(height):
        for j in range(width):
            array[i, j, 0] = int(255 * i / height)  # 红色分量
            array[i, j, 1] = int(255 * j / width)   # 绿色分量
            array[i, j, 2] = int(255 * (i + j) / (height + width))  # 蓝色分量
    
    # 创建PIL图像
    image = PILImage.fromarray(array)
    
    # 保存到临时文件
    temp_dir = tempfile.mkdtemp()
    image_path = os.path.join(temp_dir, "sample_image.png")
    image.save(image_path)
    
    return image_path

def generate_sample_pdf(output_path="sample.pdf"):
    """生成示例PDF文件，包含文本、表格和图片"""
    logger.info(f"开始生成示例PDF: {output_path}")
    
    # 创建PDF文档
    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=72
    )
    
    # 获取样式
    styles = getSampleStyleSheet()
    
    # 创建中文样式
    if 'Chinese' in pdfmetrics.getRegisteredFontNames():
        chinese_style = ParagraphStyle(
            'ChineseStyle',
            parent=styles['Normal'],
            fontName='Chinese',
            fontSize=12,
            leading=14
        )
    else:
        chinese_style = styles['Normal']
    
    # 创建内容列表
    content = []
    
    # 添加标题
    title_style = styles['Title']
    content.append(Paragraph("PDF解析工具示例文档", title_style))
    content.append(Spacer(1, 20))
    
    # 添加中文段落
    content.append(Paragraph("这是一个用于测试PDF解析工具的示例文档。", chinese_style))
    content.append(Paragraph("它包含了文本、表格和图片等不同类型的内容。", chinese_style))
    content.append(Spacer(1, 10))
    
    # 添加英文段落
    content.append(Paragraph("This is a sample document for testing the PDF parsing tool.", styles['Normal']))
    content.append(Paragraph("It contains different types of content including text, tables, and images.", styles['Normal']))
    content.append(Spacer(1, 20))
    
    # 添加子标题
    content.append(Paragraph("1. 文本内容示例", styles['Heading2']))
    content.append(Spacer(1, 10))
    
    # 添加更多文本
    lorem_ipsum = """
    Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec a diam lectus. Sed sit amet ipsum mauris. 
    Maecenas congue ligula ac quam viverra nec consectetur ante hendrerit. Donec et mollis dolor. 
    Praesent et diam eget libero egestas mattis sit amet vitae augue. Nam tincidunt congue enim, 
    ut porta lorem lacinia consectetur. Donec ut libero sed arcu vehicula ultricies a non tortor. 
    Lorem ipsum dolor sit amet, consectetur adipiscing elit. Aenean ut gravida lorem. 
    Ut turpis felis, pulvinar a semper sed, adipiscing id dolor.
    """
    content.append(Paragraph(lorem_ipsum, styles['Normal']))
    content.append(Spacer(1, 20))
    
    # 添加中文文本
    chinese_text = """
    中文文本示例：这是一段中文文本，用于测试PDF解析工具对中文的支持情况。
    PDF解析工具应该能够正确提取这段文本，并保持其格式和内容的完整性。
    这段文本包含了标点符号、数字123和英文字母ABC等不同类型的字符。
    """
    content.append(Paragraph(chinese_text, chinese_style))
    content.append(Spacer(1, 20))
    
    # 添加表格标题
    content.append(Paragraph("2. 表格示例", styles['Heading2']))
    content.append(Spacer(1, 10))
    
    # 创建表格数据
    table_data = [
        ['ID', '姓名', '年龄', '职业'],
        ['001', '张三', '28', '工程师'],
        ['002', '李四', '32', '设计师'],
        ['003', '王五', '45', '经理'],
        ['004', '赵六', '36', '销售'],
        ['005', '钱七', '29', '开发者']
    ]
    
    # 创建表格
    table = Table(table_data, colWidths=[80, 100, 80, 100])
    
    # 设置表格样式
    table_style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ])
    table.setStyle(table_style)
    
    content.append(table)
    content.append(Spacer(1, 20))
    
    # 添加另一个表格（数字数据）
    content.append(Paragraph("数据统计表格：", styles['Normal']))
    content.append(Spacer(1, 10))
    
    # 创建数据表格
    data_table = [
        ['季度', '销售额 (万元)', '增长率 (%)', '市场份额 (%)'],
        ['Q1 2024', '256.8', '12.5', '23.6'],
        ['Q2 2024', '312.4', '21.7', '25.8'],
        ['Q3 2024', '287.3', '-8.0', '24.2'],
        ['Q4 2024', '342.1', '19.1', '26.5'],
        ['总计', '1198.6', '11.3', '25.0']
    ]
    
    # 创建表格
    data_table_obj = Table(data_table, colWidths=[80, 100, 80, 100])
    
    # 设置表格样式
    data_table_style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.blue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ])
    data_table_obj.setStyle(data_table_style)
    
    content.append(data_table_obj)
    content.append(Spacer(1, 20))
    
    # 添加图片标题
    content.append(Paragraph("3. 图片示例", styles['Heading2']))
    content.append(Spacer(1, 10))
    
    # 生成并添加图片
    image_path = generate_sample_image()
    img = Image(image_path, width=400, height=300)
    content.append(img)
    content.append(Spacer(1, 10))
    content.append(Paragraph("图1：示例图片 - 彩色渐变", styles['Normal']))
    content.append(Spacer(1, 20))
    
    # 添加结束语
    content.append(Paragraph("这个PDF文件包含了文本、表格和图片等不同类型的内容，可以用来测试PDF解析工具的各种功能。", chinese_style))
    content.append(Spacer(1, 10))
    content.append(Paragraph("如果您能看到这段文字，说明PDF已经成功生成。", chinese_style))
    
    # 构建PDF文档
    doc.build(content)
    
    # 清理临时文件
    if os.path.exists(image_path):
        try:
            os.remove(image_path)
            os.rmdir(os.path.dirname(image_path))
        except Exception as e:
            logger.warning(f"清理临时文件失败: {str(e)}")
    
    logger.info(f"示例PDF生成完成: {output_path}")
    return output_path

if __name__ == "__main__":
    output_file = "sample.pdf"
    generate_sample_pdf(output_file)
    print(f"示例PDF已生成: {os.path.abspath(output_file)}")