#!/usr/bin/python
# encoding=utf-8
# Author: Zhenxuan Xu

from __future__ import division
import os
import sys
from math import radians, cos, sin, asin, sqrt
from shapely.geometry import Point, LineString
from shapely.geometry import Polygon
import logging
import traceback

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S',
                    filename='check_result.log',
                    filemode='w')
logger = logging.getLogger('')
console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
console.setFormatter(formatter)
logging.getLogger('').addHandler(console)

def list_fromfiles(dir_path_list, end):
    try:
        file_list = []
        for root, dirs, files in os.walk(dir_path_list):
            for fp in files:
                if fp.endswith(end):
                    file_path = os.path.join(root, fp)
                    file_list.append(file_path)
        return file_list
    except IOError:
        print traceback.print_exc()


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
    # print coordinates
    return coordinates


# Calculate the distance between two points
def haversine(lon1, lat1, lon2, lat2):
    """
    Calculate the great circle distance between two points
    on the earth (specified in decimal degrees)
    """
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * asin(sqrt(a))
    r = 6371
    return c * r * 1000

def compare_range(standard, compare, buf):
    rangement = LineString(standard).buffer(buf)
    compare_line = LineString(compare)
    return rangement.contains(compare_line)


def check_kml2(stand_file, test_file, range_buffer,percent_t):
    true_num = 0
    raw_gps_coordinates = kml2coordinates(stand_file)
    coordinates = kml2coordinates(test_file)
    rangement = LineString(raw_gps_coordinates).buffer(range_buffer)
    area_list = list(rangement.exterior.coords)
    polygon = Polygon(area_list)
    num = 0
    for j in range(len(coordinates)):
        if polygon.contains(Point(coordinates[j])):
            num += 1
        else:
            # logger.info("%s %s %s", test_file, coordinates[j][1], coordinates[j][0])
            continue
    percent_origin = (num / len(coordinates)) * 100
    if percent_origin >= (100 - percent_t*100):
        logger.info("%s %s PASS",test_file,range_buffer*100000)
        kml_pass_list.append(test_file)
    else:
        percent_origin = str(percent_origin)+"%"
        logger.error("%s %sm ERROR-------->percent:%s",test_file,range_buffer*100000,percent_origin)
        kml_error_list.append(test_file)
    return num


# coordinate list convert to kml
def coord_convert_kml(orignfile_full_name_path, kml_color, coord_list):
    GPS_LIST = []

    for line in coord_list:
        # print line
        info = [0.0, 0.0]
        info[0] = line[0]
        info[1] = line[1]
        GPS_LIST.append(info)

    area_full_name = orignfile_full_name_path + '.area.kml'
    fl = open(area_full_name, 'w')
    fl.write(
        '''<?xml version = "1.0" encoding = "UTF-8"?><kml xmlns="http://earth.google.com/kml/2.2"><Placemark><LineString><coordinates>''' + "\n")
    for i in range(0, len(GPS_LIST)):
        fl.write(str(GPS_LIST[i][0]) + "," + str(GPS_LIST[i][1]) + ",0\n")

    kml_style = '''</coordinates></LineString><Style><LineStyle><color>%s</color><width>2</width></LineStyle></Style></Placemark></kml>''' % kml_color
    fl.write("\n" + kml_style)
    fl.close()


def gen_LineString_kml(stand_file, range, out_area_kml, kml_color):
    try:
        raw_gps_coordinates = kml2coordinates(stand_file)
        rangement = LineString(raw_gps_coordinates).buffer(range)
        area_list = list(rangement.exterior.coords)
        coord_convert_kml(out_area_kml, kml_color, area_list)
    except Exception as e:
        print "generate gps area kml fail!! exception: %s.\n" % e

def cal_kml_length(kml_file):
    if '.kml' in kml_file:
        coordinates = kml2coordinates(kml_file)
        num = len(coordinates)
        distances = []
        for i in range(num - 1):
            distance = haversine(coordinates[i][0], coordinates[i][1],
                                 coordinates[i + 1][0], coordinates[i + 1][1])
            distances.append(distance)
    return sum(distances)


if __name__ == '__main__':
    kmls_list_first = list_fromfiles(sys.argv[1], '.kml')
    kmls_list_second = list_fromfiles(sys.argv[2], 'kml')
    t = float(sys.argv[3])/100000
    percent_t = float(sys.argv[4])
    kml_error_list = []
    kml_pass_list = []
    folders_second = os.listdir(sys.argv[2])
    for folder_first in os.listdir(sys.argv[1]):
        if folder_first not in folders_second:
            logger.error("%s don't have %s",sys.argv[2],folder_first)
        else:
            kml_first = sys.argv[1] + folder_first +"/output/final_traj_piece1.kml"
            kml_second = sys.argv[2] + folder_first + "/output/final_traj_piece1.kml"
            if not os.path.exists(kml_first):
                logger.error("don't have %s",kml_first)
            elif not os.path.exists(kml_second):
                logger.error("don't have %s", kml_second)
            else:
                new_kml_name = kml_first+"_"+sys.argv[3]+"_meter"
                gen_LineString_kml(kml_first,t,new_kml_name,'ff0055ff')
                kml_first_length = cal_kml_length(kml_first)
                kml_second_length = cal_kml_length(kml_second)
                result = kml_second_length - kml_first_length
                if result > 0:
                    logger.info("%s is ***longer*** than %s about %sm (longer) ",kml_second,kml_first,result)
                elif result < 0:
                    logger.info("%s is ***shorter*** than %s about %sm (shorter)",kml_second,kml_first,(0-result))
                else:
                    logger.info("%s is equal in value of %s ", kml_second, kml_first)
                check_kml2(kml_first, kml_second, t, percent_t)
    # for i in range(len(kmls_list_first)):
    #     for j in range(len(kmls_list_second)):
    #         if os.path.basename(kmls_list_first[i]) == os.path.basename(kmls_list_second[j]):
    #             kml_name = kmls_list_first[i] + "_"+sys.argv[3]+"_meter.kml"
    #             gen_LineString_kml(kmls_list_first[i], t, kml_name, 'ff0055ff')
    #             check_kml2(kmls_list_first[i], kmls_list_second[j], t,percent_t)
    if len(kml_error_list) == 0:
        logger.info("all right!!!!!")
    else:
        if len(kml_pass_list) == 0:
            pass
        else:
            logger.error("these are kmls passed %sm : %s",t*100000,kml_pass_list)
        logger.error("these are kmls out-of-range %sm : %s",t*100000,kml_error_list)