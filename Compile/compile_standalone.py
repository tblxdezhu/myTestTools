#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 09/02/2018 3:44 PM
# @Author  : Zhenxuan Xu
# @Site    : 
# @File    : compile_standalone.py
# @Software: PyCharm

import sys
import os
import json
import commands
import traceback
import logging
import collections

COMMON = {
    "mode": "debug",  # release/debug
    "visualization": "OFF",  # OFF/ON
    "compile_other_modules": "ON"  # default compile module is SLAM
}
VEHICLE = collections.OrderedDict([
    ("common", "master"),
    ("core/common", "master"),
    ("core/algorithm_common", "master"),
    ("core/algorithm_vehicle_slam", "master"),
    ("core/vehicle", "master")
])
SERVER = {
    "core/algorithm_sam": "master",
    # TODO 先只做debug模式，release接口后面再写

}


class Logger:
    def __init__(self, log_name, logger):
        self.logger = logging.getLogger(logger)
        self.logger.setLevel(logging.DEBUG)
        file_handler = logging.FileHandler(log_name)
        file_handler.setLevel(logging.DEBUG)
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        formatter = logging.Formatter(fmt='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                                      datefmt='%a, %d %b %Y %H:%M:%S')
        file_handler.setFormatter(formatter)
        ch.setFormatter(formatter)
        self.logger.addHandler(file_handler)
        self.logger.addHandler(ch)

    def get_log(self):
        return self.logger


class Compile:
    def __init__(self, module_name, branch_name):
        self.module_name = module_name
        self.branch_name = branch_name
        if COMMON["mode"] == "debug" and self.module_name == "core/algorithm_vehicle_slam":
            self.module_path = os.path.join(code_path, self.module_name, "example")
        else:
            self.module_path = os.path.join(code_path, self.module_name)
        self.flag = False

    def get_branch(self):
        try:
            os.chdir(self.module_path)
            branchs = os.popen("git branch").readlines()
            for branch in branchs:
                if "*" in branch:
                    return branch.strip("\n")
        except Exception:
            print traceback.print_exc()

    def git_pull(self):
        try:
            os.chdir(self.module_path)
            cmd_checkout = "git checkout " + self.branch_name
            cmd_gitpull = "git pull"
            os.system(cmd_checkout)
            status, outputs = commands.getstatusoutput(cmd_gitpull)
            if not status == 0:
                logger.error("%s pull failed", self.module_name)
        except Exception:
            print traceback.print_exc()

    def build(self):
        try:
            os.chdir(self.module_path)
            exec_cmd(dic_cmd[self.module_name], 'OFF')
        except Exception:
            print traceback.print_exc()

    @property
    def branch(self):
        return self.get_branch()


def check_build_brach(config):
    try:
        for k in config:
            compile_module = Compile(k, config[k])
            logger.info("%s %s", k, compile_module.branch)
            compile_module.git_pull()
        build_cmd()
        for k in config:
            compile_module = Compile(k, config[k])
            logger.info("%s", compile_module.module_name)
            if compile_module.module_name == "core/vehicle":
                logger.info("don't need compile in debug mode")
                continue
            compile_module.build()
    except AttributeError, IndexError:
        print traceback.print_exc()


def build_cmd():
    try:
        common_build = "./build.sh"
        dic_cmd["common"] = common_build
        dic_cmd["core/common"] = common_build
        dic_cmd["core/vehicle"] = common_build
        if COMMON["mode"] == "debug":
            logger.warning("compile mode is debug")
            dic_cmd["core/algorithm_common"] = "./build.sh -g"
            dic_cmd["core/algorithm_sam"] = "./build.sh -ag"
            if COMMON["visualization"] == "OFF":
                dic_cmd["core/algorithm_vehicle_slam"] = "./build.sh -d"
            else:
                dic_cmd["core/algorithm_vehicle_slam"] = "./build.sh"
    except Exception:
        print traceback.print_exc()


def exec_cmd(cmd, debug_switch):
    if debug_switch == "ON":
        logger.info(cmd)
    else:
        os.system(cmd)
        # status, outputs = commands.getstatusoutput(cmd)
        # if not status == 0:
        #     logger.error("%s", outputs)


if __name__ == '__main__':
    logger = Logger(log_name="compile.log", logger="test").get_log()
    code_path = sys.argv[1]
    if not code_path.endswith("/"):
        code_path += "/"
    dic_cmd = {}
    check_build_brach(VEHICLE)
    if not COMMON["compile_other_modules"] == "OFF":
        logger.warning("START COMPILE SERVER")
        check_build_brach(SERVER)
