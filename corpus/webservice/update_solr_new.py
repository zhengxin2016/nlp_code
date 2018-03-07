#!/usr/bin/env python3

import os,sys
import traceback
from pymongo import MongoClient
from bson.objectid import ObjectId
from data_backup import Data_backup
from solr import SOLR
from solr import SOLR_CORE_NAME

'''
_id => str(_id)
增加scene:db_name topic:collection
如果有super_intention字段且为空，则替换为null
如果有questions或equal_questions字段，拆开存储
    {question, question_ik, question_cn},并清除questions或equal_questions
'''

class Update():
    def __init__(self, ip, db_name):
        self.db_name = db_name
        self.db = MongoClient('127.0.0.1', 27017)[db_name]
        self.core_name = SOLR_CORE_NAME
        self.solr_url = 'http://127.0.0.1:8999/solr'
        self.solr = SOLR(self.solr_url)

    def load_log(self, server_name):
        #_id, collection, cmd, ids, comment, status, time
        if server_name == 'develop':
            query = {'status':'0'}
        elif server_name == 'master':
            query = {'status':'1'}
        else:
            query = {'status':'3'}
        logs = [x for x in self.db.log.find(query).sort('time')]
        return logs

    def check_solr_core(self):
        if not self.solr.solr_core_exists(self.core_name):
            self.solr.create_solr_core(self.core_name)

    def update_data(self, collection):
        def insert(data):
            if not data:
                return
            data_one = data.copy()
            data_one['_id'] = str(data_one['_id'])
            data_one['scene'] = self.db_name
            data_one['topic'] = collection
            if 'super_intention' in data_one:
                if data_one['super_intention'] == '':
                    data_one['super_intention'] = 'null'
            if 'equal_questions' in data_one:
                data_one.pop('equal_questions')
                for q in data['equal_questions']:
                    data_one['question'] = q
                    data_one['question_ik'] = q
                    data_one['question_cn'] = q
                    self.solr.update_solr(data_one, self.core_name)
            elif 'questions' in data_one:
                data_one.pop('questions')
                for q in data['questions']:
                    data_one['question'] = q
                    data_one['question_ik'] = q
                    data_one['question_cn'] = q
                    self.solr.update_solr(data_one, self.core_name)
            else:
                self.solr.update_solr(data_one, self.core_name)

        self.solr.delete_solr_by_query(self.core_name,
                'scene_str:'+self.db_name+' AND topic_str:'+collection)
        data = [x for x in self.db[collection].find()]
        for d in data:
            insert(d)

    def update(self):
        try:
            for collection in self.db.collection_names():
                print('start '+collection)
                self.update_data(collection)
        except Exception:
            traceback.print_exc()
            return 0

if __name__ == '__main__':
    up = Update('127.0.0.1', 'bank_psbc')
    up.update()
