#!/usr/bin/env python3

import os
import sys
import shutil
import random
import xlrd
from pymongo import MongoClient
import json

from fun import clean_str, split_pro, Emotion, questions_pro
from solr import SOLR
from utils import BaseClass

class Interaction(BaseClass):
    def __init__(self, ip, port, db_name, collection_name='interaction'):
        super().__init__(ip, port, db_name, collection_name)

    def read_data(self, filepath):
        #0分组 1问题标签 2回答 3等价描述 4表情 5图片 6超时时间
        book = xlrd.open_workbook(filepath)
        for sheet in book.sheets():
            for i in range(1, sheet.nrows):
                row = sheet.row(i)
                if row[1].value != '' and row[2].value != '':
                    d = [clean_str(x.value) for x in sheet.row(i)]
                    if d[4] == '':
                        d[4] = 'null'
                    if d[5] == '':
                        d[5] = 'null'
                    if len(d) > 6:
                        if d[6] == '':
                            timeout = 'null'
                        else:
                            timeout = d[6]
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
                    data['emotion_name'] = d[4]
                    data['emotion_url'] = Emotion[d[4]]
                    data['media'] = d[5]
                    data['timeout'] = timeout
                    self.data.append(data)

    def load_data(self):
        interaction_path = os.path.join(self.dirpath, 'interaction')
        for f in os.listdir(interaction_path):
            self.read_data(os.path.join(interaction_path, f))

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
    interaction = Interaction(ip, port, mode, 'interaction')
    print('--------interaction starting--------')
    interaction.update()
    print('--------interaction ok-----------')

