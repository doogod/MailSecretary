import re
from openai import OpenAI
import langdetect
from dateutil import parser
import datetime

class MailAnalyzer:
    def __init__(self, api_key=None):
        """初始化邮件分析器，可选择性地提供OpenAI API密钥"""
        self.api_key = api_key
        if api_key:
            self.client = OpenAI(api_key=api_key)
        else:
            self.client = None
    
    def detect_language(self, text):
        """检测文本的语言"""
        try:
            return langdetect.detect(text)
        except:
            return "en"  # 默认为英语
    
    def generate_summary(self, email_content):
        """生成邮件摘要"""
        if self.client:
            try:
                response = self.client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "请为以下邮件内容生成简洁的摘要，抓住关键信息。"},
                        {"role": "user", "content": email_content}
                    ]
                )
                return response.choices[0].message.content
            except Exception as e:
                return f"无法生成摘要: {str(e)}"
        else:
            # 如果没有API密钥，使用简单的规则生成摘要
            sentences = re.split(r'(?<=[.!?])\s+', email_content)
            if len(sentences) <= 3:
                return email_content
            else:
                return ' '.join(sentences[:3]) + "..."
    
    def extract_todos(self, email_content):
        """提取待办事项并以Markdown格式返回"""
        if self.client:
            try:
                response = self.client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "请从以下邮件中提取所有待办事项，并以Markdown格式的任务列表返回。如果有层级关系，请保持正确的缩进和层级。如果没有待办事项，请返回'无待办事项'。"},
                        {"role": "user", "content": email_content}
                    ]
                )
                return response.choices[0].message.content
            except Exception as e:
                return f"无法提取待办事项: {str(e)}"
        else:
            # 简单的规则提取（非常基础，仅作为备选）
            todos = []
            lines = email_content.split('\n')
            for line in lines:
                if re.search(r'(?i)(todo|to-do|to do|任务|待办|やること)', line):
                    todos.append(f"- {line.strip()}")
            
            return '\n'.join(todos) if todos else "无待办事项"
    
    def extract_schedule(self, email_content):
        """提取日程信息"""
        if self.client:
            try:
                response = self.client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "请从以下邮件中提取日程信息，包括：1) 日程标题, 2) 日历分类(Life/Work/Study), 3) 场所(线上会议地址或现实世界地址), 4) 时间段。然后使用日历软件能理解的自然英语语法写出包含这些信息的语句。如果没有明确的日程信息，请返回'无日程信息'。"},
                        {"role": "user", "content": email_content}
                    ]
                )
                return response.choices[0].message.content
            except Exception as e:
                return f"无法提取日程信息: {str(e)}"
        else:
            # 简单的规则提取（非常基础，仅作为备选）
            date_pattern = r'\d{1,2}[/-]\d{1,2}(?:[/-]\d{2,4})?|\d{4}年\d{1,2}月\d{1,2}日'
            time_pattern = r'\d{1,2}:\d{2}(?:\s*[aApP][mM])?'
            
            dates = re.findall(date_pattern, email_content)
            times = re.findall(time_pattern, email_content)
            
            if dates and times:
                return f"可能的日程: 日期 {dates[0]}, 时间 {times[0]}"
            else:
                return "无日程信息"
    
    def generate_reply(self, email_content):
        """根据邮件语言生成回复"""
        language = self.detect_language(email_content)
        
        if self.client:
            try:
                # 构建适合不同语言的回复提示
                if language == 'zh-cn' or language == 'zh-tw' or language == 'zh':
                    prompt = "请使用简洁干练的中文商业用语，为以下邮件写一个礼貌的回复："
                elif language == 'ja':
                    prompt = "以下のメールに対して、日本のビジネス慣習に従った敬語を使用して丁寧な返信を作成してください："
                else:
                    prompt = "Please write a polite business reply to the following email using concise and professional English:"
                
                response = self.client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": prompt},
                        {"role": "user", "content": email_content}
                    ]
                )
                return response.choices[0].message.content
            except Exception as e:
                return f"无法生成回复: {str(e)}"
        else:
            # 简单的回复模板
            if language == 'zh-cn' or language == 'zh-tw' or language == 'zh':
                return "感谢您的来信。我已收到并会尽快处理。\n\n此致\n敬礼"
            elif language == 'ja':
                return "お世話になっております。\nメールを拝見いたしました。早急に対応させていただきます。\n\n何卒よろしくお願い申し上げます。"
            else:
                return "Thank you for your email. I have received it and will process it as soon as possible.\n\nBest regards," 