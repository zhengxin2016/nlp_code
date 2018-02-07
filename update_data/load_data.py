#!/usr/bin/env python3

import os, sys
import traceback
from pymongo import MongoClient
import random
from bson.objectid import ObjectId
from solr import SOLR
from solr import SOLR_CORE_NAME


class SearchSolr():
    def __init__(self, ip='127.0.0.1', solr_core=SOLR_CORE_NAME):
        self.solr_url = 'http://'+ ip +':8999/solr'
        self.solr_core = solr_core
        self.solr = SOLR(self.solr_url)

    def load_data(self, select='*:*', fields=[], max_num=10, flag=False):
        try:
            def pro_x(x):
                y = {}
                y['store_id'] = x['store_id'][0]
                y['category'] = x['category'][0]
                y['instruction'] = x['instruction'][0]
                if 'entities' in x:
                    y['entities'] = x['entities']
                else:
                    y['entities'] = ''
                y['answers'] = x['answer']
                y['emotion_name'] = 'null'
                y['emotion_url'] = 'null'
                y['media'] = 'null'
                y['timeout'] = '0'
                return y

            Data = {}
            def pro_y(x):
                y = {}
                y['store_id'] = x['store_id'][0]
                y['category'] = x['category'][0]
                y['intent'] = x['intent']
                y['questions'] = x['question']
                if 'entities' in x:
                    y['entities'] = x['entities']
                else:
                    y['entities'] = ''
                if y['intent']+'|'+y['entities'] in Data:
                    Data[y['intent']+'|'+y['entities']]['questions'].append(x['question'][0])
                else:
                    Data[y['intent']+'|'+y['entities']] = y
                return y

            if flag == True:
                data = [pro_x(x) for x in self.solr.query_solr(self.solr_core,
                    select, fields, max_num).docs]
            else:
                data = [pro_y(x) for x in self.solr.query_solr(self.solr_core,
                    select, fields, max_num).docs]
                data = []
                for key in Data.keys():
                   data.append(Data[key])
            return data
        except:
            traceback.print_exc()
            return None

class Mongodb():
    def __init__(self, db_name, ip='127.0.0.1', port=27017):
        self.db_name = db_name
        self.db = MongoClient(ip, port)[db_name]
        self.db_test = MongoClient(ip, port)[db_name+'_test']
        self.solr_url = 'http://'+ ip +':8999/solr'
        self.solr_core = SOLR_CORE_NAME
        self.solr = SOLR(self.solr_url)

    def write(self, collection, data):
        try:
            self.db[collection].drop()
            self.db[collection].insert(data)
            self.db_test[collection].drop()
            self.db_test[collection].insert(data)
            return 1
        except:
            traceback.print_exc()
            return 0

    def write_data2solr(self, collection, data):
        query = 'scene_str:'+self.db_name+' AND topic_str:' +\
                collection
        self.solr.delete_solr_by_query(self.solr_core, query)
        for x in self.db[collection].find():
            data_one = x.copy()
            data_one['scene'] = self.db_name
            data_one['topic'] = collection
            data_one['_id'] = str(data_one['_id'])
            if collection in ['instruction']:
                self.solr.update_solr(data_one, self.solr_core)
                continue
            if 'super_intention' in data_one:
                if data_one['super_intention'] == '':
                    data_one['super_intention'] = 'null'
            data_one.pop('questions')
            for q in x['questions']:
                data_one['question'] = q
                data_one['question_ik'] = q
                data_one['question_cn'] = q
                self.solr.update_solr(data_one, self.solr_core)


if __name__ == '__main__':
    mongo = Mongodb(db_name='automata')
    s = SearchSolr(solr_core='instruction')
    data = s.load_data(max_num=100, flag=True)
    mongo.write(collection='instruction', data=data)
    mongo.write_data2solr(collection='instruction', data=data)

    s = SearchSolr(solr_core='automata')
    data = s.load_data(max_num=100000)
    mongo.write(collection='automata', data=data)
    mongo.write_data2solr(collection='automata', data=data)






