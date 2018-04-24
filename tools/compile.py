#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 16/04/2018 3:03 PM
# @Author  : zixing.deng
# @Site    :
# @File    : compile.py
# @Software: PyCharm

import sys
import os
import commands





def clear():
    os.chdir('/home/roaddb/source/core/algorithm_vehicle_slam/example/debug')
    os.system('rm algoSlamExe')
    os.chdir('/home/roaddb/source/core/algorithm_sam/build/example')
    os.system('rm serverExampleSlam')

def checkout_branch(branch):
    os.chdir('/home/roaddb/source/')
    for i in range(8):
        os.chdir(path[i])
        #print ('cd '+path[i])
        os.system('git '+'checkout '+branch)
        os.system('git pull')
    os.chdir('/home/roaddb/source/core/vehicle')
    os.system('git '+'checkout '+branch)
    os.system('git pull')

def compile_code():
    os.chdir('/home/roaddb/source/3rdparty')
    os.system('./build.sh')
    os.chdir('/home/roaddb/source/')
    for i in range(8):
        if i in range(5):
            os.chdir(path[i])
            os.system('./build.sh')
        if i == 5:
            os.chdir(path[i])
            os.system('./build.sh -g')
        if i == 6:
            os.chdir(os.path.join(path[i],'example'))
            os.system('./main.sh -d')
        if i == 7:
            os.chdir('../'+path[i])
            os.system('./build.sh -g')

def check_results():
    os.chdir('/home/roaddb/source/core/algorithm_vehicle_slam/example/debug')
    slam_exe = os.popen('ls').readlines()
    if 'algoSlamExe\n' in slam_exe :
        print ('SLAM ojbk')
    else:
        print('SLAM NG')
    os.chdir('/home/roaddb/source/core/algorithm_sam/build/example')
    sam_exe = os.popen('ls').readlines()
    if 'serverExampleSlam\n' in sam_exe:
        print ('SAM ojbk')
    else:
        print ('SAM NG')



def main():
    global path
    path = ['common/','../framework/device/gmock','../roaddb_logger/','../roaddb_video/','../../../core/common','../algorithm_common/','../algorithm_vehicle_slam/','../algorithm_sam/']
    clear()
    checkout_branch(sys.argv[1])
    compile_code()
    check_results()



if __name__ == '__main__':
    main()




