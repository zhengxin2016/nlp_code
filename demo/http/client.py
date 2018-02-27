#!/usr/bin/env python3
import os,sys
import traceback
import requests
import json

class WebHelper():
    def __init__(self):
        self.url = "http://127.0.0.1:5000/"

    def get_send(self):
        url = self.url+'download'
        r = requests.get(url)
        with open('r.svg', 'wb') as f:
            f.write(r.content)

    def post_send(self):
        url = self.url+"upload"
        #files = {'file1':('r.svg', open('./r.svg', 'rb'))}
        files = {'r.svg':open('./r.svg', 'rb').read()}
        r = requests.post(url, data=None, files=files)
        print(r.text)

if __name__ == '__main__':
    w = WebHelper()
    #result = w.get_send()
    result = w.post_send()
