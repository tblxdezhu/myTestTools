#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 05/02/2018 5:27 PM
# @Author  : Zhenxuan Xu
# @Site    : 
# @File    : querry.py
# @Software: PyCharm
import os
import sys
import commands


def execute_cmd(cmd, mode):
    """

    :param cmd:
    :param mode:
    :return:
    """
    if mode == "OFF":
        status, output = commands.getstatusoutput(cmd)
        if status == 0:
            print "execute succeed"
        else:
            print output
        return output
    else:
        print "%s", cmd


def query(self, gpgga_path, debug_switch):
    """

    :return:
    """
    print "START QUERY:"
    query_cmd_list = [self.exec_path[2], gpgga_path,
                      os.path.join(self.server_path, "section_out")]
    query_cmd = ' '.join(query_cmd_list)
    print "%s", query_cmd
    execute_cmd(query_cmd, debug_switch)
    query_out_path = os.path.join(self.server_path, "query_out")
    if os.path.exists(query_out_path):
        os.system("rm -rf " + query_out_path + "/*")
    else:
        os.mkdir(query_out_path)
    for file in os.listdir("./section"):
        with open(os.path.join("./section", file), 'r') as f:
            query_out_rtv_path = os.path.join(query_out_path, file.strip(".gps"))
            os.mkdir(query_out_rtv_path)
            dbs = f.readlines()
            for db in dbs:
                db = db.strip("\n") + ".bin"
                try:
                    cmd_cp_db = "cp " + os.path.join(self.db_path, db) + " " + query_out_rtv_path
                    print "%s", cmd_cp_db
                    execute_cmd(cmd_cp_db, debug_switch)
                except Exception:
                    pass


if __name__ == '__main__':
    query_result_path = sys.argv[1]
    need_query_dbs_path = sys.argv[2]
    query_out_path = sys.argv[3]

    for file in os.listdir(query_result_path):
        file_path = os.path.join(query_result_path, file)
        with open(file_path, 'r') as f:
            print file_path
            # rtv = "2017-10" + file.split("gps")[1].rstrip(".")
            rtv = file.replace("gps","rtv")
            print rtv
            out = os.path.join(query_out_path, rtv)
            cmd = "mkdir " + out
            print cmd
            # os.system(cmd)
            dbs = f.readlines()
            for db in dbs:
                print db.strip("\n")
                db_path = os.path.join(need_query_dbs_path, db.strip("\n"))
                cmd_db = "cp " + db_path + ".bin " + out
                print cmd_db
                # os.system(cmd_db)

    pass
