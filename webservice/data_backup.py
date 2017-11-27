#!/usr/bin/env python3
import os,sys
from pymongo import MongoClient
import shutil
import utils
from solr import SOLR

class Data_backup():
    def __init__(self, db_name):
        self.db_name = db_name
        self.client = MongoClient('127.0.0.1', 27017)
        self.db = self.client[self.db_name]
        self.solr_url = 'http://127.0.0.1:8999/solr'
        self.solr = SOLR(self.solr_url)

    def data_dump(self, datapath, comments):
        if not os.path.exists(datapath):
            os.mkdir(datapath)
        dirpath = os.path.join(datapath, utils.get_current_time())
        if os.path.exists(dirpath):
            shutil.rmtree(dirpath)
        os.mkdir(dirpath)
        cmd_dump = 'mongodump -d '+self.db_name+' -o '+dirpath
        os.system(cmd_dump)
        filepath = os.path.join(os.path.join(dirpath, self.db_name), 'comments')
        with open(filepath, 'w', encoding='utf8') as f:
            for x in comments:
                f.write(x+'\n')

    def mongodb_restore(self, dirpath):
        self.client.drop_database(self.db_name)
        self.client.drop_database(self.db_name+'_test')
        dbpath = os.path.join(dirpath, self.db_name)
        cmd_restore1 = 'mongorestore -d '+self.db_name+' '+dbpath
        cmd_restore2 = 'mongorestore -d '+self.db_name+'_test '+dbpath
        os.system(cmd_restore1)
        os.system(cmd_restore2)

    def solr_restore(self):
        collections = self.db.collection_names()
        if 'log' in collections:
            collections.remove('log')
        for collection in collections:
            core_name = 'zx_'+self.db_name+'_'+collection
            self.solr.delete_solr_core(core_name)
            self.solr.create_solr_core(core_name)
            for x in self.db[collection].find():
                data_one = x.copy()
                data_one['_id'] = str(data_one['_id'])
                data_one.pop('equal_questions')
                for q in x['equal_questions']:
                    data_one['question'] = q
                    self.solr.update_solr(data_one, core_name)

    def data_restore(self, dirpath):
        self.mongodb_restore(dirpath)
        self.solr_restore()

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




