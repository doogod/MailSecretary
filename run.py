#!/usr/bin/env python3
"""
MailSecretary - 邮件助手
该应用程序可以帮助您自动化处理邮件的各种任务。
"""

import os
import sys
from src.main import MailSecretaryApp
import tkinter as tk

def main():
    """启动MailSecretary应用程序"""
    print("启动MailSecretary...")
    
    # 检查依赖项
    try:
        import openai
        import langdetect
        import pyperclip
    except ImportError as e:
        print(f"错误: 缺少依赖项 - {e}")
        print("请运行 'pip install -r requirements.txt' 安装所需依赖。")
        sys.exit(1)
    
    # 检查OpenAI API密钥
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("注意: 未设置OPENAI_API_KEY环境变量。您可以在应用程序中手动输入API密钥。")
    
    # 启动主应用程序
    root = tk.Tk()
    app = MailSecretaryApp(root)
    root.mainloop()

if __name__ == "__main__":
    main() 