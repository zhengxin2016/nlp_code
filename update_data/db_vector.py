#!/usr/bin/env python3

import os, sys
import shutil
from pymongo import MongoClient

class DB_vectors():
    def __init__(self, ip, port, db_name):
        self.db_name = db_name
        self.data_db = MongoClient(ip, port)[db_name]
        self.vector_db = MongoClient(ip, port)['data_vectors']
        self.common_db = MongoClient(ip, port)['common']
        self.data = set()

    def load_data(self):
        for collection in self.data_db.collection_names():
            if collection == 'refuse2chat':
                continue
            for x in self.data_db[collection].find({}, {'equal_questions':1}):
                for q in x['equal_questions']:
                    self.data.add(q)

        for x in self.common_db['interaction'].find({}, {'equal_questions':1}):
            for q in x['equal_questions']:
                self.data.add(q)
        for x in self.common_db['repeat_guest'].find():
            self.data.add(x['question'])
        for x in self.common_db['repeat_machine'].find():
            self.data.add(x['question'])

        for x in self.data_db['dialogue'].find():
            for q in x['equal_questions']:
                self.data.add(x['super_intention']+q)
        
    def write_data(self):
        self.vector_db['vectors'].drop()
        for q in self.data:
            data = {}
            data['sentence'] = q
            #data['vector'] = [0,0,0]
            data['vector'] = [0,0,0]
            self.vector_db['vectors'].insert(data)
        self.vector_db['vectors'].create_index('sentence')

    def get_vector(self, s):
        try:
            result = self.vector_db['vectors'].find_one({'sentence':s})
            return result['vector']
        except Exception:
            return None


if __name__ == '__main__':
    s = DB_vectors('127.0.0.1', 27017, 'bank_psbc')
    #s.load_data()
    #s.write_data()
    #print(len(s.data))
    print(s.get_vector('你好'))
