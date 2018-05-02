#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 09/02/2018 5:04 PM
# @Author  : Zhenxuan Xu
# @Site    : 
# @File    : test.py
# @Software: PyCharm
# import collections
# import send_email
import sys
import os


# A = collections.OrderedDict([
#     ("a", 1),
#     ("b", 2),
#     ("c", 3)
# ])
#
# if __name__ == '__main__':
#     for k in A:
#         print A[k]


# def mylist(in_list):
#     global intersection_list
#     global n
#     if n == 0:
#         intersection_list = in_list
#         n = n + 1
#         return begin_list
#     diff_list = list(set(intersection_list) ^ set(in_list))
#     intersection_list = list(set(intersection_list) - set(diff_list))
#     n = n + 1
#     return intersection_list


def cal_md5(file_for_cal):
    md5 = os.popen("md5sum " + file_for_cal).readlines()
    print md5
    return md5


if __name__ == '__main__':
    # begin_list = []
    # n = 0
    # # send_email.send_email("../slam_test_config.json", "msg")
    # print mylist([1, 2, 3, 4, 5])
    # print mylist([2, 3, 4])
    # print mylist([1, 2, 3, 4, 5, 6])
    # print mylist([2, 4, 5, 6, 7, 9])

    file_path = sys.argv[1]
    print file_path
    with open(file_path, 'r') as f:
        texts = f.readlines()
        print texts
        dic_lib = {}
        for text in texts[1:]:
            if "=>" in text:
                print text.split("=>")[1].strip("\n").split("(")[0]
                result = os.popen("md5sum "+text.split("=>")[1].strip("\n").split("(")[0]).readlines()
                print result

                dic_lib[text.split("=>")[0].strip("\n")] = result
                # lib_path = text.split("=>")[1].strip("\n")
        print dic_lib

