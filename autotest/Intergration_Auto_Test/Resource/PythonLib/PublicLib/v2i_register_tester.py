#!/usr/bin/env python
import os
import json
import threading
import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish
import ssl

global response
response=""
global run
global client
RESOURCE = "/events"
METHOD = "POST"

class V2I(object):
    def __init__(self, IP, port, ssl_files, topic_pub, topic_sub, encoding_type, message_id, reply_to, device_id, body, noti_time):
        self._IP = IP
        self._port = int(port)
        self._ssl_files=[]
        for _file in ssl_files:
            new_file = _file.replace("~", os.path.expanduser("~"))
            self._ssl_files.append(new_file)
        self._topic_pub = topic_pub
        self._topic_sub = topic_sub
        self._encoding_type = int(encoding_type)
        self._message_id = str(message_id)
        self._resource = RESOURCE
        self._method = METHOD
        self._reply_to = str(reply_to)
        self._device_id = str(device_id)
        if type(body) == dict:
            self._body = body
        elif type(body) == str or type(body) == unicode:
            try:
                self._body = json.loads(str(body))
            except ValueError:
                self._body = str(body)
        else:
            self._body = body
        self._noti_time = int(noti_time)
        self._send_msg = None
        self._msg_list = []
        
    @staticmethod
    def __stop_loop():
        global client
        client.disconnect()
#         global run
#         run = False

    def __para_json(self):
        for kk in range(0, len(self._msg_list)):
            response_msg = json.loads(self._msg_list[kk])
            _msg_id = response_msg["message_id"]
            _resource = response_msg["payload"]["resource"]
            _method = response_msg["payload"]["method"]
            if self._message_id == _msg_id and self._resource == _resource and self._method == _method:
                del self._msg_list[:]
                json.dumps(response_msg, indent=2)
            # if self._message_id != _msg_id or self._resource != _resource or self._method != _method:
            #     print("response message {} error: message_id or resource or method not the same as request".format(kk+1))
            # else:
            #     del self._msg_list[:]
            #     print("response message {} is OK.".format(kk+1))
            #     # return response_msg
            #     return json.dumps(response_msg, indent=2)

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
        _send_msg = {"reply_to": "", "message_id": "", "device_id": "","payload": {"method": "", "resource": ""}}
        _send_msg["message_id"] = self._message_id
        _send_msg["reply_to"] = self._reply_to
        _send_msg["device_id"] = self._device_id
        _send_msg["payload"]["resource"] = self._resource
        _send_msg["payload"]["method"] = self._method
        if self._body != "None":
            if type(self._body) != dict:
                print("combine the message")
                payload = str(json.dumps(_send_msg["payload"])).strip("}") + "," + '"body"' + ":" + str(self._body) + "}"
                msg_id = '"message_id": "{msg_id}"'.format(msg_id=self._message_id)
                self._send_msg = '{"reply_to": "", "device_id": "",' + msg_id + "," + '"payload": ' + payload
#                 msg = self._send_msg.replace('"', '\\"')
                msg = chr(self._encoding_type) + self._send_msg
                return msg
            else:
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
        response = ""
        
        print(msg.topic+" "+str(msg.payload))
        response_str = str(msg.payload)
        
        response = self.__para_data(response_str)
        # print "response_str:     " + response_str
        # print "response:     " + response
        if response != None:
            self.__stop_loop()
#             client.disconnect()
        
    def __send_request(self):
        print self.__encode_msg()
        tls = {'ca_certs': self._ssl_files[0], 'certfile': self._ssl_files[1], 'keyfile': self._ssl_files[2],'tls_version': ssl.PROTOCOL_TLSv1,'ciphers':None}
        publish.single(self._topic_pub, self.__encode_msg(), 1, False, self._IP, self._port, None, 60, None, None, tls, None, None)
    
    def v2i_command(self):
        global response
        global client
        response = ""

        client = mqtt.Client()
        client.on_connect = self.__on_connect
        client.on_message = self.__on_message
        
        client.tls_set(ca_certs=self._ssl_files[0], certfile=self._ssl_files[1], keyfile=self._ssl_files[2])
        print self._IP
        print self._port
        timer = threading.Timer(self._noti_time, self.__stop_loop)
        timer.start()
        client.connect(self._IP, self._port)
        client.loop_forever(self._noti_time)
#         run = True
#         while run:
#             client.loop()
#         timer.cancel()
#         client.disconnect()
        # print "################################response############################################\n:   " + response
        return response
        
def v2i_register_tester(IP, port, ssl_files, topic_pub, topic_sub, encoding_type, message_id,reply_to, device_id, body, noti_time=5):
    v2i = V2I(IP, port, ssl_files, topic_pub, topic_sub, encoding_type, message_id, reply_to, device_id, body, noti_time)
    return v2i.v2i_command()

# if __name__ == "__main__":
#     username = "asample"
#     password = "test1234"
#     IP = "asample-mqtt-dev-01.roaddb.ygomi.com"
#     port = "8883"
#     # IP = "127.0.0.1"
#     # port = "1883"
#     ca_file = "~/SSL_files/ca.crt"
#     cert_file = "~/SSL_files/roaddb_device.crt"
#     key_file = "~/SSL_files/roaddb_device.pem"
#     ssl_files = [ca_file, cert_file, key_file]
#     topic_pub = "2696457ac9f87581841781b656f3e0e4" # "pref/device_queue"
#     topic_sub = "pref/server_queue" # "pref/server_queue"
#     encoding_type = 1
#     message_id = "1234"
#     resource = "/components"
#     method = "GET"
#     body = "None"
#     # send_msg = '{"dev_id": "", "message_id": "3333", "payload": {"method": "GET", "resource": "/settings"},"repy_to" : ""}'
#     sub_msg = v2i_register_tester(IP, port, ssl_files, topic_pub, topic_sub, encoding_type, message_id, resource, method, body)
#     # print("the get data is : ")
#     print(sub_msg)



