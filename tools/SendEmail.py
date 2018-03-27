# coding=utf-8
import sys
import log
import time
import smtplib
from MySqlConn import Mysql
from email.mime.text import MIMEText


mysql = Mysql()
msg_from = 'sec_system@163.com'  # 发送方邮箱
passwd = 'ngscanner2018'  # 填入发送方邮箱的授权码


def logs():
    info = sys.exc_info()
    level = 4
    lylog = log.LogMaster('scan_log', info, level)
    lylog.buildLog()


def send(ip, vul_name):
    if on2off():
        emali = find_email(ip)
        if emali:
            time1 = time.strftime('%Y-%m-%d')
            time2 = time.strftime('%Y年%m月%d日')
            subject = "风险通报"
            content = '''
            管理员：
                你好！
                ''' + time2 + '''专项漏洞''' + vul_name + '''扫描中发现IP：''' + ip + '''存在该漏洞，请及时处理！
            
            发件人：系统管理员
            发件时间：''' + time1 + '''
            
            '''
            msg = MIMEText(content)
            msg['Subject'] = subject
            msg['From'] = msg_from
            msg['To'] = emali
            try:
                s = smtplib.SMTP_SSL("smtp.163.com", 465) # 邮件服务器及端口号
                s.login(msg_from, passwd)
                s.sendmail(msg_from, emali, msg.as_string())
            except s.SMTPException:
                logs()
            finally:
                s.quit()


def find_email(ip):
    sql1 = 'select depart_id from tbl_manage_ip where inet_aton(IP_start) <= inet_aton(%s) AND inet_aton(IP_end)>=inet_aton(%s);'
    result1 = mysql.getOne(sql1, (ip, ip))
    if result1:
        depart_id = result1['depart_id']
        sql2 = 'select email from tbl_manage_group where id=%s'
        result2 = mysql.getOne(sql2, (depart_id))
        if result2:
            email = result2['email']
            return email


def on2off():
    config_file = open('/var/www/html/ngscanner2/static/sconf/scanconfig')
    data = config_file.read()
    dic = eval(data)
    dispatchwork = dic['dispatchwork']
    if dispatchwork == '1':
        return 1
    else:
        return 0