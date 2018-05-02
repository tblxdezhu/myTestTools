#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 26/04/2018 3:32 PM
# @Author  : Zhenxuan Xu
# @Site    : 
# @File    : bibao.py
# @Software: PyCharm


class Average:
    def __init__(self):
        self.series = []

    def __call__(self, new_value):
        self.series.append(new_value)
        total = sum(self.series)
        return total / len(self.series)


def make_averager():
    series = []

    def averager(new_value):
        series.append(new_value)
        return sum(series) / len(series)

    return averager




if __name__ == '__main__':
    avg = Average()
    print avg(10)
    print avg(11)
    print avg(12)
    avg2 = make_averager()
    print avg2(10)
    print avg2(11)
