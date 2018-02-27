#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 29/01/2018 4:00 PM
# @Author  : Zhenxuan Xu
# @Site    : 
# @File    : log.py
# @Software: PyCharm

import logging
import sys

class Logger:
    def __init__(self, log_name, logger):
        self.logger = logging.getLogger(logger)
        self.logger.setLevel(logging.DEBUG)
        file_handler = logging.FileHandler(log_name)
        file_handler.setLevel(logging.DEBUG)
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        formatter = logging.Formatter(fmt='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                                      datefmt='%a, %d %b %Y %H:%M:%S')
        file_handler.setFormatter(formatter)
        ch.setFormatter(formatter)
        self.logger.addHandler(file_handler)
        self.logger.addHandler(ch)

    def get_log(self):
        return self.logger
