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


class Analyse:
    def __init__(self):
        self.data = get_info()[2]
        self.failed_data = get_failed_info()
        self.group_name = self.data[1]["label"].split(".")[-1]
        self.suits_sumary = {}
        self.sumary = {}
        self.len_of_suit = 0
        self.data_processed = {}

    def process_data(self):
        self.sumary["pass"] = self.data[0]['pass']
        self.sumary["fail"] = self.data[0]['fail']
        self.sumary["time"] = self.data[0]['elapsed']
        for suit in self.data[1:]:
            if len(suit["id"].split("-")) == 2:
                self.suits_sumary[suit["name"]] = [suit["pass"], suit['fail'], suit['elapsed']]
                self.data_processed[suit['label'].split(".")[1]] = {}
        for suit in self.data[1:]:
            if len(suit["id"].split("-")) > 2:
                self.data_processed[suit['label'].split(".")[1]][suit['label'].split(".")[-1]] = [suit['pass'], suit['fail'], suit['elapsed']]


def new_send_email(sumary, suits_sumary, data_processed, failed):
    from_addr = "ygomi\RoadDB_TSRP@ygomi.com "
    to_addr = ["zhenxuan.xu@ygomi.com"]
    email_title_info = "<br><br><b>Intergration Auto Test:</b><br>"
    summary_info = "<br>Total Time Cost: %s<br>Total Cases: %s <br>Passed Cases: %s <br><b><font color=\"red\">Failed Cases: %s</font></b></br></br></br>" % (
        sumary["time"], sumary["pass"] + sumary["fail"], sumary["pass"], sumary["fail"])
    table_info = """
        <table border="1"width=\"600px\">
        <tr>
        <th>Group</th><th>Suit Name</th><th>Time Cost</th><th>Total</th><th>Pass</th><th>Fail</th>
        </tr><tr>
    """
    suit_title_info = ""
    for suits in suits_sumary:
        suit_title_info += "<th rowspan=%s>%s</th>" % (len(data_processed[suits]), suits)
        suit_info = ""
        for suit in data_processed[suits]:
            suit_info += """<td width=\"10%%\" height=30px\"><div align=\"center\">%s</td><td><div align=\"center\">%s</td><td><div align=\"center\">%s</td><td><div align=\"center\"><a href="https://bamboo-aws.ygomi.com:8443/browse/RDB-DAILINTERETEST-14/artifact"><font color=\"green\">%s</front></a></td><td><div align=\"center\"><a href="https://bamboo-aws.ygomi.com:8443/browse/RDB-DAILINTERETEST-14/artifact"><font color=\"red\">%s</front></a></td></tr>""" % (
                suit, data_processed[suits][suit][2], sum(data_processed[suits][suit][0:2]),
                data_processed[suits][suit][0], data_processed[suits][suit][1])
        suit_end_info = """
            <td><div align=\"center\">total:</td><td><div align=\"center\">%s</td><td><div align=\"center\">%s</td><td><div align=\"center\">%s</td><td><div align=\"center\">%s</td></tr></table>
        """ % (suits_sumary[suits][2], suits_sumary[suits][0] + suits_sumary[suits][1], suits_sumary[suits][0],
               suits_sumary[suits][1])
        suit_title_info = suit_title_info + suit_info
    table_end_info = "</table>"
    failed_info = "<br><b><font color=\"red\">Failed Test Cases List:</font></b></br>"
    failed_list_info = ""
    for fail in failed:
        fail_info = "<br>" + fail + "</br>"
        failed_list_info = failed_list_info + fail_info
    failed_end_info = """<br><br><b>Test Cases Robot Framework Log Link </b> : <br> <a href="https://bamboo-aws.ygomi.com:8443/browse/RDB-DAILINTERETEST-14/artifact">https://bamboo-aws.ygomi.com:8443/browse/RDB-DAILINTERETEST-14/artifact</a></br><br><b>Plan Running Log</b> :  <br><a href="https://bamboo-aws.ygomi.com:8443/browse/RDB-DAILINTERETEST-14/log">https://bamboo-aws.ygomi.com:8443/browse/RDB-DAILINTERETEST-14/log</a></br>"""
    email_msg = email_title_info + summary_info + table_info + suit_title_info + table_end_info + failed_info + failed_list_info + failed_end_info
    msg = MIMEText(email_msg, 'html', 'utf-8')
    msg['Subject'] = Header(u'Intergration Regression Test ( Master ) ', 'utf-8').encode()
    msg['From'] = _format_addr(from_addr)
    msg['To'] = _format_addr(to_addr)
    smtp_server = "mail-chengdu.ygomi.net"
    server = smtplib.SMTP()
    server.connect(smtp_server, )
    server.sendmail(from_addr, to_addr, msg.as_string())
    server.quit()


def get_info():
    with open(os.path.join(path, "test.table.tmp"), "r") as f:
        contents = f.readlines()
        return eval(contents[1])


def get_failed_info():
    failed_info = []
    with open(os.path.join(path, "test.testcase.tmp"), "r") as f:
        contents = f.readlines()
        for content in contents:
            failed_info.append(content.split(">")[1].split("<")[0])
        return failed_info


def _format_addr(s):
    name, addr = parseaddr(s)
    return formataddr((
        Header(name, 'utf-8').encode(),
        addr.encode('utf-8') if isinstance(addr, unicode) else addr))


def main():
    global path
    path = sys.argv[1]
    analyse = Analyse()
    analyse.process_data()
    new_send_email(analyse.sumary, analyse.suits_sumary, analyse.data_processed, analyse.failed_data)


if __name__ == '__main__':
    main()
