#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 19/04/2018 3:07 PM
# @Author  : Zhenxuan Xu
# @Site    : 
# @File    : function.py
# @Software: PyCharm

import random


# 1
def factorial(n):
    """:returns n"""
    return 1 if n < 2 else n * factorial(n - 1)


# 2
class BingoCage:
    def __init__(self, items):
        self._items = list(items)
        random.shuffle(self._items)

    def pick(self):
        try:
            return self._items.pop()
        except IndexError:
            raise LookupError("pick from empty BingoCage")

    def __call__(self):
        return self.pick()




if __name__ == '__main__':
    # 1 print factorial(42)
    # 2 bingo = BingoCage(range(0))
    # print bingo._items
    # print bingo.pick()
    # print bingo()
    print dir(factorial)
