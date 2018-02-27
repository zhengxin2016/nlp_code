#!/usr/bin/env python3
import os,sys
import traceback
import json
import bottle
from flask import Flask

app = Flask(__name__)

@bottle.route('/download')
def download():
    return bottle.static_file('test.svg', '.')

@bottle.route('/upload')
def upload():
    uploadfile = request.files.get('1.svg')
    uploadfile.save('test1.svg', overwrite=True)
    print('ok')
    return 'ok'

if __name__ == '__main__':
    bottle.run(host='0.0.0.0', port=5000)
