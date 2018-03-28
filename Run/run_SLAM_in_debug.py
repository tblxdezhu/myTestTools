#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 05/01/2018 3:33 PM
# @Author  : Zhenxuan Xu
# @Site    :
# @File    : run_SLAM_in_debug.py
# @Software: PyCharm

import os
import sys
from optparse import OptionParser
import json
import commands
from multiprocessing import Pool
from time import sleep
import time
import shutil
import traceback
import logging
import datetime
import coloredlogs

sys.path.append("..")
from tools import func
from tools import log


class MyException(Exception):
    def __init__(self, err=""):
        Exception.__init__(self, err)


class Check:
    def check_executable_file(self, path):
        """

        :param path:
        :return:
        """
        logger.warning("START CHECK EXECUTABLE FILES")
        try:
            # TODO 根据配置文件中不同增加产品接口和debug接口适配
            # core/vehicle/dist/x64/bin/vehicleSlam
            # core/algorithm_vehicle_slam/example/debug/algoSlamExe
            relative_path = "core/algorithm_vehicle_slam/example/debug/algoSlamExe"
            executable_path = os.path.join(path, relative_path)
            if os.path.exists(executable_path):
                logger.info("algoSlamExe : PASS")
            else:
                raise MyException(err="algoSlamExe is not exist")
            if self.mode == "slam" or self.mode == "slamwithdb":
                return executable_path, None, None
            else:
                server_path = os.path.join(path, "core/algorithm_sam/example/")
                serverExampleSLAM_path = os.path.join(path, "core/algorithm_sam/build/example/serverExampleSlam")
                # TODO 下面两个可执行文件路径待定，暂时全部设定为存在
                extractor_path = os.path.join(path, "framework/device/rdb-tools-debug-tools/dist/x64/bin/rtv-extractor")
                querySection_path = os.path.join(path,
                                                 "core/algorithm_sam/example/serverExampleQueryDivision/build/querySectionByGps")
                reset_confidence_path = os.path.join(path, "core/algorithm_sam/build/example/serverExampleSlam")
                if os.path.exists(serverExampleSLAM_path):
                    logger.info("serverExampleSLAM: PASS")
                else:
                    raise MyException(err="serverExampleSLAM is not exist")
                if os.path.exists(extractor_path):
                    logger.info("rtv-extractor: PASS")
                else:
                    raise MyException(err="rtv-extractor is not exist")
                if os.path.exists(querySection_path):
                    logger.info("querySection_path: PASS")
                else:
                    raise MyException(err="querySection is not exist")
                if self.mode == "whole":
                    if os.path.exists(reset_confidence_path):
                        logger.info("serverExampleResetConfidence: PASS")
                    else:
                        raise MyException(
                            err="serverExampleResetConfidence is not exist")
                return executable_path, serverExampleSLAM_path, querySection_path, reset_confidence_path, extractor_path
        except MyException, e:
            logger.error(e)
            sys.exit()

    def check_necessary(self):
        """

        :return:
        """
        # TODO 应该在log中打印出配置信息
        check_existence_of_path(self.ip, 'high')
        check_existence_of_path(self.ic, 'high')
        check_existence_of_path(self.ivoc, 'high')

    def check_cases(self, input_path):
        """

        :param input_path:
        :return:
        """
        rtvs = find_file("*.rtv", input_path)
        imus = find_file("*.imu", input_path)
        # gpss = find_file("*.gps", input_path)
        diff_list = list(set(rtvs) ^ set(
            [imu.replace(".imu", ".rtv") for imu in imus]))
        # touch_gps_list = list(set(gpss) ^ set([rtv.replace(".rtv", ".gps") for rtv in rtvs]))
        # print touch_gps_list
        # if gpss == ['']:
        #     gpss = touch_gps_list
        # print gpss
        # for touch_gps in touch_gps_list:
        #     cmd_touch_gps = "touch " + touch_gps
        #     logger.info("%s", cmd_touch_gps)
        #     execute_cmd(cmd_touch_gps, debug_switch)
        try:
            if diff_list:
                raise ValueError
            else:
                logger.info("cases: PASS")
        except ValueError:
            logger.error(
                "There are some files not match(rtv-imu):%s", diff_list)
        else:
            # TODO 这里的返回值还没有去掉不匹配的
            return rtvs, imus


