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
    def __init__(self, ip, port, db_name='common',
                    collection_name='interaction'):
        super().__init__(ip, port, db_name, collection_name)

    def read_data(self, filepath):
        #0分组 1问题标签 2回答 3等价描述 4表情 5图片 6超时时间
        book = xlrd.open_workbook(filepath)
        for sheet in book.sheets():
            for i in range(1, sheet.nrows):
                row = sheet.row(i)
                if row[1].value != '' and row[2].value != '':
                    d = [clean_str(x.value) for x in row]
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

class Repeat():
    def __init__(self, ip, port):
        self.db_name = 'common'
        self.db = MongoClient(ip, port)[self.db_name]
        self.repeat_guest = []
        self.repeat_machine = []

    def load_data(self):
        for line in open('./data/common/repeat_guest'):
            line = line.strip()
            if not line:
                continue
            self.repeat_guest.append({'question':line})
        for line in open('./data/common/repeat_machine'):
            line = line.strip()
            if not line:
                continue
            self.repeat_machine.append({'question':line})

    def write_data2mongodb(self):
        self.db['repeat_guest'].drop()
        self.db['repeat_guest'].insert(self.repeat_guest)
        self.db['repeat_machine'].drop()
        self.db['repeat_machine'].insert(self.repeat_machine)

    def update(self):
        self.load_data()
        self.write_data2mongodb()

class Copydb():
    def __init__(self, ip, port):
        self.client = MongoClient(ip, port)

    def copy_mongodb(self):
        print('--------copydb starting--------')
        self.client.drop_database('common_test')
        self.client.admin.command('copydb', fromdb='common',
                todb='common_test')
        print('--------copydb ok--------------')

if __name__ == '__main__':
    ip = '127.0.0.1'
    port = 27017
    interaction = Interaction(ip, port)
    repeat = Repeat(ip, port)
    copydb = Copydb(ip, port)
    print('--------common starting--------')
    interaction.update()
    repeat.update()
    copydb.copy_mongodb()
    print('--------common ok-----------')

