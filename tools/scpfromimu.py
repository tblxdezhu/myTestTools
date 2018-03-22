#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 22/03/2018 8:36 PM
# @Author  : Zhenxuan Xu
# @Site    : 
# @File    : scpfromimu.py
# @Software: PyCharm

import sys
import os

if __name__ == '__main__':
    path = sys.argv[1]
    for rtv in os.listdir(path):
        imu = rtv.replace(".rtv", ".imu")
        cmd = "scp ubuntu@10.74.24.216:/home/ubuntu/ccdemo_128/imu/" + imu + " /home/ubuntu/ccdemo_0321/"
        os.system(cmd)
