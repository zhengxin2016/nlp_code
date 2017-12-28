#!/usr/bin/env python3

import os,sys
from pymongo import MongoClient
from bson.objectid import ObjectId
from solr import SOLR
from data_backup import Data_backup

class Update():
    def __init__(self, ip, db_name):
        self.db_name = db_name
        self.db = MongoClient('127.0.0.1', 27017)[db_name]
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

    def check_solr_core(self, collection):
        core_name = 'zx_'+self.db_name+'_'+collection
        if not self.solr.solr_core_exists(core_name):
            self.solr.create_solr_core(core_name)

    def update_data(self, collection, cmd, _id):
        core_name = 'zx_'+self.db_name+'_'+collection
        def insert(collection, _id):
            data = self.db[collection].find_one({'_id':ObjectId(_id)})
            if not data:
                return
            data_one = data.copy()
            data_one['_id'] = str(data_one['_id'])
            data_one.pop('equal_questions')
            for q in data['equal_questions']:
                data_one['question'] = q
                self.solr.update_solr(data_one, core_name)
        if cmd == 'create':
            insert(collection, _id)
        elif cmd == 'update':
            self.solr.delete_solr_by_query(core_name, '_id:'+_id)
            insert(collection, _id)
        elif cmd == 'delete':
            self.solr.delete_solr_by_query(core_name, '_id:'+_id)
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
                    self.check_solr_core(log['collection'])
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
            print('exception')
            return 0

if __name__ == '__main__':
    up = Update('127.0.0.1', 'bank_ccb')
    up.update('develop')
    #up.update('master')
