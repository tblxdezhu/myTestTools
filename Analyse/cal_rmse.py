#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 27/03/2018 6:14 PM
# @Author  : Zhenxuan Xu
# @Site    : 
# @File    : cal_rmse.py
# @Software: PyCharm
from __future__ import division
import math
import random


def rmse(gps_list, slam_list, n):
    sum_list = []
    for i in range(n):
        sum_list.append((gps_list[i] - slam_list[i]) ** 2)
    return math.sqrt(sum(sum_list) / n)


if __name__ == '__main__':
    a = range(100)
    b = []
    for i in a:
        # b.append(i + random.random())
        b.append(i + random.random()*2)
    print rmse(a, b, 100)
    print b
