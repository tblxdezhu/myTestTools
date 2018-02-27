#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 09/02/2018 5:04 PM
# @Author  : Zhenxuan Xu
# @Site    : 
# @File    : test.py
# @Software: PyCharm
import collections

A = collections.OrderedDict([
    ("a", 1),
    ("b", 2),
    ("c", 3)
])

if __name__ == '__main__':
    for k in A:
        print A[k]
