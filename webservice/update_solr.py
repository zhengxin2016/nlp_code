#!/usr/bin/env python3

import os,sys
import traceback
from pymongo import MongoClient
from bson.objectid import ObjectId
from data_backup import Data_backup
from solr import SOLR
from solr import SOLR_CORE_NAME

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

    def update_data(self, collection, cmd, _id):
        def insert_automata(data, collection):
            if collection in ['automata']:
                questions = data['questions'].copy()
                data.pop('questions')
                for q in questions:
                    data['question'] = q
                    self.solr.update_solr(data, self.core_name)
            elif collection in ['instruction']:
                self.solr.update_solr(data, self.core_name)
            else:
                return None

        def insert(collection, _id):
            data = self.db[collection].find_one({'_id':ObjectId(_id)})
            if not data:
                return
            data_one = data.copy()
            data_one['_id'] = str(data_one['_id'])
            data_one['scene'] = self.db_name
            data_one['topic'] = collection
            if self.db_name == 'automata':
                return insert_automata(data_one)
            if collection in ['refuse2chat', 'sentiment']:
                self.solr.update_solr(data_one, self.core_name)
                return None
            if 'super_intention' in data_one:
                if data_one['super_intention'] == '':
                    data_one['super_intention'] = 'null'
            data_one.pop('equal_questions')
            for q in data['equal_questions']:
                data_one['question'] = q
                data_one['question_ik'] = q
                self.solr.update_solr(data_one, self.core_name)

        if cmd == 'create':
            insert(collection, _id)
        elif cmd == 'update':
            self.solr.delete_solr_by_query(self.core_name, '_id_str:'+_id)
            insert(collection, _id)
        elif cmd == 'delete':
            self.solr.delete_solr_by_query(self.core_name, '_id_str:'+_id)
        else:
            return 0

    def update(self, server_name):
        try:
            logs = self.load_log(server_name)
            if not logs:
                print('no update!')
                return 1
            for log in logs:
                if log['cmd'] == 'create':
                    self.check_solr_core()
                for _id in log['ids']:
                    self.update_data(log['collection'], log['cmd'], _id)
                if server_name == 'develop':
                    value = {'status':'1'}
                elif server_name == 'master':
                    value = {'status':'2'}
                else:
                    return 0
                self.db.log.update_one({'_id':log['_id']}, {'$set':value})
            return 1
        except Exception:
            traceback.print_exc()
            return 0

if __name__ == '__main__':
    up = Update('127.0.0.1', 'data_core')
    #up.update('develop')
    #up.update('master')
