#!/usr/bin/env python
# encoding: utf-8

'''
realize some functions about downloader
 
Create on March 12, 2018
@author: Ying Tan
'''

import time
import simplejson as json

def reconstruct_download_data(download_data_str):
    '''
    @summary: change the string download data into json format
    @param download_data_str: input the download data with string format
    @return: return the download data in list format, whose element is json format
    '''
    download_data_list = []
    line_data = download_data_str.split("\n")

    for line in range(0, len(line_data)):
        download_data_temp = line_data[line].split("|")
        kk = 0
        current_head = {}
        current_head["id"] = download_data_temp[kk]
        current_head["code"] = download_data_temp[kk + 1]
        current_head["mesg"] = download_data_temp[kk + 2]
        current_head["device_path"] = download_data_temp[kk + 3]
        current_head["md5sum"] = download_data_temp[kk + 4]
        current_head["size"] = download_data_temp[kk + 5]
        current_head["url"] = download_data_temp[kk + 6]
        current_head["time_download"] = download_data_temp[kk + 7]
        current_head["time_install"] = download_data_temp[kk + 8]
        current_head["cmd_install"] = download_data_temp[kk + 9]
        current_head["status"] = download_data_temp[kk + 10]
        current_head["left_try_times"] = download_data_temp[kk + 11]
        current_head["created_time"] = download_data_temp[kk + 12]
        current_head["downloader_flag"] = download_data_temp[kk + 13]
        current_head["latest_update_time"] = download_data_temp[kk + 14]
        current_head["batch_id"] = download_data_temp[kk + 15]
        current_head["batch_size"] = download_data_temp[kk + 16]
        current_head["additional_info"] = download_data_temp[kk + 17]
        download_data_list.append(current_head)
    
    return download_data_list

def compare_download_detail_data(body_json, download_data_json, body_len, code=200):
    '''
    @summary: compare the detail data in body and download_tasks_status table
    @param body_json: the each json data in POST updates body list
    @param download_data_json: the json data format about download_tasks_status table
    @return: return the compared result, True of False, and detail data message
    '''
    compare_res = True
    download_res = {
        "id": None,
        "code": None,
        "mesg":None,
        "device_path":None,
        "md5sum":None,
        "size":None,
        "url":None,
        "time_download":None,
        "time_install":None,
        "cmd_install":None,
        "status":None,
        "left_try_times":None,
        "created_time":None,
        "downloader_flag":None,
        "latest_update_time":None,
        "batch_id":None,
        "batch_size":None,
        "additional_info":None 
    }
    print body_json.keys()
    for kk in body_json.keys():
        if str(body_json[kk]) != str(download_data_json[kk]):
            download_res[kk] = (False, body_json[kk], download_data_json[kk])
        else:
            download_res[kk] = (True, body_json[kk], download_data_json[kk])
            
    # compare other parameters in table
#     download_res["code"] = (str(download_data_json["code"]) == str(code), download_data_json["code"])
    download_res["mesg"] = True if str(download_data_json["mesg"]) else False, download_data_json["mesg"]
    download_res["time_download"] = True if int(download_data_json["time_download"]) or download_data_json["time_download"] == str("0") else False, download_data_json["time_download"]
    download_res["time_install"] = True if int(download_data_json["time_install"]) or download_data_json["time_install"] == str("0") else False, download_data_json["time_install"]
    download_res["left_try_times"] = True if int(download_data_json["left_try_times"]) else False, download_data_json["left_try_times"]
    download_res["created_time"] = True if int(download_data_json["created_time"]) else False, download_data_json["created_time"]
    
    if str(download_data_json["status"]) != str(0) and str(download_data_json["status"]) != str(1):
        download_res["downloader_flag"] = (download_data_json["created_time"] == download_data_json["downloader_flag"], download_data_json["downloader_flag"])
    else:
        download_res["downloader_flag"] = (str(download_data_json["downloader_flag"]) == str(0), download_data_json["downloader_flag"])
        
    download_res["latest_update_time"] = True if time.mktime(time.strptime(download_data_json["latest_update_time"],"%Y-%m-%d %H:%M:%S")) else False, download_data_json["latest_update_time"]
    download_res["batch_size"] = int(download_data_json["batch_size"]) == body_len, download_data_json["batch_size"]
    if code == str(200):
        download_res["status"] = True if download_data_json["status"] == str(4) or download_data_json["status"] == str(5) else False, download_data_json["status"]
        download_res["code"] = (str(download_data_json["code"]) == str(code), download_data_json["code"])
    elif code == str(405):
        download_res["status"] = True if download_data_json["status"] == str(3) or download_data_json["status"] == str(5) else False, download_data_json["status"]
        download_res["code"] = (str(download_data_json["code"]) == str(code) or str(download_data_json["code"]) == str(200), download_data_json["code"])
    elif code == str(503):
        download_res["status"] = True if download_data_json["status"] == str(2) else False, download_data_json["status"]
    elif code == str(500):
        download_res["status"] = True if download_data_json["status"] == str(1) else False, download_data_json["status"]

    download_res["additional_info"] = True if download_data_json["additional_info"] == "" else False, download_data_json["additional_info"]
    
    # check the result after compare
    for key, value in download_res.items():
        if download_res[key][0] != True or download_res[key] == None:
            compare_res = False
    return compare_res, download_res

def compare_body_tasks_status(body, download_data_str, code):
    '''
    @summary: compare the content in updates body and content in download_tasks_status table
    @param body: updates body when call POST updates API
    @param download_data_str: the data in download_tasks_status table
    @return: return the compared result and compared data
    '''
    compare_result_flag = True
    compare_result_list = []
    
    download_data_list = reconstruct_download_data(download_data_str)
    print "download data in download_tasks_table"
    print download_data_list
    for kk in range(0, len(body)):
        body_json = json.loads(body[kk])
        body_id = body_json["id"]
        for ii in range(0, len(download_data_list)):
            download_id = download_data_list[ii]["id"]
            if body_id == int(download_id):
                com_res, data_res = compare_download_detail_data(body_json, download_data_list[ii], len(body), code)
                compare_result_list.append((com_res, data_res))
    print compare_result_flag, compare_result_list
    if len(compare_result_list) == 0:
        compare_result_flag = False
    else:
        for ii in range(0, len(compare_result_list)):
            if compare_result_list[ii][0] == False:
                compare_result_flag = False
    print compare_result_flag, compare_result_list
    return compare_result_flag, compare_result_list

if __name__ == '__main__':
    pass

