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
                #print  os.path.basename(rtv)
                #print os.path.join(path,os.path.basename(rtv).strip(".rtv"))
                os.mkdir(os.path.join(path,os.path.basename(rtv).strip(".rtv")))
                output_dir=os.path.join(path,os.path.basename(rtv).strip(".rtv"))
                #os.chdir(output_dir)
                #print output_dir
                pool.apply_async(run_cmd,(rtv,imu,gps,output_dir))
                # print rtv
                # print imu
    pool.close()
    pool.join()

def get_files(type,path_rtv):
    find_cmd=' find '+path_rtv +' -name '+type
    status, files = commands.getstatusoutput(find_cmd)
    file = files.split('\n')
    #print file
    return file

def run_cmd(rtv,imu,gps,path):
    os.chdir(path)
    exe='/home/roaddb/source/core/algorithm_vehicle/vehicle/offlineSLAM/bin/ZSLAMExe'
    config='/home/roaddb/source/core/algorithm_vehicle/vehicle/offlineSLAM/config/config65.yaml'
    run_cmd_list = [exe,'--rtv',rtv,'--iimu',imu,'--igps',gps,'--ip',config,'--ic',path,'--d',path]
    run_cmds=' '.join(run_cmd_list)
    print run_cmds
    status,results=commands.getstatusoutput(run_cmds)





if __name__ == '__main__':

    global rtvs
    global imus
    global path
    global gps
    rtvs=get_files('*.rtv',sys.argv[1])
    imus=get_files('*.imu',sys.argv[1])
    path=sys.argv[2]
    gps = '/home/roaddb/myTestTools/Run/a.txt'
    vehcile_slam(path)
    #print rtvs
    #print imus