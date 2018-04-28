#!/usr//bin/python
# -*- coding:utf-8 -*-

'''
check files md5 value about downloads rtv to vehicles
 
Create on March 28, 2018
@author: Yu Li
'''

import os
import sys
import commands


#path_before = sys.argv[1]
#path_after = sys.argv[2]



def checkmd5file(path_before,path_after):
    '''
    @summary: check md5 value both files before download and after download
    @param path_before: path of files before download
    @param path_after: path of files after download       
    @return: meg : md5 value is same or different
    @return: dic_before : a dictionary with corresponding files and md5 value before download
    @return: dic_after : a dictionary with corresponding files and md5 value before after
    '''
    dic_before = {}
    dic_after = {}
    for dirpath,dirnames,filenames in os.walk(path_before):
        for filename in filenames:
            md5_before='md5sum %s' % (path_before + filename)
            status, output = commands.getstatusoutput(md5_before)
            md5_value_before = output.split(' ')[0]
            dic_before[filename] = md5_value_before
    for dirpath,dirnames,filenames in os.walk(path_after):
        for filename in filenames:
            md5_after='md5sum %s' % (path_after + filename)
            status, output = commands.getstatusoutput(md5_after)
            md5_value_after = output.split(' ')[0]
            dic_after[filename] = md5_value_after
    result = cmp(dic_before,dic_after)
    if result == 0:
        #print 'md5 values are same'
        meg='md5 values are same'
    else:
        #print 'md5 values are different'
        meg='md5 values are different'
    return meg,dic_before,dic_after

if __name__ == '__main__':
    #path_before = '/home/test/Downloads/0307/RDB-20685/'
    #path_after = '/home/test/Downloads/sdcmdklsfkdsnfvjks/'
    checkmd5file(path_before,path_after)


