#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 20/03/2018 3:41 PM
# @Author  : Zhenxuan Xu
# @Site    : 
# @File    : send_rtv_as_num.py
# @Software: PyCharm

import sys
import os

IP_LIST = ['10.74.24.192', '10.74.24.183', '10.74.24.246', '10.74.24.166', '10.74.24.166']


def exec_scp(rtv_path, ip):
    case_path = rtv_path.replace(".rtv", "*")
    cmd_list = ['scp', case_path, 'ubuntu@' + ip + ":/home/ubuntu/gm_0320"]
    cmd = ' '.join(cmd_list)
    print cmd
    os.system(cmd)


def main():
    files_path = sys.argv[1]
    num = sys.argv[2]
    files_list = os.listdir(files_path)
    for ip in IP_LIST:
        index = 0
        print ip
        for files in files_list:
            if files.endswith(".rtv"):
                print files
                rtv_path = os.path.join(files_path, files)
                exec_scp(rtv_path, ip)
                index = index + 1
                print index
                if index > int(num):
                    break


if __name__ == '__main__':
    main()
