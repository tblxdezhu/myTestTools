#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 25/04/2018
# @Author  : Zixing Deng
# @Site    :
# @File    : Xrun_ZSLAM_in_debug.py
# @Software: PyCharm


#To run Zslam in debug

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

def vehcile_slam(o_path,i_config):
    pool = Pool(3)
    for rtv in rtvs:
        imu=rtv[:-3]+'imu'
        if imu in imus:
            date_time=str(datetime.datetime.now().month)+'_'+str(datetime.datetime.now().day)
            output_dir = os.path.join(o_path, date_time + '_' + os.path.basename(rtv).strip(".rtv"))
            #print  os.path.basename(rtv)
            #print os.path.join(path,os.path.basename(rtv).strip(".rtv"))
            if os.path.exists(output_dir):
                continue
            else:
                os.mkdir(output_dir)
                gps= os.path.basename(rtv).strip(".rtv")+'.txt'
                # os.system('touch '+output_dir+gps)
                # os.chdir(output_dir)
                # print output_dir
                pool.apply_async(run_cmd,(rtv,imu,os.path.join(output_dir,gps),output_dir,i_config))
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

def run_cmd(rtv,imu,gps,path,in_config):
    os.chdir(path)
    exe=os.path.join('/home',name,'source/core/algorithm_vehicle/vehicle/offlineSLAM/bin/ZSLAMExe')
    config=os.path.join('/home',name,'source/core/algorithm_vehicle/vehicle/offlineSLAM/config',in_config)
    run_cmd_list = [exe,'--rtv',rtv,'--iimu',imu,'--igps',gps,'--ip',config,'--ic',path,'--d',path]
    run_cmds=' '.join(run_cmd_list)
    print run_cmds
    b=os.system(run_cmds)


def get_parser():

    parser = OptionParser(usage="%prog [-n] [--ip] [--op] [-c]", version="%prog 1.0")
    parser.add_option("-n", dest="name",
                      help="Select the username:'user' or 'roaddb'",
                      default="roaddb")
    parser.add_option("--ip", dest="in_path",
                      help="Select your in_path")
    parser.add_option("--op", dest="out_path",
                      help="Select the out_path",)
    parser.add_option("-c", dest="config",
                      help="Select config file",)
    (options, args) = parser.parse_args()
    if options.config == None:
        print parser.error("You must specify a configuration file")
    return options.name, options.in_path, options.out_path, options.config


if __name__ == '__main__':
    global name
    # global gps
    name,in_path,out_path,config=get_parser()
    rtvs=get_files('*.rtv',in_path)
    imus=get_files('*.imu',in_path)
    # gps = os.path.join('/home',name,'myTestTools/Run/a.txt')
    vehcile_slam(out_path,config)
    #print rtvs
    #print imus