#!/usr/bin/env python3

import os,sys
import requests
import json

class WebHelper():
    def __init__(self):
        self.url = "http://127.0.0.1:1234/"

    def get_send(self):
        url = self.url+'count_data/suning_biu/qa/{}'
        r = requests.get(url)
        print(r.text)

    def post_send(self):
        url = self.url+"commit/suning_biu/dialogue"
        postdata = {'result':[{'cmd':'create', '_id':'0', 'group':'g1', 'label':'_你好', 'equal_questions':['你好']}]}
        postdata = json.dumps(postdata)
        r = requests.post(url, data=postdata)
        print(r.text)

    def send(self):
        s = '怎么登录注册认证刷脸'*729
        url = self.url+quote(s)
        response = request.urlopen(url).read()
        if response == b'':
            print('result:null')
        else:
            result = json.loads(response.decode('utf8'))
            print(result)
    
if __name__ == '__main__':
    w = WebHelper()
    result = w.get_send()
    result = w.post_send()
    
