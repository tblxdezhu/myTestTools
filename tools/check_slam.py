#!/usr/bin/python
# encoding=utf-8
# Author: Qian Li
from __future__ import division
import matplotlib

matplotlib.use('Agg')

import numpy as np
import matplotlib.pyplot as plt
import os, re, getopt, sys
from math import radians, cos, sin, asin, sqrt
from shapely.geometry import Point, LineString
from exceptions import AssertionError
from shapely.geometry import Polygon


def usage():
    print """ The usage of the commands:
    -i        dir path.   e.g. /home/sislee/Documents/a-sample/vehicle/kml_test/
    """


def print_help_exit():
    usage()
    sys.exit(-1)


def parse_options():
    rs = {}
    try:
        opts, args = getopt.getopt(sys.argv[1:], 'hi:')
        # print opts
        # print args

        if len(opts) == 0:
            print_help_exit()

        for name, value in opts:
            if name in ("-h"):
                print_help_exit()
            elif name in ("-i"):
                # print "dir path: ", value
                rs['input'] = value
            else:
                print_help_exit()

    except getopt.GetoptError:
        print_help_exit()
    return rs


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
    # Convert decimal degrees to radians
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    # haversine formula  
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * asin(sqrt(a))
    # The average radius of the earth. Unit is kilometers
    r = 6371
    return c * r * 1000


def TraversalFile(input_path):
    global len_list
    global file_name_path
    len_list = {}
    file_name_path = {}
    # input_param = opt_val['input']

    for root, dirs, files in os.walk(input_path):
        for file in files:
            each_file_path = os.path.join(root, file)
            file_name_path[file] = each_file_path
    return file_name_path


def GetAllKml(input_param):
    global raw_gps_kml_file
    raw_gps_kml_file = 'pre_process_gps.kml'
    TraversalFile(input_param)

    # calculate each kml file length in current path and record file name & length of kml file as a dict
    for fileName in file_name_path:
        if ".kml" in fileName:
            coordinates = kml2coordinates(file_name_path[fileName])
            num = len(coordinates)
            # print "There are %s coordinates" % (num)
            distances = []
            # points in coordinates
            for i in range(num - 1):
                distance = haversine(coordinates[i][0], coordinates[i][1],
                                     coordinates[i + 1][0], coordinates[i + 1][1])
                distances.append(distance)
                # print distance
            # print distances
            len_list[fileName] = sum(distances)
        else:
            pass
    # print "all kml length ======> %s" % len_list
    return len_list


def cal_kml_len(input_param):
    len_list = GetAllKml(input_param)
    gps_list = {}
    slam_list = {}

    for (k, v) in len_list.iteritems():
        if k == raw_gps_kml_file:
            continue
        if re.match(r'.*_slam.out0\d\d\d_kf_kfOw\.kml$', k):
            slam_list[k] = v
            # slam_list.append(v)
            # print "slam_list: %s" % k
            continue
        if re.match(r'.*good_hq_gps\.kml$', k):
            gps_list[k] = v
            # gps_list.append(v)
            # print "gps_list: %s" % k
            # continue
        else:
            # print "Skip the file: %s" % k
            pass
    print "Good gps_list ======> %s" % gps_list
    print "Good slam_list ======> %s" % slam_list
    # convert value of dict to list
    gps_value = list(gps_list.values())
    slam_value = list(slam_list.values())
    print "gps_value ======> %s" % gps_value
    print "slam_value ======> %s" % slam_value
    return gps_value, slam_value


def TotalLength(input_param):
    kml_list = []
    kml_list = cal_kml_len(input_param)
    gps_distance_result = sum(kml_list[0])
    # print "gps_distance_result: %s" % gps_distance_result
    slam_distance_result = sum(kml_list[1])
    # print "slam_distance_result: %s" % slam_distance_result
    return gps_distance_result, slam_distance_result


# define recognition_rate. If there are a few segments, need to add those seg_kml as len1
def recognition_rate(seg_len, raw_len):
    rate = seg_len / raw_len
    return rate


# judge in the buf of standard comtain the compare_line
def compare_range(standard, compare, buf):
    rangement = LineString(standard).buffer(buf)
    compare_line = LineString(compare)
    return rangement.contains(compare_line)


def cal_rate(seg_len, raw_len, threshold, info):
    rate = recognition_rate(seg_len, raw_len)
    if rate < 0 and abs(rate) < threshold:
        print "%s's total length: %s meters, rate: %s, raw_gps_kml's length: %s meters" % (info, seg_len, rate, raw_len)
    else:
        print "%s's total length: %s meters, rate: %s, raw_gps_kml's length: %s meters" % (info, seg_len, rate, raw_len)
        pass