class Preparation(Check):
    def __init__(self, mode, config_file, cases, output_path):
        self.mode = mode
        self.run_configs = config_from_json(config_file, "run_config")
        self.cases = cases
        self.gps_skeleton_path = self.cases[1]
        self.output_path = output_path
        self.sourcecode_path = self.run_configs["sourcecode_path"]
        self.processes_num = self.run_configs["processes"]
        self.ip = self.sourcecode_path + "/core/vehicle/config/" + self.run_configs["slam_config"]
        # self.ic = self.sourcecode_path + "/core/vehicle/config/camera65.json"
        self.ic = self.sourcecode_path + "/core/vehicle/config/" + self.run_configs["camera"]
        self.ivoc = self.sourcecode_path + "/core/vehicle/config/Highway_Detroit_Downtown_sum--0--1799-4_voc"
        self.rtvs, self.imus = self.check_cases(self.cases[0])
        self.exec_path = self.check_executable_file(self.sourcecode_path)
        # self.server_path = self.sourcecode_path + "/core/algorithm_sam/example"
        self.server_path = self.sourcecode_path + "/core/algorithm_sam/build/example"
        self.db_path = os.path.join(self.server_path, "section_out")
        self.if_raw_gps = self.run_configs["raw gps"]
        self.slam_db_path = self.run_configs["db path"]

    def check_preparation(self):
        """

        :return:
        """
        # check_existence_of_path(self.output_path, level='high')
        if self.mode != 'slam' and self.mode != 'slamwithdb':
            check_existence_of_path(self.gps_skeleton_path, level='high')
        self.check_necessary()
        return True


class WorkFlow(Preparation):
    def vehicle_slam(self, mode):
        """

        :param mode:
        :return:
        """
        try:
            pool = Pool(processes=self.processes_num)
            logger.warning(
                "[%s]START %s and processes nums are %s", mode, mode, self.processes_num)
            for rtv in self.rtvs:
                for imu in self.imus:
                    # for gps in self.gpss:
                    if os.path.basename(rtv).strip('.rtv') == os.path.basename(imu).strip(".imu"):
                        # if os.path.basename(rtv).strip('.rtv') == os.path.basename(imu).strip(".imu"):
                        gps = rtv.replace('.rtv', '.gps')
                        logger.info("[%s]rtv:%s,imu:%s,gps:%s",
                                    mode, rtv, imu, gps)
                        output_dir = os.path.join(self.output_path, mode, os.path.basename(rtv).strip(".rtv"))
                        # if os.path.exists(os.path.join((self.output_path, mode))):
                        #     os.mkdir(os.path.join((self.output_path, mode + "2")))
                        #     output_dir = os.path.join(self.output_path, mode + "2", os.path.basename(rtv).strip(".rtv"))
                        pool.apply_async(run_slam,
                                         (mode, self.exec_path[0], self.ip, self.ic, rtv, imu, gps, self.ivoc,
                                          output_dir,
                                          self.server_path, self.if_raw_gps, self.slam_db_path))
            pool.close()
            pool.join()

        except KeyboardInterrupt:
            sys.exit()

    def server_process(self, mode):
        """

        :param mode:
        :return:
        """
        logger.warning("START SERVER PROCESS: %s", mode)
        mode_type = {'slam': '1', 'alignment': '2', 'alignment2': '2'}
        self.serverExampleSLAM_build_path = os.path.dirname(self.exec_path[1])
        copy_files(os.path.join(self.output_path, mode),
                   self.serverExampleSLAM_build_path, mode)
        serverExampleSLAM_cmd_list = [self.exec_path[1], mode_type[mode], self.serverExampleSLAM_build_path,
                                      self.serverExampleSLAM_build_path, self.gps_skeleton_path]
        serverExampleSLAM_cmd = ' '.join(serverExampleSLAM_cmd_list)
        logger.info("[%s] serverExampleSLAM_cmd:%s",
                    mode, serverExampleSLAM_cmd)
        execute_cmd(serverExampleSLAM_cmd, debug_switch)

    def query(self, gpgga_path):
        """

        :return:
        """
        logger.warning("START QUERY:")
        query_cmd_list = [self.exec_path[2], gpgga_path,
                          os.path.join(self.server_path, "section_out")]
        query_cmd = ' '.join(query_cmd_list)
        logger.info("%s", query_cmd)
        execute_cmd(query_cmd, debug_switch)
        query_out_path = os.path.join(self.server_path, "query_out")
        if os.path.exists(query_out_path):
            os.system("rm -rf " + query_out_path + "/*")
        else:
            os.mkdir(query_out_path)
        for file in os.listdir("./section"):
            with open(os.path.join("./section", file), 'r') as f:
                query_out_rtv_path = os.path.join(query_out_path, file.strip(".gps"))
                os.mkdir(query_out_rtv_path)
                dbs = f.readlines()
                for db in dbs:
                    db = db.strip("\n") + ".bin"
                    try:
                        cmd_cp_db = "cp " + os.path.join(self.db_path, db) + " " + query_out_rtv_path
                        logger.info("%s", cmd_cp_db)
                        execute_cmd(cmd_cp_db, debug_switch)
                    except Exception:
                        pass

    def reset_confidence(self):
        """

        :return:
        """
        logger.warning("START RESET CONFIDENCE")
        reset_confidence_cmd_list = [self.exec_path[3], '3', self.server_path, self.server_path, '105']
        reset_confidence_cmd = ' '.join(reset_confidence_cmd_list)
        logger.info("reset_confidence_cmd:%s", reset_confidence_cmd)
        execute_cmd(reset_confidence_cmd, debug_switch)


