#!/usr/bin/env python3

import os
import sys
import shutil
import random
import xlrd
from pymongo import MongoClient

from fun import clean_str, split_pro, Emotion, questions_pro
import sys
from solr import SOLR
from utils import BaseClass

class Sale(BaseClass):
    def __init__(self, ip, port, db_name, collection_name='sale'):
        super().__init__(ip, port, db_name, collection_name)

    def read_data(self, filepath):
        #0分组 1问题标签 2回答 3等价描述 4类别 5表情 6图片 7产品介绍 8超时时间
        book = xlrd.open_workbook(filepath)
        for sheet in book.sheets():
            for i in range(1, sheet.nrows):
                row = sheet.row(i)
                if row[1].value != '' and row[2].value != '':
                    d = [clean_str(x.value) for x in row]
                    if d[5] == '':
                        d[5] = 'null'
                    if d[6] == '':
                        d[6] = 'null'
                    if len(d) > 8:
                        if d[8] == '':
                            timeout = 'null'
                        else:
                            timeout = d[8]
                    else:
                        timeout = 'null'
                    data = {}
                    data['group'] = d[0]
                    data['label'] = d[1]
                    data['answers'] = split_pro(d[2], '/')
                    data['equal_questions'] = list(set(split_pro(d[1], '/') + \
                            split_pro(d[3], '/')))
                    data['equal_questions'] = \
                            list(set(questions_pro(data['equal_questions'])))
                    data['type'] = d[4]
                    data['emotion_name'] = d[5]
                    data['emotion_url'] = Emotion[d[5]]
                    data['media'] = d[6]
                    data['description'] = d[7]
                    data['timeout'] = timeout
                    self.data.append(data)

    def load_data(self):
        sale_path = os.path.join(self.dirpath, 'sale')
        for f in os.listdir(sale_path):
            self.read_data(os.path.join(sale_path, f))

    def update(self):
        #print('load data')
        #self.load_data()
        #print('write mongodb')
        #self.write_data2mongodb()
        print('write solr')
        self.write_data2solr()

if __name__ == '__main__':
    ip = '127.0.0.1'
    port = 27017
    Mode = ['bank', 'bank_ccb', 'bank_psbc', 'suning_biu', 'water', 'ecovacs']
    if len(sys.argv) != 2:
        print('!!!The number of args is wrong!!!')
        assert(0)
    if sys.argv[1] not in Mode:
        print('!!!error arg:', sys.argv[1])
        assert(0)
    mode = sys.argv[1]
    s = Sale(ip, port, mode, 'sale')
    print('--------sale starting--------')
    s.update()
    print('--------sale ok-----------')