# stand_file could be pre_process_gps.kml
# file_type could be good_hq_gps.kml,good_hq_slam.kml,kf.kml.
# range could be 0.00001 means 1 meter.
def check_kml(stand_file, test_file, range):
    true_num = 0
    raw_gps_coordinates = kml2coordinates(file_name_path[stand_file])
    for fileName in file_name_path:
        if test_file in fileName:
            coordinates = kml2coordinates(file_name_path[fileName])
            compare_result = compare_range(raw_gps_coordinates, coordinates, range)
            if compare_result == True:
                true_num += 1
            print fileName, compare_result
    return true_num


def check_kml2(stand_file, test_file, range_buffer):
    true_num = 0
    raw_gps_coordinates = kml2coordinates(file_name_path[stand_file])
    for fileName in file_name_path:
        if test_file in fileName:
            coordinates = kml2coordinates(file_name_path[fileName])
            rangement = LineString(raw_gps_coordinates).buffer(range_buffer)

            area_list = []
            area_list = list(rangement.exterior.coords)
            polygon = Polygon(area_list)
            num = 0
            for j in range(len(coordinates)):
                if polygon.contains(Point(coordinates[j])):
                    num += 1
                else:
                    continue
            print "num:",num
            print "len(coordinates):",len(coordinates)
            percent_origin = (num / len(coordinates)) * 100
            print "percent_origin:",percent_origin
            percent = float('%.3f' % percent_origin)
            print percent
            if range_buffer == 0.0002:
                if percent_origin == 100:
                    print fileName, ">>>>>>20m shapely: PASS"
                else:
                    print fileName, ">>>>>>20m shapely: error"
            elif range_buffer == 0.00007:
                if percent_origin > 40:
                    print fileName, ">>>>>>7m shapely: PASS"
                    true_num += 1
                else:
                    print fileName, ">>>>>>7m shapely: error"
    return true_num


# range could be 0.00001 means 1 meter.
def check_kml_dir(input_dir, stand_file, gps_range, slam_range):
    # file_name_path = TraversalFile(input_dir)
    res = TraversalFile(input_dir)
    print res
    raw_gps_coordinates = kml2coordinates(file_name_path[stand_file])
    for fileName in file_name_path:
        if "gps.kml" in fileName:
            gps_coordinates = kml2coordinates(file_name_path[fileName])
            result = compare_range(raw_gps_coordinates, gps_coordinates, float(gps_range))
            print fileName, result
            if result != True:
                break
        elif "slam.kml" in fileName:
            slam_coordinates = kml2coordinates(file_name_path[fileName])
            result = compare_range(raw_gps_coordinates, slam_coordinates, float(slam_range))
            print fileName, result
            if result != True:
                break
    return result


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
        area_list = []
        raw_gps_coordinates = kml2coordinates(file_name_path[stand_file])
        rangement = LineString(raw_gps_coordinates).buffer(range)
        area_list = list(rangement.exterior.coords)
        # print area_list

        path = os.path.abspath(file_name_path[stand_file])
        dirPath = os.path.dirname(path)
        area_kml_full_path = dirPath + os.sep + out_area_kml

        # convert coordinate to kml
        coord_convert_kml(area_kml_full_path, kml_color, area_list)

    except Exception as e:
        print "generate gps area kml fail!! exception: %s.\n" % e


# get coordinates of x, y for each kml
def kml_for_draw(file_path):
    coords = kml2coordinates(file_path)
    coords_len = len(coords)
    file_name = file_path.split("/")[-1]
    print "file_name: %s" % file_name
    x_coord = []
    y_coord = []

    if coords_len > 0:
        for i in range(coords_len):
            x_coord.append(coords[i][0])
            y_coord.append(coords[i][1])
        all_coord[file_name + "_x"] = x_coord
        all_coord[file_name + "_y"] = y_coord
    return all_coord


