#!/usr//bin/python
# -*- coding:utf-8 -*-

'''
check return code of algorithm
 
Create on March 28, 2018
@author: Yu Li
'''

import os
import re

def Checkcode(dir_path_list, end):
    '''
    @summary: check the return code of algorithm
    @param dir_path_list: path of algorithm log
    @param end: file of .log       
    @return: meg : algorithm execute successfully or failed
    '''
    try:
	flag=False
        file_list = []
        meg=''
        for root, dirs, files in os.walk(dir_path_list):
            for fp in files:
                if fp.endswith(end):
                    file_path = os.path.join(root, fp)
                    file_list.append(file_path)
        code_list=[]
        for i in range(len(file_list)):
            code = int(file_list[i].split('/')[-2])
            code_list.append(code)
        for j in code_list:
           if j !=0:
		flag=True
	if flag:
           meg = 'algorithm execute failed'
	   print meg
	else: 
           meg = 'algorithm execute successfully'
	   print meg
	return meg
    except IOError:
        print traceback.print_exc()

if __name__ == '__main__':
    #dir_path_list = '/home/test/Downloads/253276467824'
    #end = '.log'
    Checkcode(dir_path_list, end)

