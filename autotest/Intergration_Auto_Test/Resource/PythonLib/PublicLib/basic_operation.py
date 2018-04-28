#!/usr/bin/env python
# encoding: utf-8
'''
Define some common function
 
Create on 3/20/18
@author: Siqi Zeng

'''
import os
import commands
import logging
import time


def mount_resource_to_local(remote_ip, remote_path, remote_user, remote_password, local_path):
    '''
    mount resource to local
    param remote_ip: resource server ip
    param remote_path: resource server mount path
    param remote_user: resource server login username
    param remote_password: resource server login password
    param local_path: local mount path
    return:result
    '''

    result=True
    #if local path not exist, create it
    if not os.path.exists(local_path):
        try:
            os.system('mkdir {path}'.format(path=local_path))
        except Exception, e:
            logging.info(str(e))
            result = False
    else:
        #if local path exist, get all mount point, and umount it
        mount = commands.getoutput('mount -v')
        lines = mount.split('\n')
        all_points = map(lambda line: line.split()[2], lines)
        for ponit in all_points:
            if local_path == ponit:
                    os.system('sudo umount {path}'.format(path=local_path))
    try:
       os.system('sudo mount -t cifs //{resource_ip}{resource_path} {local_path} -o username={resource_username},password={resource_password}'.format(resource_ip=remote_ip,
                                                                                     resource_path=remote_path,
                                                                                     resource_username=remote_user,
                                                                                     resource_password=remote_password,
                                                                                     local_path=local_path))
    except Exception, e:
        logging.info(str(e))
        result = False
    return result

def print_input_line():
    pass

def print_execute_line():
    pass

def print_check_results_line():
    pass
    
def get_current_unix_timestamp(exact_number=13):
    '''
    get the unix timestamp
    param exact_number: the exact number of digits, default is 13, Others are considered 10
    return: timestamp
    '''
    unix_time = time.time()
    if exact_number==13:
        timestamp = int(round(unix_time * 1000))
    else:
        timestamp = int(unix_time)
    return timestamp