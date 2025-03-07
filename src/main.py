import tkinter as tk
from tkinter import scrolledtext, messagebox, ttk
import pyperclip
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.utils import MailAnalyzer

class MailSecretaryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("MailSecretary - 邮件助手")
        self.root.geometry("900x700")
        self.root.minsize(800, 600)
        
        # 设置API密钥
        self.api_key = os.environ.get("OPENAI_API_KEY", "")
        self.analyzer = MailAnalyzer(api_key=self.api_key)
        
        self.create_widgets()
    
    def create_widgets(self):
        # 创建主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建选项卡控件
        self.tab_control = ttk.Notebook(main_frame)
        
        # 创建各个选项卡
        self.email_tab = ttk.Frame(self.tab_control)
        self.summary_tab = ttk.Frame(self.tab_control)
        self.todos_tab = ttk.Frame(self.tab_control)
        self.schedule_tab = ttk.Frame(self.tab_control)
        self.reply_tab = ttk.Frame(self.tab_control)
        
        self.tab_control.add(self.email_tab, text="邮件内容")
        self.tab_control.add(self.summary_tab, text="摘要")
        self.tab_control.add(self.todos_tab, text="待办事项")
        self.tab_control.add(self.schedule_tab, text="日程")
        self.tab_control.add(self.reply_tab, text="回复")
        
        self.tab_control.pack(fill=tk.BOTH, expand=True)
        
        # 设置邮件内容选项卡
        self.setup_email_tab()
        
        # 设置摘要选项卡
        self.setup_result_tab(self.summary_tab, "邮件摘要")
        
        # 设置待办事项选项卡
        self.setup_result_tab(self.todos_tab, "待办事项")
        
        # 设置日程选项卡
        self.setup_result_tab(self.schedule_tab, "日程信息")
        
        # 设置回复选项卡
        self.setup_result_tab(self.reply_tab, "回复内容")
        
        # 创建底部按钮框架
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        # 添加API密钥输入
        ttk.Label(button_frame, text="OpenAI API Key:").pack(side=tk.LEFT, padx=5)
        self.api_key_entry = ttk.Entry(button_frame, width=30, show="*")
        self.api_key_entry.pack(side=tk.LEFT, padx=5)
        if self.api_key:
            self.api_key_entry.insert(0, self.api_key)
        
        # 添加分析按钮
        analyze_button = ttk.Button(button_frame, text="分析邮件", command=self.analyze_email)
        analyze_button.pack(side=tk.RIGHT, padx=5)
        
        # 添加从剪贴板粘贴按钮
        paste_button = ttk.Button(button_frame, text="从剪贴板粘贴", command=self.paste_from_clipboard)
        paste_button.pack(side=tk.RIGHT, padx=5)
    
    def setup_email_tab(self):
        """设置邮件内容选项卡"""
        frame = ttk.Frame(self.email_tab, padding="10")
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(frame, text="请粘贴完整的邮件内容:").pack(anchor=tk.W, pady=(0, 5))
        
        # 邮件内容文本框
        self.email_text = scrolledtext.ScrolledText(frame, wrap=tk.WORD, height=20)
        self.email_text.pack(fill=tk.BOTH, expand=True)
    
    def setup_result_tab(self, tab, title):
        """设置结果选项卡的通用布局"""
        frame = ttk.Frame(tab, padding="10")
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(frame, text=title + ":").pack(anchor=tk.W, pady=(0, 5))
        
        # 结果文本框
        result_text = scrolledtext.ScrolledText(frame, wrap=tk.WORD, height=20)
        result_text.pack(fill=tk.BOTH, expand=True)
        
        # 复制按钮
        copy_button = ttk.Button(frame, text="复制到剪贴板", 
                                 command=lambda: self.copy_to_clipboard(result_text.get(1.0, tk.END)))
        copy_button.pack(anchor=tk.E, pady=(5, 0))
        
        # 保存文本框的引用
        if title == "邮件摘要":
            self.summary_text = result_text
        elif title == "待办事项":
            self.todos_text = result_text
        elif title == "日程信息":
            self.schedule_text = result_text
        elif title == "回复内容":
            self.reply_text = result_text
    
    def paste_from_clipboard(self):
        """从剪贴板粘贴内容到邮件文本框"""
        try:
            clipboard_content = pyperclip.paste()
            self.email_text.delete(1.0, tk.END)
            self.email_text.insert(tk.END, clipboard_content)
            messagebox.showinfo("粘贴成功", "已从剪贴板粘贴内容")
        except Exception as e:
            messagebox.showerror("粘贴失败", f"无法从剪贴板粘贴内容: {str(e)}")
    
    def copy_to_clipboard(self, content):
        """复制内容到剪贴板"""
        try:
            pyperclip.copy(content)
            messagebox.showinfo("复制成功", "内容已复制到剪贴板")
        except Exception as e:
            messagebox.showerror("复制失败", f"无法复制到剪贴板: {str(e)}")
    
    def analyze_email(self):
        """分析邮件内容"""
        email_content = self.email_text.get(1.0, tk.END).strip()
        
        if not email_content:
            messagebox.showwarning("输入为空", "请先输入或粘贴邮件内容")
            return
        
        # 更新API密钥
        api_key = self.api_key_entry.get().strip()
        if api_key:
            self.analyzer = MailAnalyzer(api_key=api_key)
        
        # 显示加载提示
        self.show_loading()
        
        try:
            # 生成摘要
            summary = self.analyzer.generate_summary(email_content)
            self.summary_text.delete(1.0, tk.END)
            self.summary_text.insert(tk.END, summary)
            
            # 提取待办事项
            todos = self.analyzer.extract_todos(email_content)
            self.todos_text.delete(1.0, tk.END)
            self.todos_text.insert(tk.END, todos)
            
            # 提取日程信息
            schedule = self.analyzer.extract_schedule(email_content)
            self.schedule_text.delete(1.0, tk.END)
            self.schedule_text.insert(tk.END, schedule)
            
            # 生成回复
            reply = self.analyzer.generate_reply(email_content)
            self.reply_text.delete(1.0, tk.END)
            self.reply_text.insert(tk.END, reply)
            
            # 完成后切换到摘要选项卡
            self.tab_control.select(1)
            
        except Exception as e:
            messagebox.showerror("分析失败", f"邮件分析过程中出错: {str(e)}")
        
        # 隐藏加载提示
        self.hide_loading()
    
    def show_loading(self):
        """显示加载中提示"""
        self.loading_window = tk.Toplevel(self.root)
        self.loading_window.title("处理中")
        self.loading_window.geometry("300x100")
        self.loading_window.transient(self.root)
        self.loading_window.grab_set()
        
        ttk.Label(self.loading_window, text="正在分析邮件，请稍候...").pack(padx=20, pady=20)
        
        progressbar = ttk.Progressbar(self.loading_window, mode="indeterminate")
        progressbar.pack(fill=tk.X, padx=20, pady=10)
        progressbar.start(10)
        
        # 强制更新界面
        self.loading_window.update()
    
    def hide_loading(self):
        """隐藏加载提示"""
        if hasattr(self, 'loading_window') and self.loading_window:
            self.loading_window.destroy()
            self.loading_window = None

if __name__ == "__main__":
    root = tk.Tk()
    app = MailSecretaryApp(root)
    root.mainloop() 