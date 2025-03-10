#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import shutil
from pathlib import Path
import logging
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QFileDialog, QCheckBox, QProgressBar,
    QTextEdit, QTabWidget, QMessageBox, QGroupBox, QGridLayout
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QSize
from PyQt5.QtGui import QIcon, QPixmap, QFont

from pdf_parser import PDFParser

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WorkerThread(QThread):
    """工作线程，用于执行耗时操作"""
    update_progress = pyqtSignal(int, str)
    finished = pyqtSignal(dict)
    error = pyqtSignal(str)
    
    def __init__(self, pdf_path, output_dir, options):
        super().__init__()
        self.pdf_path = pdf_path
        self.output_dir = output_dir
        self.options = options
        self.results = {}
    
    def run(self):
        try:
            # 初始化解析器
            parser = PDFParser(self.pdf_path)
            
            # 执行OCR
            if self.options.get('ocr', False):
                self.update_progress.emit(10, "执行OCR处理...")
                ocr_pdf_path = parser.perform_ocr()
                if ocr_pdf_path and Path(ocr_pdf_path).exists():
                    # 复制OCR处理后的PDF到输出目录
                    ocr_output = self.output_dir / f"ocr_{Path(self.pdf_path).name}"
                    shutil.copy2(ocr_pdf_path, ocr_output)
                    self.results['ocr_pdf'] = str(ocr_output)
            
            # 提取文本
            if self.options.get('extract_text', False):
                self.update_progress.emit(30, "提取文本...")
                text = parser.extract_text_with_pdfminer()
                if text:
                    text_output = self.output_dir / "extracted_text.txt"
                    with open(text_output, "w", encoding="utf-8") as f:
                        f.write(text)
                    self.results['text'] = str(text_output)
                    self.results['text_content'] = text
            
            # 提取图片
            if self.options.get('extract_images', False):
                self.update_progress.emit(50, "提取图片...")
                images_dir = parser.extract_images()
                if images_dir:
                    # 复制图片到输出目录
                    images_output = self.output_dir / "images"
                    images_output.mkdir(exist_ok=True, parents=True)
                    
                    # 复制所有文件
                    image_files = []
                    for item in images_dir.glob("*"):
                        if item.is_file():
                            dest_file = images_output / item.name
                            shutil.copy2(item, dest_file)
                            image_files.append(str(dest_file))
                    
                    self.results['images_dir'] = str(images_output)
                    self.results['image_files'] = image_files
            
            # 提取表格
            if self.options.get('extract_tables', False):
                self.update_progress.emit(70, "提取表格...")
                tables_path = parser.extract_tables()
                if tables_path and Path(tables_path).exists():
                    # 复制表格到输出目录
                    tables_output = self.output_dir / f"tables_{Path(self.pdf_path).stem}.xlsx"
                    shutil.copy2(tables_path, tables_output)
                    self.results['tables'] = str(tables_output)
            
            # 提取结构化内容
            if self.options.get('extract_structured', False):
                self.update_progress.emit(90, "提取结构化内容...")
                elements = parser.extract_structured_content()
                if elements:
                    self.results['structured_elements'] = elements
            
            # 清理临时文件
            if not self.options.get('keep_temp', False):
                parser.cleanup()
            
            self.update_progress.emit(100, "处理完成")
            self.finished.emit(self.results)
            
        except Exception as e:
            logger.error(f"处理过程中出现错误: {str(e)}", exc_info=True)
            self.error.emit(str(e))


