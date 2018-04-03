#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 02/04/2018 11:52 AM
# @Author  : Zhenxuan Xu
# @Site    : 
# @File    : result_analyse.py
# @Software: PyCharm
from __future__ import division
import sys
import os
import traceback
import json
from pyecharts import Bar
from pyecharts import Page
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
    def __init__(self, case_set):
        self.case_set = case_set
        self.case_set_names = {}
        self.list_diff = {}
        self.data = {"slam": {}, "alignment": {}, "alignment2": {}, "rt": {}, "slamwithdb": {}}

    def check_case_in_common(self):
        for mode in ["slam", "alignment", "alignment2", "rt", "slamwithdb"]:
            self.case_set_names[mode] = []
            for case in self.case_set:
                if case:
                    if case["mode"] == mode:
                        self.case_set_names[mode].append(case["name"])

    def data_process(self):
        self.read_json()
        for mode in ["slam", "alignment", "alignment2", "rt", "slamwithdb"]:
            for key in self.performance_criteria:
                self.data[mode][key] = []
                for case in self.case_set:
                    if case:
                        if case["mode"] == mode:
                            self.data[mode][key].append(case[key])


def draw(datas, keys, names):
    for mode in ["slam", "alignment", "alignment2", "rt", "slamwithdb"]:
        page = Page(page_title="(%s) SLAM Performance Test Report" % mode)
        radar = Radar()
        for data in datas:
            num = len(datas[data][mode]["kf_num"])
            schema = [
                ("kf数量", 3000 * num), ("lost数量", 100 * num), ("分段数", 10 * num),
                ("3D点数量", 70000 * num), ("耗时", 4000 * num)
            ]
            radar.config(schema)
            values = [[s2i(datas[data][mode]["kf_num"]), s2i(datas[data][mode]["lost_num"]),
                       sum(datas[data][mode]["section_num"]), s2i(datas[data][mode]["mp_num"]),
                       s2i(datas[data][mode]["time"]), 19000]]
            radar.add(data, values, is_splitline=True, is_axisline_show=True, is_area_show=False,
                      legend_selectedmode='normal')
            print datas[data][mode]
            for key in keys:
                draw_in_type(version=data, value=datas[data][mode][key], attr=names[mode], page=page, key_name=key)
        page.add(radar)
        page.render(path="../Reports/SLAM_Performance_%s.html" % mode)


def s2i(str_list):
    return sum(map(eval, str_list))


def draw_in_type(version, value, attr, page, key_name):
    bar = Bar(key_name)
    bar.add(version, attr, value, is_datazoom_show=True, datazoom_range=[10, 13], is_label_show=True,
            is_random=False, is_more_utils=True, mark_line=["average"], mark_point=["max", "min"])
    page.add(bar)


def mylist(in_list):
    global intersection_list
    global n
    if n == 0:
        intersection_list = in_list
        n = n + 1
        return intersection_list
    diff_list = list(set(intersection_list) ^ set(in_list))
    intersection_list = list(set(intersection_list) - set(diff_list))
    n = n + 1
    return intersection_list


def backup_diff(cases_path, diff_dic):
    for mode in ["slam", "alignment", "alignment2", "rt", "slamwithdb"]:
        for case_set in os.listdir(cases_path):
            if os.path.exists(os.path.join(cases_path, case_set, mode)):
                for case in os.listdir(os.path.join(cases_path, case_set, mode)):
                    if case in diff_dic[mode]:
                        pass
                    else:
                        if cases_path.endswith("/"):
                            cases_path = os.path.dirname(cases_path)
                        backup_path = os.path.join(os.path.dirname(cases_path), "backup_diff_cases")
                        if not os.path.exists(backup_path):
                            print "mkdir ", backup_path
                            os.system("mkdir " + backup_path)
                        mv_cmd = "mv " + os.path.join(cases_path, case_set, mode, case)+" "+backup_path
                        print mv_cmd
                        os.system(mv_cmd)


def make_cases_in_common(cases_path):
    case_dic = {}
    diff_dic = {}
    for case in os.listdir(cases_path):
        case_path = os.path.join(cases_path, case)
        data_preprocess = DataProcess(ResultCheck(case_path).check_have_snippet())
        data_preprocess.check_case_in_common()
        case_dic[case] = data_preprocess.case_set_names
    for mode in ["slam", "alignment", "alignment2", "rt", "slamwithdb"]:
        for case in case_dic:
            diff_dic[mode] = mylist(case_dic[case][mode])
    backup_diff(cases_path, diff_dic)


def main():
    case_sets = sys.argv[1]
    data_for_draw = {}
    performance_criteria = []
    attr = {}
    global intersection_list
    intersection_list = []
    global n
    n = 0
    make_cases_in_common(case_sets)
    for case_set in os.listdir(case_sets):
        version = case_set.split("_")[-2] + "_" + case_set.split("_")[1]
        case_set_path = os.path.join(case_sets, case_set)
        data_processing = DataProcess(ResultCheck(case_set_path).check_have_snippet())
        data_processing.data_process()
        data_for_draw[version] = data_processing.data
        performance_criteria = data_processing.performance_criteria
        attr = data_processing.case_set_names
    print performance_criteria
    draw(data_for_draw, performance_criteria, attr)


if __name__ == '__main__':
    main()
