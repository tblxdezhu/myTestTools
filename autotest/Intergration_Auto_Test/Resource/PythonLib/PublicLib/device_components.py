import socket
import datetime
import sys, getopt, os
import paramiko
import sqlite3
import hashlib
from exceptions import AssertionError
import time

is_debug = 0

# ==== log ====
def log_base(type, msg):
    log_info = u'%(time)s UTC [%(type)s][%(pid)d] %(msg)s \n' % { 'time' : datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'), 'type' : type, 'pid' : os.getpid(), 'msg' : msg }
    print log_info

def log_d(msg):
    if is_debug == 1:
        log_base('D', msg)

def log_i(msg):
    log_base('I', msg)

def log_e(msg):
    log_base('E', msg)


'''
receive the gps
'''

def udp_receiver(host,port):
    try:
        port = int(port)
        socket.setdefaulttimeout(5)
        s = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        s.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        s.bind((host,port))
        data,addr = s.recvfrom(1024) 
        rm_gps_date = data.replace("GPS:","")
        data_list = rm_gps_date.split(",")
        s.close()
        return data_list

    except Exception, e:
        print 'UDP receiver error: %s' % e

def udp_sender(timestamp,host,port):
    try:
       port = int(port)
       s = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
       s.sendto(timestamp, (host,port))
       s.close()
    except Exception, e:
        print 'UDP sender error: %s' % e

def udp_bc_sender(gps,host,port,interval,count):
    try:
        HOST = '<broadcast>'
        PORT = 6001
        ADDR = (HOST, PORT)
        gps = str(gps)
        i = 1
        count = int(count)
        interval = int(interval)
        udpCliSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        udpCliSock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        print 'send begin'
        while i < count:   
              i += 1
              udpCliSock.sendto(gps,ADDR)
              time.sleep(interval)
        print 'send end'
    except Exception, e:
        print 'udp_bc_sender error: %s' % e


# download file from remote to local
def download_file(ip,remote_path,local_path,username,password):  
    try:
        t = paramiko.Transport((ip,22))  
        t.connect(username=username, password=password)  # login  
        sftp = paramiko.SFTPClient.from_transport(t)     # sftp transfer
        src = remote_path   
        des = local_path  
        sftp.get(src,des) #download file from des to src
        print("download file PASS!!!")
    except Exception,e:
        print "download file FAIL:", e
        t.close()
    finally:
        t.close()
