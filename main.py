#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import argparse

def main():
    parser = argparse.ArgumentParser(description='PDF解析工具')
    parser.add_argument('--gui', action='store_true', help='启动图形界面')
    parser.add_argument('--cli', action='store_true', help='启动命令行界面')
    parser.add_argument('--generate-sample', action='store_true', help='生成示例PDF')
    parser.add_argument('--output', '-o', help='输出文件路径')
    
    args, remaining_args = parser.parse_known_args()
    
    # 如果没有指定任何参数，默认启动GUI
    if not any([args.gui, args.cli, args.generate_sample]):
        args.gui = True
    
    # 启动图形界面
    if args.gui:
        try:
            from gui import main as gui_main
            gui_main()
            return
        except ImportError as e:
            print(f"启动GUI失败: {str(e)}")
            print("尝试使用命令行界面...")
            args.cli = True
    
    # 生成示例PDF
    if args.generate_sample:
        try:
            from generate_sample_pdf import generate_sample_pdf
            output_path = args.output or 'sample.pdf'
            generate_sample_pdf(output_path=output_path)
            return
        except ImportError as e:
            print(f"生成示例PDF失败: {str(e)}")
    
    # 启动命令行界面
    if args.cli:
        try:
            sys.argv = [sys.argv[0]] + remaining_args
            from cli import main as cli_main
            cli_main()
            return
        except ImportError as e:
            print(f"启动命令行界面失败: {str(e)}")
    
if __name__ == "__main__":
    main()