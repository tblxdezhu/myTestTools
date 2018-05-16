# !/usr/bin/env python
# -*- coding: utf-8 -*-*
# @Author: zhenxuan.xu
# @Date: 2018-01-31 10:36:13
# @Last Modified by:   zhenxuan.xu
# @Last Modified time: 2018-01-31 10:36:13


import sys
import os
# from Analyse import slam_test_report
# from Compile import mygit
from Run import run_SLAM_in_debug
from tools import func
from tools import log
from tools import send_email
import time
import coloredlogs
import datetime


# def main_2():
#     cases_standard = slam_test_report.ResultCheck(
#         "/Users/test1/Documents/tools/test_data/20171211_220431_debug_feiyang_master_ccdemo")
#     cases_develop = slam_test_report.ResultCheck(
#         "/Users/test1/Documents/tools/test_data/20171211_215334_debug_feiyang_20238_ccdemo")

#     data_preprocessing = slam_test_report.DataProcess(cases_standard.check_have_snippet(),
#                                                       cases_develop.check_have_snippet())
#     data_preprocessing.check_case_if_in_common()
#     data_preprocessing.data_process()
#     data_preprocessing.draw()


def main():
    script_mode, config_file, output_path, debug_switch = func.get_parser()
    # if func.config_from_json(config_file, 'run_config')["compile code"] == "ON":
    #     if mygit.pull(config_file):
    #         send_email.send_email(config_file, 'msg')
    #         os.chdir(sys.path[0])
    #         cases_set_dict = func.config_from_json(config_file, "cases_config")
    #         for k in cases_set_dict:
    #             log_file_name = ''.join([time.strftime('%Y-%m-%d_%H_%M_%S', time.localtime(
    #                 time.time())), '_', os.path.basename(cases_set_dict[k][0]), '.log'])
    #             logger = log.Logger(log_name=log_file_name, logger=k).get_log()
    #             coloredlogs.install(level='DEBUG', logger=logger)
    #             date_now = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    #             output_dir = os.path.join(output_path,
    #                                       date_now + "_debug_" + func.config_from_json(config_file, "run_config")[
    #                                           "owner"] + "_" + func.config_from_json(config_file, "run_config")[
    #                                           "branch"] + "_" + k)
    #             run_SLAM_in_debug.main_flow(
    #                 cases_set_dict[k], logger, script_mode, config_file, output_path, debug_switch, output_dir)
    #     else:
    #         print "没有更新，没有触发自动测试"
    # else:
    os.chdir(sys.path[0])
    cases_set_dict = func.config_from_json(config_file, "cases_config")
    for k in cases_set_dict:
        os.chdir(sys.path[0])
        log_file_name = ''.join([time.strftime('%Y-%m-%d_%H_%M_%S', time.localtime(
            time.time())), '_', os.path.basename(cases_set_dict[k][0]), '.log'])
        logger = log.Logger(log_name=log_file_name, logger=k).get_log()
        coloredlogs.install(level='DEBUG', logger=logger)
        date_now = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        output_dir = os.path.join(output_path,
                                  date_now + "_debug_" + func.config_from_json(config_file, "run_config")[
                                      "owner"] + "_" + func.config_from_json(config_file, "run_config")[
                                      "branch"] + "_" + k)
        run_SLAM_in_debug.main_flow(
            cases_set_dict[k], logger, script_mode, config_file, output_path, debug_switch, output_dir)
    send_email.send_email(config_file, "msg")


if __name__ == '__main__':
    main()
