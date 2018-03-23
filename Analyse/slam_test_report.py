#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 14/12/2017 10:47 AM
# @Author  : Zhenxuan Xu
# @Site    : 
# @File    : slam_test_report.py
# @Software: PyCharm
from __future__ import division
import os
import sys
import traceback
import json
from pyecharts import Bar
from pyecharts import Line
from pyecharts import Grid
from pyecharts import Page
from pyecharts import Style, Pie
from pyecharts import Radar


class ResultCheck:
    """
        This is the class of test set,always it has many cases in folder of "slam,alignment,rt"
    """

    def __init__(self, str_path):
        """
        :param str_path: test set path
        """
        self.set_path = str_path
        self.is_have_snippet = False
        basename = os.path.basename(self.set_path)
        # TODO 这个地方需要加入越界异常判断
        self.time = basename.split("_")[0] + basename.split("_")[1]
        self.interface, self.owner, self.branch, self.set = basename.split("_")[2:]
        self.path = ""
        self.performance_criteria = {}
        self.performance_alignment_criteria = {}
        self.config_snippet = {}

    def get_case_in_mode(self):
        """
        judge the mode of case : slam , alignment ,rt
        :return: the mode of case
        """
        modes = os.listdir(self.set_path)
        case_in_mode = {}
        for mode in modes:
            case_in_mode[mode] = os.listdir(os.path.join(self.set_path, mode))
        return case_in_mode

    def read_json(self):
        """
        read config from config.json
        :return: config dic
        """
        with open("../common.json", 'r') as f:
            data = json.load(f)
            self.performance_criteria = data["result_analyse_config"][0]
            self.performance_alignment_criteria = data["result_analyse_config"][1]
            self.config_snippet = data["result_analyse_config"][2]

    def check_have_snippet(self):
        self.read_json()
        self.rate_dic = {}
        self.all_case = []
        for k in self.get_case_in_mode():
            success_case_dic = {k: []}
            failed_case_dic = {k: []}
            for case in sorted(self.get_case_in_mode()[k]):
                self.path = os.path.join(self.set_path, k, case)
                find_snippet_cmd = "find " + self.path + " -name " + self.config_snippet[k]
                check_result = os.popen(find_snippet_cmd).readlines()
                if check_result:
                    self.is_have_snippet = True
                    success_case_dic[k].append(self.path)
                    quality_in_case = QualityAnalyse(self.path, case, k)
                    quality_in_case.check_quality()
                    if quality_in_case.is_have_quality:
                        quality_in_case.quality_analyse()
                        del quality_in_case.__dict__["performance_criteria"]
                        del quality_in_case.__dict__["performance_alignment_criteria"]
                        del quality_in_case.__dict__["config_snippet"]
                        self.all_case.append(quality_in_case.__dict__)
                    else:
                        # TODO 后续会修改为logging模块
                        print "%s don't have quality file" % quality_in_case.name
                else:
                    failed_case_dic[k].append(self.path)
            self.rate_dic[k] = len(success_case_dic[k]) / (len(success_case_dic[k]) + len(failed_case_dic[k]))
        return self.all_case

    @property
    def get_status(self):
        return self.check_have_snippet()


class QualityAnalyse(ResultCheck):
    def __init__(self, path, case, mode):
        self.path = path
        self.name = case
        self.mode = mode
        self.is_have_quality = True
        self.quality_path = ""
        self.quality_rtv_name = ""
        self.section_num = 0
        self.high_quality_slam_coverage = 0.0
        self.total_length_slam = 0.0
        self.total_length_gps = 0.0
        self.kf_per_km = 0.0
        self.mp_per_km = 0.0
        self.lost_num = 0
        self.kf_num = 0
        self.mp_num = 0
        self.time = 0.0

    def check_quality(self):
        find_quality_cmd = "find " + self.path + " -name quality.txt"
        check_result = os.popen(find_quality_cmd).readlines()
        if not check_result:
            self.is_have_quality = False
        else:
            self.quality_path = check_result[0].strip("\n")

    def quality_analyse(self):
        self.read_json()
        try:
            with open(self.quality_path, 'r') as file_to_read:
                lines = file_to_read.readlines()
                self.quality_rtv_name = lines[0].split(".rtv")[0].strip().split(" ")[1]
                if self.quality_rtv_name not in self.quality_path:
                    raise IOError
                else:
                    # TODO 简化这部分代码
                    self.section_num = len(self.grep_text_in_quality(self.performance_criteria["section_num"]))
                    self.high_quality_slam_coverage = self.grep_data_in_quality(
                        self.performance_criteria["high_quality_slam_coverage"])
                    self.total_length_slam = self.grep_data_in_quality(self.performance_criteria["total_length_slam"])
                    self.total_length_gps = self.grep_data_in_quality(self.performance_criteria["total_length_gps"])
                    self.kf_num = self.grep_data_in_quality(self.performance_criteria["kf_num"])
                    self.mp_num = self.grep_data_in_quality(self.performance_criteria["mp_num"])
                    self.time = self.grep_data_in_quality(self.performance_criteria["time"])
                    self.kf_per_km = self.grep_data_in_quality(self.performance_criteria["kf_per_km"])
                    self.mp_per_km = self.grep_data_in_quality(self.performance_criteria["mp_per_km"])
                    self.lost_num = self.grep_data_in_quality(self.performance_criteria["lost_num"])
                    if self.mode == 'alignment' or self.mode == 'alignment2':
                        self.usage_rate_of_mp_in_db = self.grep_data_in_quality(
                            self.performance_alignment_criteria["usage_rate_of_mp_in_db"])
                        self.cr_of_new_mp = self.grep_data_in_quality(
                            self.performance_alignment_criteria["cr_of_new_mp"])
                        self.cr_of_new_kf = self.grep_data_in_quality(
                            self.performance_alignment_criteria["cr_of_new_kf"])
                        self.slam_cost_time = self.grep_data_in_quality(
                            self.performance_alignment_criteria["slam_cost_time"])
                        self.alignment_cost_time = self.grep_data_in_quality(
                            self.performance_alignment_criteria["alignment_cost_time"])
        except IOError:
            print traceback.print_exc()

    def grep_text_in_quality(self, keyword):
        return os.popen("grep '" + keyword + "' " + self.quality_path + " -n").readlines()

    def grep_data_in_quality(self, keyword):
        return self.grep_text_in_quality(keyword)[0].split(":")[-1].strip()


