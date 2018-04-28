#!/usr/bin/python2.7
#encoding=utf-8
import json
import types

def ParseJson(json_str):
    try:
        return json.loads(json_str)
    except Exception as e:
        print("ParseJson has Exception:",str(e))
        return {}

def getValue(json1,expect_key):
    if type(json1) != dict:
        json1= ParseJson(json1)
    if json1.has_key(expect_key):
        code = 0#0:"have key"
        value = json1[expect_key]
    else:
        code = -1#-1:"key miss"
        value = "None"
    return code,value


def getListValues(listjson,expect_key):
    result_list = []
    num = 0
    if type(listjson) != list:
        listjson = ParseJson(listjson)
    for i in range(0,len(listjson)):
        if type(listjson[i]) != dict:
            listjson[i]= ParseJson(listjson[i]) 
        if listjson[i].has_key(expect_key):
            num  = num+1
            result_list.append(listjson[i][expect_key])
        else:
            result_list.append("None") 
    if num == 0:
        code = -1#-1:"key miss"
    else:
        code = 0 #0:"have key"
    return code,result_list


def getListValue(listjson,filterKey,filterValue,targetKey):
    targetValue = []
    num1 = 0
    num2 = 0
    code = -1
    if type(listjson) != list:
        listjson = ParseJson(listjson)
    for i in range(0,len(listjson)):
        if type(listjson[i]) != dict:
            listjson[i]= ParseJson(listjson[i])
        if listjson[i].has_key(filterKey) and listjson[i].has_key(targetKey):
            num1 = num1 + 1
            if listjson[i][filterKey] == filterValue:
                targetValue = listjson[i][targetKey]
                num2 = num2 + 1            
    if num1 == 0:
        targetValue ="key miss"
    elif num2 > 1:
        targetValue ="more than 1 filterKey-value"
    elif num2 == 0:
        targetValue ="no filterKey-value"
    else:
        code = 0
    return code,targetValue
  
def formattedDepends(str_ldd):
    list_ldd = []
    try:
        str_ldd = str_ldd.strip()
        list_temp = str_ldd.split("\n\t")
    #     print list_temp
        for str_temp in list_temp:
            if str_temp.startswith("/") == False:
    #             print 'startswith:' + str_temp
                ldd = str_temp.split("=>")
                temp = ldd[0].strip()
                list_ldd.append(temp)
            elif str_temp.startswith("/") == True:
                ldd = str_temp.split(" ")
                temp = ldd[0].strip()
                lib_name = temp.split("/")
                list_ldd.append(lib_name[-1].strip())
    except Exception as e:
        print("split ldd Exception:",str(e))
    return list_ldd
  
  
def compareDepends(list_1, list_2):
    list_res = []
    list_ldd = []
    result = 0
    for res in list_1:
        if type(res) == types.StringType:
            list_res.append(res.strip())
        else:
            list_res.append(res)
    for ldd in list_2:
        if type(ldd) == types.StringType:
            list_ldd.append(ldd.strip())
        else:
            list_ldd.append(ldd)
    if len(list_res) == len(list_ldd):
        if len(list(set(list_res).union(set(list_ldd)))) == len(list_ldd) and len(list(set(list_res).difference(set(list_ldd)))) == 0:
            return result
        else:
            result = -1
    else:
        result = -1
    return result

def getVolInfo(output):
    rs_list = []
    for line in output.split('\n'):
        col = line.split(' ')
        try:
            rs_dict = {"vol_device":col[0],"vol_mount":col[1], "vol_size":col[2]}
            rs_list.append(rs_dict)
        except IndexError:
            pass

    return rs_list

# if __name__ == "__main__":
#     print (getListValue([{"name":"jinxin","age":"24","gender":"female"},{"name":"kim","age":"25","gender":"male"},{"name":"kimi","age":"265","gender":"male"}],"name","kim","age"))
