#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 06/02/2018 10:01 AM
# @Author  : Zhenxuan Xu
# @Site    : 
# @File    : tmp.py
# @Software: PyCharm
import sys
sys.path.append("..")
from Run import run_SLAM_in_debug

if __name__ == '__main__':
    intput_path = '/home/roaddb/xuzhenxuan/outputs/20180205_050344_debug_zhenxuan_master_tokyo/alignment'
    out_path = "/home/roaddb/new_repo/core/algorithm_sam/build/example/alignmentout"
    run_SLAM_in_debug.copy_files(intput_path,out_path,'alignment')