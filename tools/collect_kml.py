#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 19/03/2018 3:03 PM
# @Author  : Zhenxuan Xu
# @Site    : 
# @File    : collect_kml.py
# @Software: PyCharm

import sys
import os
import commands


class MyException(Exception):
    def __init__(self, err=""):
        Exception.__init__(self, err)


def find_file(file_type, input_path):
    """
    find the file and return the list
    :param file_type: the type of file which you want to find
    :param input_path: the input path
    :return:files list
    """
    try:
        find_cmd = "find " + input_path + " -name '" + file_type + "'"
        status, files = commands.getstatusoutput(find_cmd)
        if not status == 0:
            raise MyException
        files = files.split("\n")
        return files
    except MyException, e:
        print find_cmd, e
        sys.exit()


def gather():
    """
    collect the kmls and rename them
    :return: None
    """
    try:
        os.mkdir("kmls")
        for kml in find_file("*.kml", sys.argv[1]):
            if os.path.basename(os.path.dirname(kml)) == "segment":
                if 'pre_process_gps' in os.path.basename(kml) or 'hq_slam' in os.path.basename(kml):
                    try:
                        case_name = kml.split("/")[-3]
                        if not case_name.endswith(".rtv"):
                            raise IndexError
                        mode = kml.split("/")[-5]
                        if mode not in ['slam', 'alignment', 'rt']:
                            raise IndexError
                        new_kml_name = mode + "_" + case_name + "_" + os.path.basename(kml)
                        os.system("cp " + kml + " ./kmls/" + new_kml_name)
                    except IndexError:
                        print "please check the index number:\n"
                        print kml
    except OSError:
        print "the folder 'kmls' is exist, please delete it"


if __name__ == '__main__':
    gather()
