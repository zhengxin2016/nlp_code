#!/usr/bin/env python3

import os
import sys
import shutil
from pymongo import MongoClient

class Output():
    def __init__(self, ip, port, db_name):
        self.db_name = db_name
        self.db = MongoClient(ip, port)[db_name]
        self.db_common = MongoClient(ip, port)['common']
        self.collections = self.db.collection_names()

    def write_dialogue(self):
        dirpath = self.db_name+'_dialogue_data'
        if os.path.exists(dirpath):
            shutil.rmtree(dirpath)
        os.mkdir(dirpath)
        data = {}
        for x in self.db['dialogue'].find():
            key = x['intention']
            data[key] = data.setdefault(key, []) + list(map(
                lambda q:x['super_intention']+q, x['equal_questions']))
        for k in data.keys():
            f = open(os.path.join(dirpath, k), 'w', encoding='utf-8')
            for i in data[k]:
                f.write(i+'\n')
            f.close()

    def write_topic_dialogue(self, filepath):
        data = [x['equal_questions'] for x in self.db['dialogue'].find()]
        f = open(filepath, 'w', encoding='utf-8')
        for d in set(sum(data, [])):
            f.write(d+'\n')
        f.close()

    def write_topic_common(self, dirpath):
        data = [x['question'] for x in self.db_common['repeat_guest'].find()]
        f = open(os.path.join(dirpath, 'repeat_guest'), 'w', encoding='utf-8')
        for d in set(data):
            f.write(d+'\n')
        f.close()
        data = [x['question'] for x in self.db_common['repeat_machine'].find()]
        f = open(os.path.join(dirpath, 'repeat_machine'), 'w', encoding='utf-8')
        for d in set(data):
            f.write(d+'\n')
        f.close()
        data = [x['equal_questions'] for x in self.db_common['interaction'].find()]
        f = open(os.path.join(dirpath, 'interaction'), 'a', encoding='utf-8')
        for d in set(sum(data, [])):
            f.write(d+'\n')
        f.close()

    def write_topic_collection(self, filepath, doc_name):
        data = [x['equal_questions'] for x in self.db[doc_name].find()]
        f = open(filepath, 'w', encoding='utf-8')
        for d in set(sum(data, [])):
            f.write(d+'\n')
        f.close()

    def write_topic(self):
        dirpath = self.db_name+'_topic_data'
        if os.path.exists(dirpath):
            shutil.rmtree(dirpath)
        os.mkdir(dirpath)
        for collection in self.collections:
            if collection == 'dialogue':
                self.write_topic_dialogue(os.path.join(dirpath, 'dialogue'))
            elif collection in ['greeting', 'qa', 'sale', 'interaction']:
                self.write_topic_collection(os.path.join(dirpath, collection), collection)
        self.write_topic_common(dirpath)


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
    out = Output(ip, port, mode)

    out.write_dialogue()
    out.write_topic()
    print('(^_^) load '+ mode +' ok...')
