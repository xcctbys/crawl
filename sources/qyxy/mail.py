#encoding=utf-8

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


class SendMail(object):
    
    def __init__(self, host, port, username, password, ssl=False):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.ssl = ssl
        self.smtp = None
    
    def send_text(self, from_addr, to_addrs, subject, content):
        self._login()
        
        multipart = MIMEMultipart('alternative')
        multipart.set_charset('utf-8')
        
        multipart["Subject"] = subject
        multipart["From"] = from_addr
        multipart["To"] = ", ".join(to_addrs)
        
        text = MIMEText(content, 'plain', "utf-8")
        multipart.attach(text)
        
        self.smtp.sendmail(from_addr, to_addrs, multipart.as_string(False))
        self.smtp.quit()
        
    def send_html(self, from_addr, to_addrs, subject, content):
        self._login()
        
        multipart = MIMEMultipart('alternative')
        multipart.set_charset('utf-8')
        
        multipart["Subject"] = subject
        multipart["From"] = from_addr
        multipart["To"] = ", ".join(to_addrs)
        
        html = MIMEText(content, 'html', "utf-8")
        multipart.attach(html)
        
        self.smtp.sendmail(from_addr, to_addrs, multipart.as_string(False))
        self.smtp.quit()
    
    def _login(self):
        if self.ssl:
            self.smtp = smtplib.SMTP_SSL(self.host, self.port)
        else:
            self.smtp = smtplib.SMTP(self.host, self.port)
            
        self.smtp.connect(self.host, self.port)
        self.smtp.login(self.username, self.password)
        