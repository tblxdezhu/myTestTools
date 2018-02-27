# !/usr/bin/env python
# -*- coding: utf-8 -*-*
# @Author: zhenxuan.xu
# @Date: 2018-01-31 10:39:20
# @Last Modified by:   zhenxuan.xu
# @Last Modified time: 2018-01-31 10:39:20

import sys
import json
from optparse import OptionParser


def config_from_json(config_file, keyword):
    """
        Reading parameters from the configuration file
    :param config_file: json files
    :param keyword:
    :return:
    """
    with open(config_file, 'r') as cf:
        configs = json.load(cf)[keyword]
    return configs


def get_parser():
    """

    :return:
    """
    parser = OptionParser(usage="%prog [-m] [-f] [-o]", version="%prog 1.0")
    parser.add_option("-m", dest="mode", help="Select the run mode of script: slam (default), alignment or whole",
                      default="slam")
    parser.add_option("-f", dest="config_file",
                      help="Select your config file (necessary!)")
    parser.add_option("-o", dest="output_path",
                      help="Select the PATH of your outputs,default is '/home/test/xuzhenxuan/outputs'",
                      default="/home/test/xuzhenxuan/outputs")
    parser.add_option("-e", dest="debug_switch",
                      help="Select whether open the debug mode of script OFF or ON,default is OFF",
                      default="OFF")
    (options, args) = parser.parse_args()
    if len(sys.argv) == 1 or options.mode not in ["slam", "alignment", "whole"] or options.debug_switch not in ['ON', 'OFF']:
        print parser.error("You can enter '-h' to see the detailed usage")
    if options.config_file == None:
        print parser.error("You must specify a configuration file")
    return options.mode, options.config_file, options.output_path, options.debug_switch
