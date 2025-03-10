#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import tempfile
from pathlib import Path
import ocrmypdf
from unstructured.partition.pdf import partition_pdf
from pdfminer.high_level import extract_text
import fitz  # PyMuPDF
import pandas as pd
from pdf2image import convert_from_path
import tabula
from PIL import Image
import subprocess
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PDFParser:
    def __init__(self, pdf_path):
        """初始化 PDF 解析器
        
        Args:
            pdf_path (str): PDF 文件路径
        """
        self.pdf_path = Path(pdf_path)
        if not self.pdf_path.exists():
            raise FileNotFoundError(f"PDF文件不存在: {pdf_path}")
        
        self.temp_dir = Path(tempfile.mkdtemp())
        self.ocr_path = self.temp_dir / f"ocr_{self.pdf_path.name}"

    def perform_ocr(self):
        """对 PDF 执行 OCR 处理"""
        logger.info("开始执行 OCR 处理...")
        try:
            # 使用 ocrmypdf 进行 OCR
            ocrmypdf.ocr(
                input_file=str(self.pdf_path),
                output_file=str(self.ocr_path),
                language='chi_sim+eng',  # 支持中文和英文
                skip_text=True,  # 跳过已有文本的页面
                force_ocr=False,
                progress_bar=False
            )
            logger.info("OCR 处理完成")
            return str(self.ocr_path)
        except Exception as e:
            logger.error(f"OCR 处理失败: {str(e)}")
            return str(self.pdf_path)

    def extract_text_with_pdfminer(self):
        """使用 pdfminer 提取文本"""
        logger.info("使用 PDFMiner 提取文本...")
        try:
            text = extract_text(self.pdf_path)
            return text
        except Exception as e:
            logger.error(f"文本提取失败: {str(e)}")
            return ""

    def extract_images(self):
        """提取 PDF 中的图片"""
        logger.info("开始提取图片...")
        images_dir = self.temp_dir / "images"
        images_dir.mkdir(exist_ok=True)
        
        try:
            doc = fitz.open(self.pdf_path)
            image_count = 0
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                image_list = page.get_images()
                
                for img_index, img in enumerate(image_list):
                    xref = img[0]
                    base_image = doc.extract_image(xref)
                    image_bytes = base_image["image"]
                    
                    image_filename = images_dir / f"image_p{page_num+1}_{img_index+1}.{base_image['ext']}"
                    with open(image_filename, "wb") as img_file:
                        img_file.write(image_bytes)
                    image_count += 1
                    
                    # 使用 GraphicsMagick 优化图片
                    self._optimize_image(image_filename)
            
            logger.info(f"成功提取 {image_count} 张图片到 {images_dir}")
            return images_dir
        except Exception as e:
            logger.error(f"图片提取失败: {str(e)}")
            return None

    def _optimize_image(self, image_path):
        """使用 GraphicsMagick 优化图片"""
        try:
            # 调整图片大小和质量
            subprocess.run([
                'gm', 'convert', str(image_path),
                '-strip', '-quality', '85',
                str(image_path)
            ], check=True)
        except Exception as e:
            logger.warning(f"图片优化失败: {str(e)}")

    def extract_tables(self):
        """提取 PDF 中的表格"""
        logger.info("开始提取表格...")
        try:
            # 使用 tabula-py 提取表格
            tables = tabula.read_pdf(
                str(self.pdf_path),
                pages='all',
                multiple_tables=True,
                guess=True
            )
            
            # 保存表格到 Excel 文件
            if tables:
                excel_path = self.temp_dir / f"tables_{self.pdf_path.stem}.xlsx"
                with pd.ExcelWriter(excel_path) as writer:
                    for i, table in enumerate(tables, 1):
                        table.to_excel(writer, sheet_name=f'Table_{i}', index=False)
                logger.info(f"成功提取 {len(tables)} 个表格到 {excel_path}")
                return excel_path
            return None
        except Exception as e:
            logger.error(f"表格提取失败: {str(e)}")
            return None

    def extract_structured_content(self):
        """使用 unstructured 提取结构化内容"""
        logger.info("开始提取结构化内容...")
        try:
            elements = partition_pdf(
                filename=str(self.pdf_path),
                strategy="fast"
            )
            return elements
        except Exception as e:
            logger.error(f"结构化内容提取失败: {str(e)}")
            return []

    def cleanup(self):
        """清理临时文件"""
        try:
            import shutil
            shutil.rmtree(self.temp_dir)
            logger.info("临时文件清理完成")
        except Exception as e:
            logger.error(f"临时文件清理失败: {str(e)}")

def main():
    # 使用示例
    pdf_path = "example.pdf"  # 替换为实际的 PDF 文件路径
    
    try:
        parser = PDFParser(pdf_path)
        
        # 执行 OCR
        ocr_pdf = parser.perform_ocr()
        
        # 提取文本
        text = parser.extract_text_with_pdfminer()
        print("提取的文本:", text[:500] + "..." if text else "无文本内容")
        
        # 提取图片
        images_dir = parser.extract_images()
        if images_dir:
            print(f"图片已保存到: {images_dir}")
        
        # 提取表格
        tables_path = parser.extract_tables()
        if tables_path:
            print(f"表格已保存到: {tables_path}")
        
        # 提取结构化内容
        elements = parser.extract_structured_content()
        print(f"提取到 {len(elements)} 个结构化内容元素")
        
        # 清理临时文件
        parser.cleanup()
        
    except Exception as e:
        print(f"处理过程中出现错误: {str(e)}")

if __name__ == "__main__":
    main()