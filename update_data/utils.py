#!/usr/bin/env python3

import os,sys
import traceback
from pymongo import MongoClient
from solr import SOLR
from solr import SOLR_CORE_NAME

class BaseClass():
    def __init__(self, ip, port, db_name, collection_name,
            solr_name=SOLR_CORE_NAME):
        self.dirpath = 'data/' + db_name
        self.db_name = db_name
        self.collection_name = collection_name
        self.db = MongoClient(ip, port)[db_name]
        self.collection = self.db[collection_name]
        self.data = []
        self.solr_url = 'http://'+ ip +':8999/solr'
        self.solr_core = solr_name
        self.solr = SOLR(self.solr_url)

    def write_data2mongodb(self):
        self.collection.drop()
        self.collection.insert(self.data)
        if self.collection_name in ['refuse2chat', 'sentiment']:
            self.collection.create_index('question')
        else:
            self.collection.create_index('group')
            self.collection.create_index('label')

    def write_data2solr(self):
        query = 'scene:'+self.db_name + ' AND topic:' + self.collection_name
        self.solr.delete_solr_by_query(self.solr_core, query)
        for x in self.collection.find():
            data_one = x.copy()
            data_one['scene'] = self.db_name
            data_one['topic'] = self.collection_name
            data_one['_id'] = str(data_one['_id'])
            if self.collection_name in ['refuse2chat', 'sentiment']:
                self.solr.update_solr(data_one, self.solr_core)
                continue
            if 'super_intention' in data_one:
                if data_one['super_intention'] == '':
                    data_one['super_intention'] = 'null'
            data_one.pop('equal_questions')
            for q in x['equal_questions']:
                data_one['question'] = q
                data_one['question_ik'] = q
                self.solr.update_solr(data_one, self.solr_core)


