#!/usr/bin/python2.7
#encoding=utf-8

import json

def ParseJson(json_str):
    try:
        return json.loads(json_str)
    except Exception as e:
        print("ParseJson has Exception:",str(e))
        return {}

# def Comparevalue(json1,expect_key,expect_value):
#   if type(json1) != dict:
#     json_dict = ParseJson(json1)
#   else:
#     json_dict = json1
#     result_list = []
#   if json_dict.has_key(expect_key):
#     result_list.append(1)#1:"have key"
#     if type(expect_value) == type(json_dict[expect_key]):
#         result_list.append(1)#1:"type equal"
#         if expect_value == json_dict[expect_key]:
#             result_list.append(1)#1:"value equal"
#             msg = 'equal'
#         else:
#             result_list.append(0)#0:"value dismatch"
#             msg = "value dismatch"

#     else:
#             result_list.append(0)#0:"type dismatch"
#             result_list.append(0)
#             msg = "type dismatch"
#   else:
#       result_list.append(0)#0:"key miss"
#       result_list.append(0)
#       result_list.append(0)
#       msg = "key miss"
  
#   return result_list,msg,type(expect_value) 

def Comparevalue(json1,expect_key,expect_value):
  if type(json1) != dict:
    json_dict = ParseJson(json1)
  else:
    json_dict = json1
    result_list = []
  if json_dict.has_key(expect_key):
    result_list.append(1)#1:"have key"
    if expect_value == json_dict[expect_key]:
        result_list.append(1)#1:"value equal"
        msg = 'equal'
    else:
            result_list.append(0)#0:"value dismatch"
            msg = "value dismatch"
  else:
      result_list.append(0)#0:"key miss"
      result_list.append(0)
      msg = "key miss"
  
  return result_list,msg

