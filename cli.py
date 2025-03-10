#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import argparse
import logging
from pathlib import Path
from pdf_parser import PDFParser

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description='PDF解析工具命令行界面')
    parser.add_argument('--input', '-i', required=True, help='输入PDF文件路径')
    parser.add_argument('--output', '-o', help='输出目录路径')
    parser.add_argument('--ocr', action='store_true', help='执行OCR处理')
    parser.add_argument('--extract-text', action='store_true', help='提取文本')
    parser.add_argument('--extract-images', action='store_true', help='提取图片')
    parser.add_argument('--extract-tables', action='store_true', help='提取表格')
    parser.add_argument('--extract-all', action='store_true', help='提取所有内容')
    parser.add_argument('--keep-temp', action='store_true', help='保留临时文件')
    parser.add_argument('--verbose', '-v', action='store_true', help='显示详细日志')
    
    return parser.parse_args()

def setup_output_dir(output_dir=None):
    """设置输出目录"""
    if output_dir:
        output_path = Path(output_dir)
    else:
        output_path = Path(os.getcwd()) / "pdf_output"
    
    output_path.mkdir(exist_ok=True, parents=True)
    return output_path

def save_text(text, output_dir, filename="extracted_text.txt"):
    """保存提取的文本到文件"""
    if not text:
        logger.warning("没有提取到文本内容")
        return None
    
    output_file = output_dir / filename
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(text)
    
    logger.info(f"文本已保存到: {output_file}")
    return output_file

def copy_files(src_dir, dst_dir):
    """复制文件到目标目录"""
    import shutil
    if not src_dir or not src_dir.exists():
        return
    
    # 确保目标目录存在
    dst_dir.mkdir(exist_ok=True, parents=True)
    
    # 复制所有文件
    for item in src_dir.glob("*"):
        if item.is_file():
            shutil.copy2(item, dst_dir / item.name)
    
    logger.info(f"文件已复制到: {dst_dir}")

def main():
    """主函数"""
    args = parse_args()
    
    # 设置日志级别
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # 检查输入文件
    input_path = Path(args.input)
    if not input_path.exists():
        logger.error(f"输入文件不存在: {input_path}")
        return 1
    
    # 设置输出目录
    output_dir = setup_output_dir(args.output)
    
    # 如果没有指定任何操作，默认执行所有操作
    if not any([args.ocr, args.extract_text, args.extract_images, args.extract_tables]):
        args.extract_all = True
    
    # 如果指定了提取所有内容，设置所有提取标志
    if args.extract_all:
        args.ocr = True
        args.extract_text = True
        args.extract_images = True
        args.extract_tables = True
    
    try:
        # 初始化解析器
        parser = PDFParser(input_path)
        
        # 执行OCR
        ocr_pdf_path = None
        if args.ocr:
            logger.info("执行OCR处理...")
            ocr_pdf_path = parser.perform_ocr()
            if ocr_pdf_path and Path(ocr_pdf_path).exists():
                # 复制OCR处理后的PDF到输出目录
                import shutil
                ocr_output = output_dir / f"ocr_{input_path.name}"
                shutil.copy2(ocr_pdf_path, ocr_output)
                logger.info(f"OCR处理后的PDF已保存到: {ocr_output}")
        
        # 提取文本
        if args.extract_text:
            logger.info("提取文本...")
            text = parser.extract_text_with_pdfminer()
            save_text(text, output_dir)
        
        # 提取图片
        if args.extract_images:
            logger.info("提取图片...")
            images_dir = parser.extract_images()
            if images_dir:
                # 复制图片到输出目录
                images_output = output_dir / "images"
                copy_files(images_dir, images_output)
        
        # 提取表格
        if args.extract_tables:
            logger.info("提取表格...")
            tables_path = parser.extract_tables()
            if tables_path and Path(tables_path).exists():
                # 复制表格到输出目录
                import shutil
                tables_output = output_dir / f"tables_{input_path.stem}.xlsx"
                shutil.copy2(tables_path, tables_output)
                logger.info(f"表格已保存到: {tables_output}")
        
        # 清理临时文件
        if not args.keep_temp:
            parser.cleanup()
        
        logger.info(f"所有处理完成，结果保存在: {output_dir}")
        return 0
    
    except Exception as e:
        logger.error(f"处理过程中出现错误: {str(e)}", exc_info=args.verbose)
        return 1

if __name__ == "__main__":
    exit(main())