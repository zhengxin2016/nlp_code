#!/usr/bin/env python3

import os
import sys
import random
import xlrd
from pymongo import MongoClient

from fun import clean_str, split_pro, Emotion
from solr import SOLR

class Refuse2chat():
    def __init__(self, ip, port, db_name):
        self.dirpath = 'data/' + db_name
        self.db_name = db_name
        self.db = MongoClient(ip, port)[db_name]
        self.refuse2chat = []
        self.solr_url = 'http://'+ ip +':8999/solr'
        self.solr_core = 'zx_' + self.db_name + '_refuse2chat'
        self.solr = SOLR(self.solr_url)

    def read_data(self, filepath):
        #0问题 1回答 2表情 3图片 4超时时间
        book = xlrd.open_workbook(filepath)
        for sheet in book.sheets():
            for i in range(1, sheet.nrows):
                row = sheet.row(i)
                if row[0].value != '' and row[1].value != '':
                    d = [clean_str(x.value) for x in row]
                    if d[2] == '':
                        d[2] = 'null'
                    if d[3] == '':
                        d[3] = 'null'
                    if len(d) > 4:
                        if d[4] == '':
                            timeout = 'null'
                        else:
                            timeout = d[4]
                    else:
                        timeout = 'null'
                    data = {}
                    data['group'] = '转折句'
                    data['label'] = '拒绝闲聊'
                    data['equal_questions'] = ['null']
                    data['answers'] = split_pro(d[1], '/')
                    data['emotion_name'] = d[2]
                    data['emotion_url'] = Emotion[d[2]]
                    data['media'] = d[3]
                    data['timeout'] = timeout
                    self.refuse2chat.append(data)

    def load_data(self):
        refuse2chat_path = os.path.join(self.dirpath, 'refuse2chat')
        for f in os.listdir(refuse2chat_path):
            self.read_data(os.path.join(refuse2chat_path, f))

    def write_data2mongodb(self):
        self.db['refuse2chat'].drop()
        self.db['refuse2chat'].insert(self.refuse2chat)
        self.db['refuse2chat'].create_index('question')

    def write_data2solr(self):
        self.solr.delete_solr_core(self.solr_core)
        self.solr.create_solr_core(self.solr_core)
        for x in self.db['refuse2chat'].find():
            x['_id'] = str(x['_id'])
            self.solr.update_solr(x, self.solr_core)

    def update(self):
        print('load data')
        self.load_data()
        print('write mongodb')
        self.write_data2mongodb()
        print('write solr')
        self.write_data2solr()

if __name__ == '__main__':
    ip = '127.0.0.1'
    port = 27017
    Mode = ['bank', 'bank_ccb', 'bank_psbc', 'suning_biu', 'water', 'ecovacs', 'ule']
    if len(sys.argv) != 2:
        print('!!!The number of args is wrong!!!')
        assert(0)
    if sys.argv[1] not in Mode:
        print('!!!error arg:', sys.argv[1])
        assert(0)
    mode = sys.argv[1]
    r = Refuse2chat(ip, port, mode)
    print('--------refuse2chat starting-------')
    r.update()
    print('--------refuse2chat ok-----------')