def draw(all_files, path):
    kf_filename = []
    if os.path.exists(ori_gps_kml) and os.path.exists(shapely_scope_7_kml) and os.path.exists(shapely_scope_20_kml):
        kml_for_draw(ori_gps_kml)
        kml_for_draw(shapely_scope_7_kml)
        kml_for_draw(shapely_scope_20_kml)
        # draw
        plt.plot(all_coord[ori_gps_kml.split("/")[-1] + "_x"], all_coord[ori_gps_kml.split("/")[-1] + "_y"], 'r-',
                 label='Original GPS', linewidth=1)
        print "draw Original GPS"
        plt.plot(all_coord[shapely_scope_7_kml.split("/")[-1] + "_x"],
                 all_coord[shapely_scope_7_kml.split("/")[-1] + "_y"], 'b-', label='Shapely: 7 meters scope',
                 linewidth=1)
        print "draw Shapely: 7 meters scope"
        plt.plot(all_coord[shapely_scope_20_kml.split("/")[-1] + "_x"],
                 all_coord[shapely_scope_20_kml.split("/")[-1] + "_y"], 'b-', label='Shapely: 20 meters scope',
                 linewidth=1)
        print "draw Shapely: 20 meters scope"
        for file in all_files.keys():
            if re.match(r'.*_slam.out0\d\d\d_kf_kfOw\.kml$', file.split("/")[-1]):
                print "kf file: %s" % file.split("/")[-1]
                kml_for_draw(all_files[file])
                print "get kf coords"
                kf_filename.append(file)
            else:
                pass
        print "kf_filename: %s" % kf_filename

        for f in kf_filename:
            # print "kf file name: %s" % f
            if re.match(r'.*_slam.out0000_kf_kfOw\.kml$', f):
                plt.plot(all_coord[f + "_x"], all_coord[f + "_y"], 'g-', label='SLAM slam.out00_kfOw.kml', linewidth=1)
                print "draw SLAM slam.out0000_kf_kfOw.kml"
            elif re.match(r'.*_slam.out0001_kf_kfOw\.kml$', f):
                plt.plot(all_coord[f + "_x"], all_coord[f + "_y"], 'k-', label='SLAM slam.out01_kfOw.kml', linewidth=1)
                print "draw SLAM slam.out0001_kf_kfOw.kml"
            elif re.match(r'.*_slam.out0002_kf_kfOw\.kml$', f):
                plt.plot(all_coord[f + "_x"], all_coord[f + "_y"], 'c-', label='SLAM slam.out02_kfOw.kml', linewidth=1)
                print "draw SLAM slam.out0002_kf_kfOw.kml"

        plt.xlabel("longitude", fontsize=15)
        plt.ylabel("latitude", fontsize=15)
        # set label in title location
        plt.legend(bbox_to_anchor=(0., 1, 1., .1), loc=3,
                   ncol=2, mode="expand", borderaxespad=0.)
        # save picture in high quality
        plt.savefig(path + "/kml_track.png", dpi=300)
    else:
        print "draw picutre failed!!!"


if __name__ == '__main__':
    all_coord = {}
    total_len = []
    opt_val = parse_options()
    # store all coordinates by dict
    all_files = TraversalFile(opt_val['input'])
    coord = GetAllKml(opt_val['input'])

    # generate orange area kml
    gen_LineString_kml('pre_process_gps.kml', 0.00001, 'pre_process_gps.socpe_1_meter1.kml', 'ff0055ff')
    # generate yellow area kml
    gen_LineString_kml('pre_process_gps.kml', 0.00007, 'pre_process_gps.socpe_7_meter1.kml', 'ff00ffff')
    gen_LineString_kml('pre_process_gps.kml', 0.0002, 'pre_process_gps.socpe_20_meter1.kml', 'ff00ffff')
    # num_gps = check_kml('pre_process_gps.kml','good_hq_gps.kml',0.00001)
    # check_kml2('pre_process_gps.kml','good_hq_slam.kml',0.0002)
    # num_slam = check_kml2('pre_process_gps.kml','good_hq_slam.kml',0.00007)
    check_kml2('pre_process_gps.kml', 'kfOw.kml', 0.0002)
    num_out2kml = check_kml2('pre_process_gps.kml', 'kfOw.kml', 0.00007)
    total_num = num_out2kml
    print "total_num = %s" % total_num
    print "\n"

    # length of raw gps kml
    raw_gps_distance = len_list[raw_gps_kml_file]
    print "raw_gps_distance ======> %s" % raw_gps_distance
    # length of total
    total_len = TotalLength(opt_val['input'])
    # calculate gps.kml rate
    cal_rate(total_len[0], raw_gps_distance, '0.1', 'gps.kml')
    # calculate slam.kml rate
    cal_rate(total_len[1], raw_gps_distance, '0.2', 'slam.kml')

    # draw picture
    ori_gps_kml = opt_val['input'] + "/pre_process_gps.kml"
    shapely_scope_7_kml = opt_val['input'] + "/pre_process_gps.socpe_7_meter1.kml.area.kml"
    shapely_scope_20_kml = opt_val['input'] + "/pre_process_gps.socpe_20_meter1.kml.area.kml"
    draw(all_files, opt_val['input'])
