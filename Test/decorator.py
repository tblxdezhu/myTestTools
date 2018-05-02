#!/usr/bin/env python

# @Time    : 24/04/2018 4:44 PM
# @Author  : Zhenxuan Xu
# @Site    : 
# @File    : decorator.py
# @Software: PyCharm


def printf(func):
    def inner():
        print "run inner()"

    return inner


@printf
def myprint():
    print "run myprint()"


if __name__ == '__main__':
    myprint()
