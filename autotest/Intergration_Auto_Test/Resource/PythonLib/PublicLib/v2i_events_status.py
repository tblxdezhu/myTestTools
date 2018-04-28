#!/usr/bin/env python
import os
import subprocess
import json
import threading
import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish
import ssl

global response
response = ""
global run
global timer

class V2I(object):
    def __init__(self, IP, port, ssl_files, topic_pub, topic_sub, encoding_type, msgid_res_method_body, type_devid_time_num):
        self._IP = IP
        self._port = int(port)
        self._ssl_files=[]
        for _file in ssl_files:
            new_file = _file.replace("~", os.path.expanduser("~"))
            self._ssl_files.append(new_file)
        self._topic_pub = topic_pub
        self._topic_sub = topic_sub
        self._encoding_type = int(encoding_type)
        self._message_id = str(msgid_res_method_body[0])
        self._resource = str(msgid_res_method_body[1])
        self._body_resource_type = self._resource.split("/")[1]
        self._method = str(msgid_res_method_body[2])
        body = msgid_res_method_body[3]
        if type(body) == dict:
            self._body = body
        elif type(body) == str or type(body) == unicode:
            try:
                self._body = json.loads(str(body))
            except ValueError:
                self._body = body
        else:
            self._body = body

        # get the keys in the input body
        if dict == type(self._body):
            self._keys_in_body = self._body.keys()
        else:
            self._keys_in_body = None

        self._event_type = int(type_devid_time_num[0])
        self._device_id = type_devid_time_num[1]
        self._noti_time = int(type_devid_time_num[2])
        self._num = int(type_devid_time_num[3])

        self._send_msg = None
        self._msg_list = []

    @staticmethod
    def __stop_loop():
        global run
        run = False
        
    def __para_json(self):
        event_list = []
        msg = None
        for kk in range(0, len(self._msg_list)):
            response_msg = json.loads(self._msg_list[kk])
            _resource = response_msg["payload"]["resource"]
            if "/events" == _resource:
                _device_id = response_msg["device_id"]
                _resource = response_msg["payload"]["resource"]
                _event_type = response_msg["payload"]["event_type"]
                if 5 == _event_type:
                    _body_resource = response_msg["payload"]["body"]["resource"]
                    if self._device_id == _device_id and "/events" == _resource and self._event_type == _event_type \
                            and _body_resource.find(self._body_resource_type) > 0\
                            and _body_resource.split("/")[-1] in self._keys_in_body:
                        event_list.append(json.dumps(response_msg, indent=2))
                else:
                    if self._device_id == _device_id and "/events" == _resource and self._event_type == _event_type:
                        event_list.append(json.dumps(response_msg, indent=2))
            else:
                _msg_id = response_msg["message_id"]
                _method = response_msg["payload"]["method"]
                if self._message_id == _msg_id and self._resource == _resource and self._method == _method:
                    msg = json.dumps(response_msg, indent=2)
                # if self._message_id != _msg_id or self._resource != _resource or self._method != _method:
                #     print("response message {} error: message_id or resource or method not the same as request".format(kk+1))
                # else:
                #     print("response message {} is OK.".format(kk+1))
                #     msg = json.dumps(response_msg, indent=2)
        del self._msg_list[:]
        if len(event_list) == 0 or self._num == 2:
            return msg, event_list
        elif self._num == 0:
            return msg, event_list[0]
        elif self._num == 1:
            return msg, event_list[-1]


    def __split_chr(self, msg, start=0):
        var = [chr(1), chr(2), chr(3)]
        new = msg.split(var[start])
        for kk in range(0, len(new)):
            if new[kk]:
                if (start + 1) <= len(var) - 1:
                    self.__split_chr(new[kk],start+1)
                else:
                    self._msg_list.append(new[kk].strip("\n"))

    def __para_data(self, out_msg):
        global response
        if not out_msg:
            print("response message is None")
            return None
        self.__split_chr(out_msg, start=0)
        response = ""
        if 1 == ord(out_msg[0]) or 2 == ord(out_msg[0]) or 3 == ord(out_msg[0]):
            try:
                return self.__para_json()
            except ValueError:
                print("response message error: can not para response message into json format")
                # exit()
        else:
            return "response message error: message encoding type wrong"

    def __encode_msg(self):
        _send_msg = {"reply_to": "", "message_id": "", "dev_id": "","payload": {"method": "", "resource": ""}}
        _send_msg["message_id"] = self._message_id
        _send_msg["payload"]["resource"] = self._resource
        _send_msg["payload"]["method"] = self._method
        if self._body != "None":
            _send_msg["payload"]["body"] = self._body
        self._send_msg = json.dumps(_send_msg)
