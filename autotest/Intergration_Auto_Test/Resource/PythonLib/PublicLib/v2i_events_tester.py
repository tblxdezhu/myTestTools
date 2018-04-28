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
    def __init__(self, IP, port, ssl_files, topic_sub, event_type, device_id, noti_time, num, code):
        self._IP = IP
        self._port = int(port)
        self._ssl_files=[]
        for _file in ssl_files:
            new_file = _file.replace("~", os.path.expanduser("~"))
            self._ssl_files.append(new_file)
        self._topic_sub = topic_sub
        self._event_type = int(event_type)
        self._device_id = device_id
        self._noti_time = int(noti_time)
        self._num = int(num)
        self._msg_list = []
        self._code = int(code)

    @staticmethod
    def __stop_loop():
        global run
        run = False
         
    def __para_json(self):
        response_msg_lsit = []
        for kk in range(0, len(self._msg_list)):
            response_msg = json.loads(self._msg_list[kk])
            _device_id = response_msg["device_id"]
            _resource = response_msg["payload"]["resource"]
            if "/events" == _resource:
                _event_type = response_msg["payload"]["event_type"]
                if self._device_id == _device_id and "/events" == _resource and self._event_type == _event_type:
                    if self._event_type == 3:
                        if response_msg["payload"]["body"]["error_code"] == self._code:
                            response_msg_lsit.append(json.dumps(response_msg, indent=2))
                    else:
                        response_msg_lsit.append(json.dumps(response_msg, indent=2))
        del self._msg_list[:]
        if len(response_msg_lsit) == 0 or self._num == 2:
            return response_msg_lsit
        elif self._num == 0:
            return response_msg_lsit[0]
        elif self._num == 1:
            return response_msg_lsit[-1]

    def __split_chr(self, msg, start=0):
        var = [chr(1), chr(2), chr(3)]
        new = msg.split(var[start])
        for kk in range(0, len(new)):
            if new[kk]:
                if (start + 1) <= len(var) - 1:
                    self.__split_chr(new[kk],start+1)
                else:
                    self._msg_list.append(new[kk].strip("\n"))
                    print "self._msg_list without n:    " + str(self._msg_list)

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

    # The callback for when the client receives a CONNACK response from the server.
    def __on_connect(self, client, userdata, flags, rc):
        print("Connected with result code "+str(rc))
    
        # Subscribing in on_connect() means that if we lose the connection and
        # reconnect then subscriptions will be renewed.
        client.subscribe("pref/server_queue")
#         self.__send_request()
    
    def __on_message(self, client, userdata, msg):
        global response
        global run
        
        # print(msg.topic+" "+str(msg.payload))
        response_str = str(msg.payload)
        response = response + response_str
        # print "response_str:     " + response_str
#         print "response:     " + response
#         if self._num == 0:
#             response = self.__para_data(response_str)
#             if response != None:
#                 timer.cancel()
#         elif self._num == 1 or self._num == 2:
#             response_list.append(response_str)
#         if self._num == 0:
#             response_list = self.__para_data(response_str)
#             if response_list != None:
#                 timer.cancel()
#         if self._num == 1 or self._num == 2:
#             response_list.append(response_str)
        
#     def __send_request(self):
#         print self.__encode_msg()
#         tls = {'ca_certs': self._ssl_files[0], 'certfile': self._ssl_files[1], 'keyfile': self._ssl_files[2],'tls_version': ssl.PROTOCOL_TLSv1,'ciphers':None}
#         publish.single(self._topic_pub, self.__encode_msg(), 0, False, self._IP, self._port, None, 60, None, None, tls, None, None)
    
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
#         client.loop_forever()
        timer = threading.Timer(self._noti_time, self.__stop_loop)
        timer.start()
        run = True
        while run:
            client.loop()
        client.disconnect()
        
        # print "################################response############################################\n:     " + response
        para_data = self.__para_data(response)
        if para_data == None :
            para_data = []
        return para_data
        
    
def v2i_events_tester(IP, port, ssl_files, topic_sub, event_type, device_id, noti_time, num = 1, code = 400):
    v2i = V2I(IP, port, ssl_files, topic_sub, event_type, device_id, noti_time, num, code)
    return v2i.v2i_command()

# if __name__ == "__main__":
#     # username = "asample"
#     # password = "asample"
#     IP = "asample-server-staging-02.roaddb.ygomi.com"
#     port = "8883"
#     # IP = "127.0.0.1"
#     # port = "1883"
#     ca_file = "/home/simon/SSL_files/ca.crt"
#     cert_file = "/home/simon/SSL_files/roaddb_device.crt"
#     key_file = "/home/simon/SSL_files/roaddb_device.pem"
#     ssl_files = [ca_file, cert_file, key_file]
#     topic_sub = "pref/server_queue"
#     event_type = 2
#     device_id = "a96d64446a32038318e3109457a1a29f"
#     noti_time = 10
#     num = 2
#     sub_msg = v2i_events_tester(IP, port, ssl_files, topic_sub, event_type, device_id, noti_time, num, )
#     print("the get data is : ")
#     print(sub_msg)
#     if sub_msg != None:
#         for ii in range(0, len(sub_msg)):
#             print(sub_msg[ii])