class DataProcess(ResultCheck):
    def __init__(self, standard_set, develop_set):
        self.standard_set = standard_set
        self.develop_set = develop_set
        self.standard_set_names = {}
        self.develop_set_names = {}
        self.list_diff = {}
        self.data_standard = {"slam": {}, "alignment": {}, "alignment2": {}, "rt": {}}
        self.data_develop = {"slam": {}, "alignment": {}, "alignment2": {}, "rt": {}}

    def check_case_if_in_common(self):
        for mode in ["slam", "alignment", "alignment2", "rt"]:
            self.standard_set_names[mode] = []
            self.develop_set_names[mode] = []
            self.list_diff[mode] = []
            for case in self.standard_set:
                if case:
                    if case["mode"] == mode:
                        self.standard_set_names[mode].append(case["name"])
            for case in self.develop_set:
                if case:
                    if case["mode"] == mode:
                        self.develop_set_names[mode].append(case["name"])
            self.list_diff[mode] = list(set(self.standard_set_names[mode]) ^ set(self.develop_set_names[mode]))
            if self.list_diff[mode]:
                for diff_case in self.list_diff[mode]:
                    if diff_case in self.standard_set_names[mode]:
                        print "your branch don't run out %s, mode is %s" % (diff_case, mode)
                        self.standard_set_names[mode].remove(diff_case)
                        for case in self.standard_set:
                            if case:
                                if case["name"] == diff_case and case["mode"] == mode:
                                    case.clear()
                    else:
                        print "master/release don't run out %s, mode is %s" % (diff_case, mode)
                        self.develop_set_names[mode].remove(diff_case)
                        for case in self.develop_set:
                            if case:
                                if case["name"] == diff_case and case["mode"] == mode:
                                    case.clear()

    def data_process(self):
        self.read_json()
        for mode in ["slam", "alignment", "alignment2", "rt"]:
            for key in self.performance_criteria:
                self.data_standard[mode][key] = []
                self.data_develop[mode][key] = []
                for case in self.standard_set:
                    if case:
                        if case["mode"] == mode:
                            self.data_standard[mode][key].append(case[key])
                for case in self.develop_set:
                    if case:
                        if case["mode"] == mode:
                            self.data_develop[mode][key].append(case[key])

    def draw(self):
        for mode in ["slam", "alignment", "alignment2", "rt"]:
            page = Page(page_title="(%s) SLAM Performance Test Report" % mode)
            num = len(self.data_standard[mode]["kf_num"])
            # TODO 这个地方的自适应还没修改
            schema = [
                ("kf数量", 3000 * num), ("lost数量", 30 * num), ("分段数", 10 * num),
                ("3D点数量", 70000 * num), ("耗时", 4000 * num)
            ]
            v1 = [[s2i(self.data_standard[mode]["kf_num"]), s2i(self.data_standard[mode]["lost_num"]),
                   sum(self.data_standard[mode]["section_num"]), s2i(self.data_standard[mode]["mp_num"]),
                   s2i(self.data_standard[mode]["time"]), 19000]]
            v2 = [[s2i(self.data_develop[mode]["kf_num"]), s2i(self.data_develop[mode]["lost_num"]),
                   sum(self.data_develop[mode]["section_num"]), s2i(self.data_develop[mode]["mp_num"]),
                   s2i(self.data_develop[mode]["time"]), 19000]]
            radar = Radar()
            radar.config(schema)
            radar.add(sys.argv[1].split("_")[-2], v1, is_splitline=True, is_axisline_show=True)
            radar.add(sys.argv[2].split("_")[-2], v2, label_color=["#4e79a7"], is_area_show=False,
                      legend_selectedmode='normal')
            page.add(radar)
            for key in self.performance_criteria:
                draw_in_type(self.data_standard[mode][key], self.data_develop[mode][key], self.standard_set_names[mode],
                             page, key)
            page.render(path="../Reports/SLAM_Performance_%s.html" % mode)


def s2i(str_list):
    return sum(map(eval, str_list))


def draw_in_type(v1, v2, attr, page, key):
    bar = Bar(key)
    bar.add(sys.argv[1].split("_")[-2], attr, v1, is_label_show=True)
    bar.add(sys.argv[2].split("_")[-2], attr, v2, is_datazoom_show=True, is_label_show=True, is_random=False,
            is_more_utils=True)
    page.add(bar)


def float2percent(num):
    print '%.2f%%' % (num * 100)


# TODO 发送通知，附带测试报告地址
def send_email():
    pass


def main():
    cases_standard = ResultCheck(sys.argv[1])
    cases_develop = ResultCheck(sys.argv[2])

    data_preprocessing = DataProcess(cases_standard.check_have_snippet(), cases_develop.check_have_snippet())
    data_preprocessing.check_case_if_in_common()
    data_preprocessing.data_process()
    data_preprocessing.draw()


if __name__ == '__main__':
    main()
