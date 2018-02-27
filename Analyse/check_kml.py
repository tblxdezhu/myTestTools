#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 06/02/2018 3:44 PM
# @Author  : Zhenxuan Xu
# @Site    : 
# @File    : check_kml.py
# @Software: PyCharm

import cal_frechet_distance
import numpy as np


def kml2coordinates(file_path):
    with open(file_path) as f:
        lines = f.readlines()
    coordinates = []
    for line in lines:
        if line.strip().startswith('<'):
            continue
        try:
            for coordinate in line.strip().split():
                lon, lat, alt = coordinate.split(',')
                coordinates.append((float(lon), float(lat)))
        except Exception, e:
            print "converting gps wrongly !!!"
            print e
            continue
    return coordinates


def coordinate2array(coordinates):
    list1 = []
    list2 = []
    for coordinate in coordinates:
        list1.append(coordinate[0])
        list2.append(coordinate[1])
    arr = np.array([list1, list2])
    return arr


if __name__ == '__main__':
    kml1 = kml2coordinates("/Users/test1/Downloads/gps/2017-10-20_T_13-02-10.101_GMT.gps.kml")
    kml2 = kml2coordinates("/Users/test1/Downloads/gps/2017-10-20_T_13-07-10.112_GMT.gps.kml")
    print cal_frechet_distance.frechetDist(coordinate2array(kml1),coordinate2array(kml2))
