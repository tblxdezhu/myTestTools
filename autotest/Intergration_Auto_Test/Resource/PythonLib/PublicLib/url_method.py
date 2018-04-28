#!/usr/bin/env python

import sys
import os
import datetime
import urllib2
import simplejson as json
import string
import pycurl
import StringIO

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

# ==== http utils ====
def http_get(url, header):
    try:
        if header is None:
            log_d('HTTP GET: %s' % url)
            connection = urllib2.urlopen(url)
            content = connection.read()
            return_code = connection.getcode()
            connection.close()
            log_d('HTTP response: %s' % content)
            return return_code, content
        else:
            log_d('HTTP GET: %s with header: %s' % (url, header))
            request = urllib2.Request(url)
            
            headerlists=header.split(';')
            for headerlist in headerlists:
                headerlist=header.split(':')
                key = headerlist[0]
                val = headerlist[1]
                request.add_header(key, val)
            
            connection = urllib2.urlopen(request)
            content = connection.read()
            return_code = connection.getcode()
            connection.close()
            log_d('HTTP response: %s' % content)
            return return_code, content
    except Exception, e:
        log_e('http_get() error: %s' % e)
        return e.code, e.read()

def http_post(url, body, header):
    try:
	if type(body) == list:
            _body = []
            for kk in range(0, len(body)):
                _body.append(json.dumps(json.loads(str(body[kk]))))
            body = _body

        if header is None:
            log_d('HTTP POST: %s, body: %s' % (url, body))
            request = urllib2.Request(url, body)
            connection = urllib2.urlopen(request)
            content = connection.read()
            return_code = connection.getcode()
            connection.close()
            log_d('HTTP response: %s' % content)
            return return_code, content
        else:
            log_d('HTTP POST: %s with header: %s' % (url, header))
            request = urllib2.Request(url, body)

            headerlists=header.split(';')
            for headerlist in headerlists:
                headerlist=header.split(':')
                key = headerlist[0]
                val = headerlist[1]
                request.add_header(key, val)

            connection = urllib2.urlopen(request)
            content = connection.read()
            return_code = connection.getcode()
            connection.close()
            log_d('HTTP response: %s' % content)
            return return_code, content
    except Exception, e:
        log_e('http_get() error: %s' % e)
        return e.code, e.read()

def http_put(url, body, header):
    try:
        if header is None:
            log_d('HTTP PUT: %s, body: %s' % (url, body))
            request = urllib2.Request(url, body)
            request.get_method = lambda: 'PUT'
            connection = urllib2.urlopen(request)
            content = connection.read()
            return_code = connection.getcode()
            connection.close()
            log_d('HTTP response: %s' % content)
            return return_code, content
        else:
            log_d('HTTP PUT: %s with header: %s' % (url, header))
            request = urllib2.Request(url, body)
            request.get_method = lambda: 'PUT'

            headerlists=header.split(';')
            for headerlist in headerlists:
                headerlist=header.split(':')
                key = headerlist[0]
                val = headerlist[1]
                request.add_header(key, val)

            connection = urllib2.urlopen(request)
            content = connection.read()
            return_code = connection.getcode()
            connection.close()
            log_d('HTTP response: %s' % content)
            return return_code, content
    except Exception, e:
        log_e('http_get() error: %s' % e)
        return e.code, e.read()

def http_delete(url, body, header):
    try:
        if header is None:
            log_d('HTTP DELETE: %s' % (url))
            request = urllib2.Request(url, body)
            request.get_method = lambda: 'DELETE'
            connection = urllib2.urlopen(request)
            content = connection.read()
            return_code = connection.getcode()
            connection.close()
            log_d('HTTP response: %s' % content)
            return return_code, content
        else:
            log_d('HTTP DELETE: %s with header: %s' % (url, header))
            request = urllib2.Request(url, body)
            request.get_method = lambda: 'DELETE'

            headerlists=header.split(';')
            for headerlist in headerlists:
                headerlist=header.split(':')
                key = headerlist[0]
                val = headerlist[1]
                request.add_header(key, val)

            connection = urllib2.urlopen(request)
            content = connection.read()
            return_code = connection.getcode()
            connection.close()
            log_d('HTTP response: %s' % content)
            return return_code, content
    except Exception, e:
        log_e('http_get() error: %s' % e)
        return e.code, e.read()

def http_get_json(url, header=None):
    return_code, response = http_get(url, header)

    if None == response:
        return return_code, None

    try:    
        jsonObj = json.loads(response)
        return return_code, jsonObj
    except:
        log_e('Parse json error: ' + response)
        return return_code, response

def http_post_json(url, body, header=None):
    return_code, response = http_post(url, body, header)

    if None == response:
        return return_code, None

    try:    
        jsonObj = json.loads(response)
        return return_code, jsonObj
    except:
        log_e('Parse json error: ' + response)
        return return_code, response

def http_put_json(url, body, header=None):
    return_code, response = http_put(url, body, header)

    if None == response:
        return return_code, None

    try:    
        jsonObj = json.loads(response)
        return return_code, jsonObj
    except:
        log_e('Parse json error: ' + response)
        return return_code, response

def http_delete_json(url, header=None):
    return_code, response = http_delete(url, None, header)

    if None == response:
        return return_code, None

    try:    
        jsonObj = json.loads(response)
        return return_code, jsonObj
    except:
        log_e('Parse json error: ' + response)
        return return_code, response

def curl_get_header(url, header):
    c = pycurl.Curl()
    buf = StringIO.StringIO()
    c.setopt(c.WRITEFUNCTION, buf.write)
    c.setopt(c.URL, url)
    c.setopt(c.HEADER, True)
    if header is not None:
        c.setopt(pycurl.HTTPHEADER,  header)
    c.perform()
    the_page = buf.getvalue()
    buf.close()
    return the_page

# ==== common lib ====
def restful_tester(url, method, header = None, body = None):
    if header == None:
        header = "Content-Type:application/json"	
    if method == 'GET':
        return_code, return_json = http_get_json(url, header)
    elif method == 'POST':
        return_code, return_json = http_post_json(url, body, header)
    elif method == 'PUT':
        return_code, return_json = http_put_json(url, body, header)
    elif method == 'DELETE':
        return_code, return_json = http_delete_json(url, header)
    else:
        return_code = -1
        return_json = json.loads('{"error_msg":"invaild method input"}')

    return return_code, return_json

# if '__main__' == __name__:
#     acode, a = restful_tester("http://10.69.0.204:8081/DevicesManager-bamboo_version/rs/devices/5da70533c103e404ccb6d2a256a88e7/components?cache=true", "GET")
#     acode, a = restful_tester('http://10.69.0.25:8080/devices/device_1234567','GET',None, None)
#     bcode, b = restful_tester('http://10.69.0.25:8080/deferred?device_id=test1&resource=test2&method=test3&parameters=\{"a1":"aa","a2":"bb"\}','POST',None,'{"body":"string"}')
#     ccode, c = restful_tester('http://10.69.0.25:8080/deferred/1?status=deferring&code=200','PUT',None,'{"body":"string"}')
#     dcode, d = restful_tester('http://10.69.0.25:8080/deferred/1?status=deferring&code=200','DELETE',None, None)
#     ecode, e = restful_tester('http://10.69.0.25:8080/deferred/1?status=deferring&code=200','DEL',None, None)
#     print acode, a
#     print bcode, b
#     print ccode, c
#     print dcode, d
#     print ecode, e
