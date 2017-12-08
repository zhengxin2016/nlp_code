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

class Interaction():
    def __init__(self, ip, port, db_name):
        self.dirpath = 'data/' + db_name
        self.db_name = db_name
        self.db = MongoClient(ip, port)[db_name]
        self.interaction = []
        self.solr_url = 'http://'+ ip +':8999/solr'
        self.solr_core = 'zx_' + self.db_name + '_interaction'
        self.solr = SOLR(self.solr_url)

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
                            questions_pro(data['equal_questions'])
                    data['emotion_name'] = d[4]
                    data['emotion_url'] = Emotion[d[4]]
                    data['media'] = d[5]
                    data['timeout'] = timeout
                    self.interaction.append(data)

    def load_data(self):
        interaction_path = os.path.join(self.dirpath, 'interaction')
        for f in os.listdir(interaction_path):
            self.read_data(os.path.join(interaction_path, f))

    def write_data2mongodb(self):
        self.db['interaction'].drop()
        self.db['interaction'].insert(self.interaction)
        self.db['interaction'].create_index('group')
        self.db['interaction'].create_index('label')

    def write_data2solr(self):
        self.solr.delete_solr_core(self.solr_core)
        self.solr.create_solr_core(self.solr_core)
        for x in self.db['interaction'].find():
            data_one = x.copy()
            data_one['_id'] = str(data_one['_id'])
            data_one.pop('equal_questions')
            for q in x['equal_questions']:
                data_one['question'] = q
                data_one['question_ik'] = q
                self.solr.update_solr(data_one, self.solr_core)

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
    interaction = Interaction(ip, port, mode)
    print('--------interaction starting--------')
    interaction.update()
    print('--------interaction ok-----------')

