#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 27/04/2018 3:03 PM
# @Author  : Zixing Deng
# @Site    :
# @File    : ZslamCollect_kml.py
# @Software: PyCharm

import sys
import os
import commands


def find_file(file_path):
    find_cmd=' '.join(['find',file_path,'-name','\"*.kml\"'])
    # print(find_cmd)
    files=os.popen(find_cmd).readlines()
    return files


def collect():
    for kml in find_file(file_path):
        if os.path.basename(kml)=='pre_process_gps.kml\n':
            gps_kml=kml.split('/')[-2]+'_gps.kml'
            cp_gps_cmd='cp '+kml[:-1]+' ./gps_kml/'+gps_kml
            os.system(cp_gps_cmd)
        else:
            slam_kml=kml.split('/')[-2]+'_slam.kml'
            cp_slam_cmd='cp '+kml[:-1]+' ./slam_kml/'+slam_kml
            os.system(cp_slam_cmd)

if __name__ == '__main__':
    global file_path
    file_path=sys.argv[1]
    os.chdir(file_path)
    os.mkdir('gps_kml')
    os.mkdir('slam_kml')
    find_file(file_path)
    collect()