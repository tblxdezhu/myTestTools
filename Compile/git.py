#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 22/11/2017 10:20 AM
# @Author  : Zhenxuan Xu
# @Site    :
# @File    : git.py
# @Software: PyCharm

import sys
import os
import traceback
import commands

sys.path.append("..")
import tools.log  # noqa
import tools.func  # noqa
import tools.send_email  # noqa
# from tools import log

CONFIG = {
    "mode": "debug",  # release/debug
    "visualization": "OFF",  # OFF/ON
    "compile_other_modules": "OFF"
}

SLAM_CONFIG = {
    # feature/RDB-18520-gps-fusion
    "core/algorithm_vehicle_slam/example": "master",
    "core/vehicle": "master",
}

COMMON_CONFIG = {
    "common": "master",
    "framework/device/gmock": "master",
    "framework/device/roaddb_logger": "master",
    "framework/device/roaddb_video": "master",
    "core/common": "master",
    "core/algorithm_common": "master",
    "core/algorithm_sam": "master",
}


class Compile:
    def __init__(self, module_name, branch_name):
        self.__module_name = module_name
        self.__branch_name = branch_name
        self.__module_path = os.path.join(code_path, self.__module_name)
        self.flag = False

    def get_branch(self):
        try:
            os.chdir(self.__module_path)
            branchs = os.popen("git branch").readlines()
            for branch in branchs:
                if "*" in branch:
                    return branch.strip("\n")
        except Exception:
            print traceback.print_exc()

    def checkout_branch(self):
        try:
            os.chdir(self.__module_path)
            cmd_checkout = "git checkout " + self.__branch_name
            cmd_gitpull = "git pull"
            os.system(cmd_checkout)
            status, outputs = commands.getstatusoutput(cmd_gitpull)
            if outputs.find("insertions") != -1 and outputs.find("deletions") != -1:
                logger.warning("代码有更新，触发编译")
                self.flag = True
                self.compile_build()
                # logger.info(self.compile_build())
            else:
                if outputs.find("Please move or remove them before you can merge") != -1:
                    logger.error("代码更新冲突，正在处理...")
                    cmd_clean = "git clean -d -fx ''"
                    logger.info("%s", cmd_clean)
                    os.system(cmd_clean)
                    self.checkout_branch()
                logger.warning("代码没有更新")
            flags.append(self.flag)
            # logger.info("%s,%s %s", self.module, ">" * 20, self.branch)
            # logger.info("start to compile module %s", self.module)

        except Exception:
            print traceback.print_exc()

    def compile_build(self):
        if self.module == "core/algorithm_vehicle_slam/example":
            if CONFIG["visualization"] == "OFF":
                # status,outputs = commands.getstatusoutput("./build.sh -d")
                os.system("./build.sh -d")
            else:
                # status, outputs = commands.getstatusoutput("./build.sh")
                os.system("./build.sh")
        else:
            # status, outputs = commands.getstatusoutput("./build.sh")
            os.system("./build.sh")
        # return outputs

    def check_compile_result(self):
        # TODO add check_compile_result
        pass  # OFF/ON

    def comile_debug_mode(self):
        # TODO add debug mode
        pass

    @property
    def branch(self):
        return self.get_branch()

    @property
    def module(self):
        return self.__module_name


def check_object_brach(config):
    try:
        for k in config:
            compile_module = Compile(k, config[k])
            compile_module.checkout_branch()
            compile_module.check_compile_result()
    except AttributeError, IndexError:
        print traceback.print_exc()


def pull(config_file):
    # TODO 日志重复写入问题，待解决(重复写入也可以)
    # TODO git模块增加debug模式
    try:
        global logger
        logger = tools.log.Logger(
            log_name="compile.log", logger="test").get_log()
        global code_path
        code_path = tools.func.config_from_json(
            config_file, "run_config")["sourcecode_path"]
        global flags
        flags = []
    except Exception, e:
        logger.error("read config error @git_pull")
        tools.send_email.send_email()
    else:
        if not code_path.endswith("/"):
            code_path += "/"
        if not CONFIG["compile_other_modules"] == "OFF":
            check_object_brach(COMMON_CONFIG)
        check_object_brach(SLAM_CONFIG)
        if True in flags:
            return True
        else:
            return False
    

    # os.chdir(os.getcwd()+"/../")
    # tools.send_email.send_email()
