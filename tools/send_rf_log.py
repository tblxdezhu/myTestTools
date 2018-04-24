#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 11/04/2018 3:34 PM
# @Author  : Zhenxuan Xu
# @Site    : 
# @File    : send_rf_log.py
# @Software: PyCharm

import os
import sys
from email.header import Header
from email.mime.text import MIMEText
from email.utils import parseaddr, formataddr
import smtplib
import datetime


class Analyse:
    def __init__(self):
        self.data = get_info()[2]
        self.failed_data = get_failed_info()
        self.group_name = self.data[1]["label"].split(".")[-1]
        self.suits = {}
        self.sumary = {}
        self.len_of_suit = 0

    def process_data(self):
        for suit in self.data[2:]:
            self.suits[suit["name"]] = [suit["pass"], suit["fail"], suit["elapsed"]]
        self.sumary["pass"] = 0
        self.sumary["fail"] = 0
        self.sumary["time"] = "00:00:00"
        for suit in self.suits:
            self.sumary["pass"] = self.sumary["pass"] + self.suits[suit][0]
            self.sumary["fail"] = self.sumary["fail"] + self.suits[suit][1]
            self.sumary["time"] = cal_time(self.sumary["time"], self.suits[suit][2])
        self.len_of_suit = len(self.suits)


def get_info():
    with open(os.path.join(path, "Intergration_ubuntu.table.tmp"), "r") as f:
        contents = f.readlines()
        return eval(contents[1])


def get_failed_info():
    failed_info = []
    with open(os.path.join(path, "Intergration_ubuntu.testcase.tmp"), "r") as f:
        contents = f.readlines()
        for content in contents:
            failed_info.append(content.split(">")[1].split("<")[0])
        return failed_info


def cal_time(init_time, str_time):
    dt_init = datetime.datetime.strptime(init_time, "%H:%M:%S")
    dt = datetime.datetime.strptime(str_time, "%H:%M:%S")
    hour, minute, second = dt.hour, dt.minute, dt.second
    return str((dt_init + datetime.timedelta(hours=hour, minutes=minute, seconds=second)).time())


def _format_addr(s):
    name, addr = parseaddr(s)
    return formataddr((
        Header(name, 'utf-8').encode(),
        addr.encode('utf-8') if isinstance(addr, unicode) else addr))


def send_email(length, suits, group, failed, sumary):
    from_addr = "ygomi\RoadDB_TSRP@ygomi.com "
    to_addr = ["zhenxuan.xu@ygomi.com"]
    # to_addr = ["zhenxuan.xu@ygomi.com", "xianlong.wan@ygomi.com", "yu.zhou@ygomi.com", "zixing.deng@ygomi.com"]
    total_num_info = "<br>Total Time Cost: %s<br>Total Cases: %s <br>Passed Cases: %s <br><b><font color=\"red\">Failed Cases: %s</font></b></br></br></br>" % (
        sumary["time"], sumary["pass"] + sumary["fail"], sumary["pass"], sumary["fail"])
    email_msg = """
    <br><br><b>Intergration Auto Test:</b><br>
    """
    email_msg = email_msg + total_num_info
    table_info = """
        <table border="1"width=\"600px\">
        <tr>
        <th>Group</th><th>Suit Name</th><th>Time Cost</th><th>Total</th><th>Pass</th><th>Fail</th>
        </tr><tr>"""
    len_info = "<th rowspan=%s>%s</th>" % (length + 2, group)
    suit_info = ""
    for suit in suits:
        suit_info = suit_info + """<tr><td width=\"10%%\" height=30px\"><div align=\"center\">%s</td><td><div align=\"center\">%s</td><td><div align=\"center\">%s</td><td><div align=\"center\"><a href="https://bamboo-aws.ygomi.com:8443/browse/RDB-DAILINTERETEST-14/artifact"><font color=\"green\">%s</front></a></td><td><div align=\"center\"><a href="https://bamboo-aws.ygomi.com:8443/browse/RDB-DAILINTERETEST-14/artifact"><font color=\"red\">%s</front></a></td></tr>""" % (
            suit, suits[suit][2], sum(suits[suit][0:2]), suits[suit][0], suits[suit][1])
    end_info = """
    <td><div align=\"center\">total:</td><td><div align=\"center\">%s</td><td><div align=\"center\">%s</td><td><div align=\"center\">%s</td><td><div align=\"center\">%s</td></tr></table>
    """ % (sumary["time"], sumary["pass"] + sumary["fail"], sumary["pass"], sumary["fail"])
    table_info = table_info + len_info + suit_info + end_info
    failed_info = "<br><b><font color=\"red\">Failed Test Cases List:</font></b></br>"
    failed_list_info = ""
    for fail in failed:
        fail_info = "<br>" + fail + "</br>"
        failed_list_info = failed_list_info + fail_info
    failed_end_info = """<br><br><b>Test Cases Robot Framework Log Link </b> : <br> <a href="https://bamboo-aws.ygomi.com:8443/browse/RDB-DAILINTERETEST-14/artifact">https://bamboo-aws.ygomi.com:8443/browse/RDB-DAILINTERETEST-14/artifact</a></br><br><b>Plan Running Log</b> :  <br><a href="https://bamboo-aws.ygomi.com:8443/browse/RDB-DAILINTERETEST-14/log">https://bamboo-aws.ygomi.com:8443/browse/RDB-DAILINTERETEST-14/log</a></br>"""
    email_msg = email_msg + table_info + failed_info + failed_list_info + failed_end_info
    msg = MIMEText(email_msg, 'html', 'utf-8')
    msg['Subject'] = Header(u'Intergration Regression Test ( Master ) ', 'utf-8').encode()
    msg['From'] = _format_addr(from_addr)
    msg['To'] = _format_addr(to_addr)
    smtp_server = "mail-chengdu.ygomi.net"
    server = smtplib.SMTP()
    # server.set_debuglevel(1)
    server.connect(smtp_server, )
    server.sendmail(from_addr, to_addr, msg.as_string())
    server.quit()


def main():
    global path
    path = sys.argv[1]
    analyse = Analyse()
    analyse.process_data()
    send_email(analyse.len_of_suit, analyse.suits, analyse.group_name, analyse.failed_data, analyse.sumary)


if __name__ == '__main__':
    main()