#         msg = self._send_msg.replace('"', '\\"')
        msg = chr(self._encoding_type) + self._send_msg
        return msg

    # The callback for when the client receives a CONNACK response from the server.
    def __on_connect(self, client, userdata, flags, rc):
        print("Connected with result code "+str(rc))
    
        # Subscribing in on_connect() means that if we lose the connection and
        # reconnect then subscriptions will be renewed.
        client.subscribe("pref/server_queue")
        self.__send_request()
    
    def __on_message(self, client, userdata, msg):
        global response
        
        # print(msg.topic+" "+str(msg.payload))
        response_str = str(msg.payload)
        response = response + response_str
        # print "response_str:     " + response_str
#         print "response:     " + response
        
    def __send_request(self):
        print self.__encode_msg()
        tls = {'ca_certs': self._ssl_files[0], 'certfile': self._ssl_files[1], 'keyfile': self._ssl_files[2],'tls_version': ssl.PROTOCOL_TLSv1,'ciphers':None}
        publish.single(self._topic_pub, self.__encode_msg(), 1, False, self._IP, self._port, None, 60, None, None, tls, None, None)
    
    def v2i_command(self):
        global response
        global run
        global timer
        response = ""
        
        client = mqtt.Client()
        client.on_connect = self.__on_connect
        client.on_message = self.__on_message
        
        client.tls_set(ca_certs=self._ssl_files[0], certfile=self._ssl_files[1], keyfile=self._ssl_files[2])
        print self._IP
        print self._port
        client.connect(self._IP, self._port)
#         client.loop_forever(self._noti_time)
        timer = threading.Timer(self._noti_time, self.__stop_loop)
        timer.start()
        run = True
        while run:
            client.loop()
        client.disconnect()
        #create response list
        # print "################################response############################################\n:     " + response
        return self.__para_data(response)


def v2i_tester_status(IP, port, ssl_files, topic_pub, topic_sub, encoding_type, msgid_res_method_body, type_devid_time_num):
    v2i = V2I(IP, port, ssl_files, topic_pub, topic_sub, encoding_type, msgid_res_method_body, type_devid_time_num)
    return v2i.v2i_command()


# if __name__ == "__main__":
#     username = "asample"
#     password = "asample"
#     IP = "asample-mqtt-dev-01.roaddb.ygomi.com"
#     port = "8883"
#     # IP = "127.0.0.1"
#     # port = "1883"
#     ca_file = "/home/ying-tan/Desktop/Device_V2I/robot/cert/ca.crt"
#     cert_file = "/home/ying-tan/Desktop/Device_V2I/robot/cert/roaddb_device.crt"
#     key_file = "/home/ying-tan/Desktop/Device_V2I/robot/cert/roaddb_device.pem"
#     ssl_files = [ca_file, cert_file, key_file]
#     topic_pub = "pref/server_queue"
#     topic_sub = "pref/device_queue"
#     encoding_type = 1
#     msgid_res_method_body = [20, "/settings", "PUT", {"time_sunset": "20:21", "time_sunrise": "09:26"}]
#     type_devid_time_num = [5, "2696457ac9f87581841781b656f3e0e4", 25, 2]
#     sub_msg = v2i_tester_status(IP, port, ssl_files, topic_pub, topic_sub, encoding_type, msgid_res_method_body, type_devid_time_num)
#     print("the get data is : ")
#     print(sub_msg)
#     for ii in range(0, len(sub_msg)):
#         print(type(sub_msg[ii]))
#         if type(sub_msg[ii]) == list:
#             for kk in range(0, len(sub_msg[ii])):
#                 print(sub_msg[ii][kk])
#                 print("the json type")
#                 print(json.loads(sub_msg[ii][kk]))
#         else:
#             print(sub_msg[ii])
#             print("the json type")
#             print(json.loads(sub_msg[ii]))



