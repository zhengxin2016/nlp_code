#!/usr/bin/env python3
import os,sys
import traceback
from pymongo import MongoClient
import shutil
import utils
from solr import SOLR
from solr import SOLR_CORE_NAME

DATA_PATH = '../Data_dump'

class Data_backup():
    def __init__(self, db_name):
        self.db_name = db_name
        self.client = MongoClient('127.0.0.1', 27017)
        self.db = self.client[self.db_name]
        self.solr_url = 'http://127.0.0.1:8999/solr'
        self.solr = SOLR(self.solr_url)
        self.core_name = SOLR_CORE_NAME

    def data_dump(self, datapath, log_id):
        if not os.path.exists(datapath):
            os.mkdir(datapath)
        dirpath = os.path.join(datapath, log_id)
        if os.path.exists(dirpath):
            shutil.rmtree(dirpath)
        os.mkdir(dirpath)
        cmd_dump = 'mongodump -d '+self.db_name+' -o '+dirpath
        try:
            os.system(cmd_dump)
            return 1
        except:
            traceback.print_exc()
            return 0

    def mongodb_restore(self, dirpath):
        self.client.drop_database(self.db_name)
        self.client.drop_database(self.db_name+'_test')
        dbpath = os.path.join(dirpath, self.db_name)
        cmd_restore1 = 'mongorestore -d '+self.db_name+' '+dbpath
        cmd_restore2 = 'mongorestore -d '+self.db_name+'_test '+dbpath
        if os.system(cmd_restore1):
            return 0
        if os.system(cmd_restore2):
            return 0
        return 1

    def solr_restore(self):
        collections = self.db.collection_names()
        if 'log' in collections:
            collections.remove('log')
        try:
            for collection in collections:
                query = '(scene_str:' + self.db_name + \
                        ' AND topic_str:' + collection + ')'
                self.solr.delete_solr_by_query(self.core_name, query)
                for data in self.db[collection].find():
                    data_one = data.copy()
                    data_one['scene'] = self.db_name
                    data_one['topic'] = collection
                    data_one['_id'] = str(data_one['_id'])
                    if collection in ['refuse2chat', 'sentiment']:
                        self.solr.update_solr(data_one, self.core_name)
                        break
                    data_one.pop('equal_questions')
                    for q in data['equal_questions']:
                        data_one['question'] = q
                        self.solr.update_solr(data_one, self.core_name)
            return 1
        except:
            traceback.print_exc()
            return 0

    def data_restore(self, dirpath, _id):
        dirpath = os.path.join(dirpath, _id)
        return self.mongodb_restore(dirpath) and  self.solr_restore()

def check_args(argv):
    if len(argv) != 3:
        print('!!! The number of args is wrong!!!')
        return 0
    if argv[1] not in dbs:
        print('!!!error db_name:', argv[1])
        return 0
    if not os.path.exists(argv[2]):
        print('!!! no exists dirpath:', argv[2])
        return 0
    return 1

if __name__ == '__main__':
    #agrs: db_name, db_path
    dbs = ['bank', 'bank_ccb', 'test']
    if check_args(sys.argv):
        d = Data_backup(sys.argv[1])
        d.data_restore(sys.argv[2])




