#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 20/03/2018 3:41 PM
# @Author  : Zhenxuan Xu
# @Site    : 
# @File    : send_rtv_as_num.py
# @Software: PyCharm

import sys
import os

IP_LIST = ['10.74.24.199', '10.74.24.197', '10.74.24.201', '10.74.24.216']


def exec_scp(rtv_path, ip):
    case_path = rtv_path.replace(".imu", "*")
    cmd_list = ['scp', case_path, 'ubuntu@' + ip + ":/home/ubuntu/ccdemo_0321"]
    cmd = ' '.join(cmd_list)
    print cmd
    os.system(cmd)


def main():
    files_path = sys.argv[1]
    num = sys.argv[2]
    files_list = os.listdir(files_path)
    flag = 0
    for ip in IP_LIST:
        index = 0
        for files in files_list[flag * int(num):]:
            rtv_path = os.path.join(files_path, files)
            exec_scp(rtv_path, ip)
            index = index + 1
            print index
            if index >= int(num):
                flag = flag + 1
                break


if __name__ == '__main__':
    main()