class PDFParserGUI(QMainWindow):
    """PDF解析工具的图形用户界面"""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.pdf_path = None
        self.output_dir = None
        self.worker_thread = None
        self.results = {}
    
    def init_ui(self):
        """初始化用户界面"""
        self.setWindowTitle("PDF解析工具")
        self.setMinimumSize(800, 600)
        
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主布局
        main_layout = QVBoxLayout(central_widget)
        
        # 文件选择区域
        file_group = QGroupBox("文件选择")
        file_layout = QGridLayout()
        
        self.pdf_label = QLabel("PDF文件:")
        self.pdf_path_label = QLabel("未选择")
        self.pdf_path_label.setStyleSheet("color: gray;")
        self.browse_pdf_btn = QPushButton("浏览...")
        self.browse_pdf_btn.clicked.connect(self.browse_pdf)
        
        self.output_label = QLabel("输出目录:")
        self.output_path_label = QLabel("未选择")
        self.output_path_label.setStyleSheet("color: gray;")
        self.browse_output_btn = QPushButton("浏览...")
        self.browse_output_btn.clicked.connect(self.browse_output)
        
        file_layout.addWidget(self.pdf_label, 0, 0)
        file_layout.addWidget(self.pdf_path_label, 0, 1)
        file_layout.addWidget(self.browse_pdf_btn, 0, 2)
        file_layout.addWidget(self.output_label, 1, 0)
        file_layout.addWidget(self.output_path_label, 1, 1)
        file_layout.addWidget(self.browse_output_btn, 1, 2)
        
        file_group.setLayout(file_layout)
        main_layout.addWidget(file_group)
        
        # 选项区域
        options_group = QGroupBox("处理选项")
        options_layout = QGridLayout()
        
        self.ocr_checkbox = QCheckBox("执行OCR处理")
        self.ocr_checkbox.setChecked(True)
        
        self.extract_text_checkbox = QCheckBox("提取文本")
        self.extract_text_checkbox.setChecked(True)
        
        self.extract_images_checkbox = QCheckBox("提取图片")
        self.extract_images_checkbox.setChecked(True)
        
        self.extract_tables_checkbox = QCheckBox("提取表格")
        self.extract_tables_checkbox.setChecked(True)
        
        self.extract_structured_checkbox = QCheckBox("提取结构化内容")
        self.extract_structured_checkbox.setChecked(True)
        
        self.keep_temp_checkbox = QCheckBox("保留临时文件")
        
        options_layout.addWidget(self.ocr_checkbox, 0, 0)
        options_layout.addWidget(self.extract_text_checkbox, 0, 1)
        options_layout.addWidget(self.extract_images_checkbox, 1, 0)
        options_layout.addWidget(self.extract_tables_checkbox, 1, 1)
        options_layout.addWidget(self.extract_structured_checkbox, 2, 0)
        options_layout.addWidget(self.keep_temp_checkbox, 2, 1)
        
        options_group.setLayout(options_layout)
        main_layout.addWidget(options_group)
        
        # 进度条
        progress_layout = QHBoxLayout()
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.status_label = QLabel("就绪")
        
        progress_layout.addWidget(self.progress_bar)
        progress_layout.addWidget(self.status_label)
        
        main_layout.addLayout(progress_layout)
        
        # 结果标签页
        self.results_tabs = QTabWidget()
        
        # 文本结果标签页
        self.text_tab = QWidget()
        text_layout = QVBoxLayout(self.text_tab)
        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)
        text_layout.addWidget(self.text_edit)
        
        # 图片结果标签页
        self.images_tab = QWidget()
        images_layout = QVBoxLayout(self.images_tab)
        self.images_label = QLabel("处理后将显示图片信息")
        self.images_label.setAlignment(Qt.AlignCenter)
        images_layout.addWidget(self.images_label)
        
        # 表格结果标签页
        self.tables_tab = QWidget()
        tables_layout = QVBoxLayout(self.tables_tab)
        self.tables_label = QLabel("处理后将显示表格信息")
        self.tables_label.setAlignment(Qt.AlignCenter)
        tables_layout.addWidget(self.tables_label)
        
        # 结构化内容标签页
        self.structured_tab = QWidget()
        structured_layout = QVBoxLayout(self.structured_tab)
        self.structured_edit = QTextEdit()
        self.structured_edit.setReadOnly(True)
        structured_layout.addWidget(self.structured_edit)
        
        # 添加标签页
        self.results_tabs.addTab(self.text_tab, "文本")
        self.results_tabs.addTab(self.images_tab, "图片")
        self.results_tabs.addTab(self.tables_tab, "表格")
        self.results_tabs.addTab(self.structured_tab, "结构化内容")
        
        main_layout.addWidget(self.results_tabs)
        
        # 按钮区域
        buttons_layout = QHBoxLayout()
        
        self.process_btn = QPushButton("开始处理")
        self.process_btn.setEnabled(False)
        self.process_btn.clicked.connect(self.start_processing)
        
        self.open_output_btn = QPushButton("打开输出目录")
        self.open_output_btn.setEnabled(False)
        self.open_output_btn.clicked.connect(self.open_output_directory)
        
        buttons_layout.addStretch()
        buttons_layout.addWidget(self.process_btn)
        buttons_layout.addWidget(self.open_output_btn)
        
        main_layout.addLayout(buttons_layout)
    
    def browse_pdf(self):
        """浏览并选择PDF文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择PDF文件", "", "PDF文件 (*.pdf)"
        )
        if file_path:
            self.pdf_path = file_path
            self.pdf_path_label.setText(file_path)
            self.update_process_button()
    
    def browse_output(self):
        """浏览并选择输出目录"""
        dir_path = QFileDialog.getExistingDirectory(
            self, "选择输出目录", ""
        )
        if dir_path:
            self.output_dir = dir_path
            self.output_path_label.setText(dir_path)
            self.update_process_button()
            self.open_output_btn.setEnabled(True)
    
    def update_process_button(self):
        """更新处理按钮状态"""
        self.process_btn.setEnabled(
            self.pdf_path is not None and self.output_dir is not None
        )
    
    def start_processing(self):
        """开始处理PDF"""
        if not self.pdf_path or not self.output_dir:
            QMessageBox.warning(
                self, "警告", "请先选择PDF文件和输出目录"
            )
            return
        
        # 收集选项
        options = {
            'ocr': self.ocr_checkbox.isChecked(),
            'extract_text': self.extract_text_checkbox.isChecked(),
            'extract_images': self.extract_images_checkbox.isChecked(),
            'extract_tables': self.extract_tables_checkbox.isChecked(),
            'extract_structured': self.extract_structured_checkbox.isChecked(),
            'keep_temp': self.keep_temp_checkbox.isChecked()
        }
        
        # 检查是否至少选择了一个操作
        if not any([options['ocr'], options['extract_text'], 
                   options['extract_images'], options['extract_tables'],
                   options['extract_structured']]):
            QMessageBox.warning(
                self, "警告", "请至少选择一个处理操作"
            )
            return
        
        # 禁用按钮
        self.process_btn.setEnabled(False)
        self.browse_pdf_btn.setEnabled(False)
        self.browse_output_btn.setEnabled(False)
        
        # 清空结果
        self.text_edit.clear()
        self.images_label.setText("正在处理图片...")
        self.tables_label.setText("正在处理表格...")
        self.structured_edit.clear()
        
        # 创建工作线程
        self.worker_thread = WorkerThread(
            self.pdf_path, 
            Path(self.output_dir), 
            options
        )
        self.worker_thread.update_progress.connect(self.update_progress)
        self.worker_thread.finished.connect(self.processing_finished)
        self.worker_thread.error.connect(self.processing_error)
        
        # 启动线程
        self.worker_thread.start()
    
    def update_progress(self, value, status):
        """更新进度条和状态"""
        self.progress_bar.setValue(value)
        self.status_label.setText(status)
    
    def processing_finished(self, results):
        """处理完成后的操作"""
        self.results = results
        
        # 更新文本结果
        if 'text_content' in results:
            self.text_edit.setText(results['text_content'])
            self.results_tabs.setCurrentIndex(0)  # 切换到文本标签页
        
        # 更新图片结果
        if 'images_dir' in results:
            self.images_label.setText(f"图片已保存到: {results['images_dir']}")
        
        # 更新表格结果
        if 'tables' in results:
            self.tables_label.setText(f"表格已保存到: {results['tables']}")
        
        # 更新结构化内容
        if 'structured_elements' in results:
            elements = results['structured_elements']
            text = f"提取到 {len(elements)} 个结构化内容元素:\n\n"
            for i, element in enumerate(elements[:20], 1):  # 只显示前20个元素
                text += f"{i}. {str(element)[:100]}...\n"
            if len(elements) > 20:
                text += f"\n(仅显示前20个元素，共 {len(elements)} 个)"
            self.structured_edit.setText(text)
        
        # 重新启用按钮
        self.process_btn.setEnabled(True)
        self.browse_pdf_btn.setEnabled(True)
        self.browse_output_btn.setEnabled(True)
        
        # 显示完成消息
        QMessageBox.information(
            self, "完成", f"PDF处理完成，结果已保存到: {self.output_dir}"
        )
    
    def processing_error(self, error_msg):
        """处理错误"""
        # 重新启用按钮
        self.process_btn.setEnabled(True)
        self.browse_pdf_btn.setEnabled(True)
        self.browse_output_btn.setEnabled(True)
        
        # 显示错误消息
        QMessageBox.critical(
            self, "错误", f"处理过程中出现错误: {error_msg}"
        )
    
    def open_output_directory(self):
        """打开输出目录"""
        if not self.output_dir:
            return
        
        # 根据操作系统打开文件夹
        if sys.platform == 'win32':
            os.startfile(self.output_dir)
        elif sys.platform == 'darwin':  # macOS
            import subprocess
            subprocess.run(['open', self.output_dir])
        else:  # Linux
            import subprocess
            subprocess.run(['xdg-open', self.output_dir])


def main():
    app = QApplication(sys.argv)
    window = PDFParserGUI()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()