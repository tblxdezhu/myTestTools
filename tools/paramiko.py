#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 19/03/2018 8:13 PM
# @Author  : Zhenxuan Xu
# @Site    : 
# @File    : paramiko.py
# @Software: PyCharm

import paramiko

if __name__ == '__main__':
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname='10.69.141.72', port=22, username='test', password='test1234')
    stdin, stdout, stderr = ssh.exec_command('ls')
    result = stdout.read()
    ssh.close()