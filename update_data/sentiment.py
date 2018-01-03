#!/usr/bin/env python3

import os
import sys
import random
import xlrd
from pymongo import MongoClient

from fun import clean_str, split_pro, Emotion
from solr import SOLR

class Sentiment():
    def __init__(self, ip, port):
        self.dirpath = 'data/common'
        self.db_name = 'common'
        self.db = MongoClient(ip, port)[self.db_name]
        self.sentiment = []
        self.solr_url = 'http://'+ ip +':8999/solr'
        self.solr_core = 'zx_' + self.db_name + '_sentiment'
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
                    data['group'] = '情感'
                    data['label'] = d[0]
                    data['equal_questions'] = ['null']
                    data['answers'] = split_pro(d[1], '/')
                    data['emotion_name'] = d[2]
                    data['emotion_url'] = Emotion[d[2]]
                    data['media'] = d[3]
                    data['timeout'] = timeout
                    self.sentiment.append(data)

    def load_data(self):
        sentiment_path = os.path.join(self.dirpath, 'sentiment')
        for f in os.listdir(sentiment_path):
            self.read_data(os.path.join(sentiment_path, f))

    def write_data2mongodb(self):
        self.db['sentiment'].drop()
        self.db['sentiment'].insert(self.sentiment)
        self.db['sentiment'].create_index('question')

    def write_data2solr(self):
        self.solr.delete_solr_core(self.solr_core)
        self.solr.create_solr_core(self.solr_core)
        for x in self.db['sentiment'].find():
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
    sen = Sentiment(ip, port)
    print('--------sentiment starting-------')
    sen.update()
    print('--------sentiment ok-----------')
