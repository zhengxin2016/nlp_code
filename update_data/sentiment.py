#!/usr/bin/env python3

import os
import sys
import random
import xlrd
from pymongo import MongoClient

from fun import clean_str, split_pro, Emotion
from solr import SOLR
from utils import BaseClass

class Sentiment(BaseClass):
    def __init__(self, ip, port, db_name='common', collection_name='sentiment'):
        super().__init__(ip, port, db_name, collection_name)

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
                    self.data.append(data)

    def load_data(self):
        sentiment_path = os.path.join(self.dirpath, 'sentiment')
        for f in os.listdir(sentiment_path):
            self.read_data(os.path.join(sentiment_path, f))

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
