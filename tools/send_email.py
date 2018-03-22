#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 22/11/2017 10:20 AM
# @Author  : Zhenxuan Xu
# @Site    :
# @File    : email.py
# @Software: PyCharm

from email.header import Header
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.utils import parseaddr, formataddr
import smtplib
import os
import sys

sys.path.append("..")
from tools import func  # noqa


def _format_addr(s):
    name, addr = parseaddr(s)
    return formataddr((
        Header(name, 'utf-8').encode(),
        addr.encode('utf-8') if isinstance(addr, unicode) else addr))


def send_email(config_file, mode):
    # TODO 发送编译失败邮件，附上编译log
    from_addr = "zhenxuan.xu@ygomi.com"
    to_addr = func.config_from_json(config_file, "run_config")["email"]
    if mode == 'msg':
        msg = MIMEText('批量测试已经完成，请检查10.74.24.35\n自动发送，请勿回复', 'plain', 'utf-8')
        msg['Subject'] = Header(
            u'Notifications for automated tests', 'utf-8').encode()
    else:
        msg = MIMEMultipart()
        msg['Subject'] = Header(u'Your test report', 'utf-8').encode()
        att = MIMEText(open('./Reports/SLAM_Performance_slam.html',
                            'rb').read(), 'base64', 'utf-8')
        att["Content-Type"] = "application/octet-stream"
        att['Content-Disposition'] = 'attachment;filename="SLAM.html"'
        msg.attach(att)
        att2 = MIMEText(open(
            './Reports/SLAM_Performance_alignment.html', 'rb').read(), 'base64', 'utf-8')
        att2["Content-Type"] = "application/octet-stream"
        att2['Content-Disposition'] = 'attachment;filename="alignment.html"'
        msg.attach(att2)
    msg['From'] = _format_addr(from_addr)
    msg['To'] = _format_addr(to_addr)
    smtp_server = "mail-chengdu.ygomi.net"
    server = smtplib.SMTP()
    server.set_debuglevel(1)
    server.connect(smtp_server, )
    server.sendmail(from_addr, to_addr, msg.as_string())
    server.quit()
