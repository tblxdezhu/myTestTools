#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 25/04/2018
# @Author  : Zixing Deng
# @Site    :
# @File    : Xrun_ZSLAM_in_debug.py
# @Software: PyCharm


import os
import sys
from optparse import OptionParser
import json
import commands
from multiprocessing import Pool
from time import sleep
import time
import shutil
import traceback
import logging
import datetime
import coloredlogs


def vehcile_slam(path):
    pool = Pool(3)
    for rtv in rtvs:
        for imu in imus:
            if os.path.basename(rtv).strip('.rtv') == os.path.basename(imu).strip(".imu"):
                # print  os.path.basename(rtv)
                # print os.path.join(path,os.path.basename(rtv).strip(".rtv"))
                if os.path.exists(os.path.join(path, os.path.basename(rtv).strip(".rtv"))):
                    continue
                else:
                    os.mkdir(os.path.join(path, os.path.basename(rtv).strip(".rtv")))
                    output_dir = os.path.join(path, os.path.basename(rtv).strip(".rtv"))
                    # os.chdir(output_dir)
                    # print output_dir
                    pool.apply_async(run_cmd, (rtv, imu, gps, output_dir))
                # print rtv
                # print imu
    pool.close()
    pool.join()


def get_files(type, path_rtv):
    find_cmd = ' find ' + path_rtv + ' -name ' + type
    status, files = commands.getstatusoutput(find_cmd)
    file = files.split('\n')
    # print file
    return file


def run_cmd(rtv, imu, gps, path):
    os.chdir(path)
    exe = os.path.join('/home/', user_name, '/source/core/algorithm_vehicle/vehicle/offlineSLAM/bin/ZSLAMExe')
    config = os.path.join('/home/', user_name,
                          '/source/core/algorithm_vehicle/vehicle/offlineSLAM/config/config65.yaml')
    run_cmd_list = [exe, '--rtv', rtv, '--iimu', imu, '--igps', gps, '--ip', config, '--ic', path, '--d', path]
    run_cmds = ' '.join(run_cmd_list)
    print run_cmds
    # b = os.system(run_cmds)


if __name__ == '__main__':
    global rtvs
    global imus
    global path
    global gps
    global user_name
    gps = ''
    rtvs = get_files('*.rtv', sys.argv[2])
    imus = get_files('*.imu', sys.argv[2])
    path = sys.argv[3]
    user_name = sys.argv[1]
    print user_name
    gps = os.path.join('/home', user_name, '/myTestTools/Run/a.txt')
    print gps
    # vehcile_slam(path)
    # print rtvs
    # print imus