def config_from_json(config_file, keyword):
    """

    :param config_file:
    :param keyword:
    :return:
    """
    with open(config_file, 'r') as cf:
        configs = json.load(cf)[keyword]
    return configs


def find_file(file_type, input_path):
    """

    :param file_type:
    :param input_path:
    :return:
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


def run_slam(mode, exec_file, ip, ic, rtv, imu, gps, ivoc, path, server_path, if_raw_gps, slam_db_path):
    """

    :param mode:
    :param exec_file:
    :param ip:
    :param ic:
    :param rtv:
    :param imu:
    :param ivoc:
    :param path:
    :param server_path:
    :param if_raw_gps:
    :return:
    """
    try:
        idb = path
        os.makedirs(path)
        logger.info("mkdir %s", path)
        parameter_list = [exec_file, '--ip', ip, '--ic', ic, '--ivg', rtv, '--iimu', imu, '--igps', gps, '--ivoc', ivoc,
                          '--tmp', path,
                          '--ol', path, '--d', path, '--oqlt', path, '--osp', os.path.join(
                path, 'slam.out'), '--ivid',
                          '170ca9d4e6b40738',
                          '--ort', os.path.join(path, 'rt.out'), '--idb', idb]
        if mode == "slamwithdb":
            db_path = slam_db_path
            parameter_list.extend(['--dso', db_path])
        if mode == 'alignment' or mode == 'alignment2' or mode == "rt":
            # db_path = os.path.join(server_path, "section_out")
            db_path = os.path.join(server_path, "query_out", os.path.basename(rtv))
            parameter_list.extend(['--dso', db_path])
        else:
            pass
        if if_raw_gps == 'no':
            parameter_list.remove('--igps')
            parameter_list.remove(gps)
        else:
            pass
        cmd_vehicleSlam = ' '.join(parameter_list)
    except Exception, e:
        logger.error("%s\n%s", e, traceback.print_exc())
    logger.info("[%s] cmd_vehicleSlam:\n%s", mode, cmd_vehicleSlam)
    logger.warning("Processing...")
    execute_cmd(cmd_vehicleSlam, debug_switch)
    # TODO 可以考虑在这里加上一个日志，打印出已经跑完多少case


def check_existence_of_path(path, level):
    """

    :param path:
    :param level:
    :return:
    """
    try:
        if os.path.exists(path):
            logger.info("[Check Path] %s :PASS", path)
        else:
            raise MyException(err="is not exist")
    except MyException, e:
        logger.error("Path %s :%s", e, path)
        if level == "high":
            sys.exit()


def copy_files(files_path, output_path, mode):
    """

    :param files_path:
    :param output_path:
    :param mode:
    :return:
    """
    mode_snippet_type = {"slam": "SlamSnippet*",
                         "alignment": "incSnippet.bin", "rt": "incSnippet.bin", "alignment2": "incSnippet.bin"}
    mode_file_type = {"slam": "maplist.txt", "alignment": "inclist.txt", "alignment2": "inclist.txt"}
    try:
        if mode == "alignment2":
            mode = "alignment"
        output_path = os.path.join(output_path, mode + "out")
        if os.path.exists(output_path):
            shutil.rmtree(output_path)
        os.mkdir(output_path)
        for snippet in find_file(mode_snippet_type[mode], files_path):
            logger.info("%s", snippet)
            create_path = os.path.join(output_path, snippet.split("/")[-2])
            if not os.path.exists(create_path):
                os.mkdir(create_path)
            shutil.copy(snippet, os.path.join(
                create_path, os.path.basename(snippet)))
        logger.info("%s copy done", mode)
        os.chdir(os.path.dirname(output_path))
        cmd = "find ./ -name '" + mode_snippet_type[mode] + "' >" + os.path.dirname(
            output_path) + "/" + mode_file_type[mode]
        execute_cmd(cmd, debug_switch)
    except IndexError, e:
        logger.error("%s\n%s don't have snippets", e, files_path)


def execute_cmd(cmd, mode):
    """

    :param cmd:
    :param mode:
    :return:
    """
    if mode == "OFF":
        status, output = commands.getstatusoutput(cmd)
        if status == 0:
            logger.warning("execute succeed")
        else:
            logger.error(output)
        return output
    else:
        logger.info("%s", cmd)


def main_flow(cases, logger_in, script_mode, config_file, output_path, switch, output_dir):
    """

    :param cases:
    :return:
    """
    global logger
    global debug_switch
    logger = logger_in
    debug_switch = switch
    logger.info("\nscript mode:%s\nconfig file:%s\ncases:%s\ngps skeleton:%s\noutput path:%s", script_mode,
                config_file, cases[0], cases[1], output_dir)
    logger.warning("START CHECK PREPARATION")
    check_existence_of_path(output_path, level='high')
    preparation = Preparation(script_mode, config_file, cases, output_dir)
    if preparation.check_preparation():
        work = WorkFlow(script_mode, config_file, cases, output_dir)
        logger.warning("start process data and script mode is %s", script_mode)
        try:
            if script_mode == "slam":
                work.vehicle_slam("slam")
            elif script_mode == "slamwithdb":
                work.vehicle_slam("slamwithdb")
            elif script_mode == "alignment":
                work.output_path = os.path.dirname(work.output_path)
                work.server_process("slam")
                gpgga_path = cases[0] + "/gpggagps"
                func.rtv2gpggagps(cases[0], gpgga_path, work.exec_path[4])
                work.query(gpgga_path)
                work.vehicle_slam("alignment")
                work.server_process("alignment")
                work.query(gpgga_path)
                work.vehicle_slam("alignment2")
                work.server_process("alignment2")
                work.reset_confidence()
                work.query(gpgga_path)
                work.processes_num = 1
                work.vehicle_slam("rt")
            elif script_mode == "rt":
                work.output_path = os.path.dirname(work.output_path)
                work.server_process("alignment2")
                gpgga_path = cases[0] + "/gpggagps"
                work.reset_confidence()
                work.query(gpgga_path)
                work.processes_num = 2
                work.vehicle_slam("rt")
            elif script_mode == "whole":
                work.vehicle_slam("slam")
                work.server_process("slam")
                gpgga_path = cases[0] + "/gpggagps"
                func.rtv2gpggagps(cases[0], gpgga_path, work.exec_path[4])
                work.query(gpgga_path)
                work.vehicle_slam("alignment")
                work.server_process("alignment")
                work.query(gpgga_path)
                work.vehicle_slam("alignment2")
                work.server_process("alignment2")
                work.reset_confidence()
                work.query(gpgga_path)
                work.processes_num = 1
                work.vehicle_slam("rt")
            else:
                raise MyException
        except Exception, e:
            logger.error(e)
