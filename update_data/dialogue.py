#!/usr/bin/env python3

import os
import sys
import xlrd
import shutil
from pymongo import MongoClient
from fun import clean_str, split_pro, Emotion, questions_pro
from solr import SOLR
from utils import BaseClass

class Dialogue(BaseClass):
    def __init__(self, ip, port, db_name, collection_name='dialogue'):
        super().__init__(ip, port, db_name, collection_name)
        self.q2i = {}
        self.i2a = {}
        self.I = set()
        self.II = set()

    def read_questions(self, filepath):
        #0问题 1回答 2业务 3意图 4上级意图 5等价描述
        book = xlrd.open_workbook(filepath)
        for sheet in book.sheets():
            for i in range(1, sheet.nrows):
                if sheet.row(i)[0].value == '':
                    continue
                line = [clean_str(x.value) for x in sheet.row(i)]
                questions = split_pro(line[0], '/') + split_pro(line[5], '/')
                key = line[2]+'#'+line[3]+ '#' + line[4]
                self.q2i[key] = self.q2i.setdefault(key, []) + questions

    def read_intention2answer(self, filepath):
        #0意图 1回答 2表情名称 3图片 4超时时间
        book = xlrd.open_workbook(filepath)
        for sheet in book.sheets():
            for i in range(1, sheet.nrows):
                if sheet.row(i)[0].value == '':
                    continue
                line = [clean_str(x.value) for x in sheet.row(i)]
                if line[2] == '':
                    line[2] = 'null'
                if line[3] == '':
                    line[3] = 'null'
                if len(line) > 4:
                    if line[4] == '':
                        timeout = 'null'
                    else:
                        timeout = line[4]
                else:
                    timeout = 'null'
                self.i2a[line[0]] = [split_pro(line[1], '/'), line[2],
                        line[3], timeout]
        self.II = set(self.i2a.keys())

    def load_data(self):
        dialogue_path = os.path.join(self.dirpath, 'dialogue')
        for f in os.listdir(dialogue_path):
            self.read_questions(os.path.join(dialogue_path, f))
        intention_path = os.path.join(self.dirpath, 'intention')
        for f in os.listdir(intention_path):
            self.read_intention2answer(os.path.join(intention_path, f))
            
    def write_data2mongodb(self):
        for key in self.q2i.keys():
            i = key.split('#')
            self.I.add(i[1])
            dic = {}
            dic['equal_questions'] = list(set(questions_pro(list(set(self.q2i[key])))))
            dic['business'] = i[0]
            dic['intention'] = i[1]
            dic['super_intention'] = i[2]
            dic['answers'] = self.i2a[i[1]][0]
            dic['emotion_name'] = self.i2a[i[1]][1]
            dic['emotion_url'] = Emotion[self.i2a[i[1]][1]]
            dic['media'] = self.i2a[i[1]][2]
            dic['timeout'] = self.i2a[i[1]][3]
            self.data.append(dic)
        self.db['dialogue'].drop()
        self.db['dialogue'].insert(self.data)
        self.db['dialogue'].create_index('intention')
        #print(self.II - self.I)

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
    d = Dialogue(ip, port, mode, 'dialogue')
    print('--------dialogue starting--------')
    d.update()
    print('--------dialogue ok-----------')
    




