#!/usr/bin/env python3

import os, sys
import re
from pymongo import MongoClient
from bson.objectid import ObjectId
import utils

class Mongo():
    def __init__(self, db_name):
        self.db_name = db_name
        self.client = MongoClient('127.0.0.1', 27017)
        self.db = self.client[db_name]
        self.commit_db = self.client[db_name.rstrip('_test')]
    '''
    client = MongoClient('127.0.0.1', 27017)
    client.drop_database('t')
    client.admin.command('copydb', fromdb='test', todb='t', fromhost='xx')
    db = client['t']
    #db.command('cloneCollection', **{'cloneCollection':'test.dialogue', 'from':'127.0.0.1:27017'})
    '''

    def create_collection(self, collection):
        return 1

    def load_dialogue_business(self):
        try:
            data = self.db.dialogue.distinct('business')
            return data
        except Exception:
            return None

    def load_dialogue_intention(self, business):
        try:
            query = {}
            if business:
                query['business'] = business
            data = [x['super_intention'] +'_'+ x['intention']
                    for x in self.db.dialogue.find(query)]
            return data
        except Exception:
            return None

    def load_dialogue_data(self, query):
        try:
            def p(x):
                x['_id'] = str(x['_id'])
                return x
            select = {}
            if 'group' in query.keys():
                select['business'] = query['group']
            if 'label' in query.keys():
                intention = query['label']
                #select['intention'] = intention
                select['super_intention'] = intention.split('_')[0]
                select['intention'] = intention.split('_')[1]
            data = [p(x) for x in self.db.dialogue.find(select)]
            return data
        except Exception:
            return None

    def store_dialogue(self, data):
        try:
            for x in data['result']:
                if x['cmd'] == 'create':
                    x.pop('_id')
                    x.pop('cmd')
                    self.db.dialogue.insert(x)
                elif x['cmd'] == 'delete':
                    if '_id' in x:
                        x['_id'] = ObjectId(x['_id'])
                    x.pop('cmd')
                    #self.db.dialogue.delete_one({'_id':x['_id']})
                    self.db.dialogue.delete_many(x)
                elif x['cmd'] == 'update':
                    x['_id'] = ObjectId(x['_id'])
                    x.pop('cmd')
                    self.db.dialogue.update_one({'_id':x['_id']}, {'$set':x})
                else:
                    return 0
            return 1
        except Exception:
            return 0

    def search_dialogue(self, raw_query):
        try:
            def pro(x):
                x['_id'] = str(x['_id'])
                return x
            query = {}
            for key in raw_query.keys():
                if key == 'group':
                    query['business'] = re.compile(raw_query[key])
                if key == 'label':
                    query['intention'] = re.compile(raw_query[key])
            data = [pro(x) for x in self.db.dialogue.find(query)]
            return data
        except Exception:
            return None

    def count(self, collection):
        return self.db[collection].count()

    def load_group(self, collection):
        try:
            data = self.db[collection].distinct('group')
            #data = [x['group'] for x in self.db[collection].find({},
            #    {'group':1})]
            return data
        except Exception:
            return None

    def load_label(self, collection, group):
        try:
            query = {}
            if group:
                query['group'] = group
            data = [x['label'] for x in
                    self.db[collection].find(query)]
            return data
        except Exception:
            return None

    def load_data(self, collection, query):
        try:
            def p(x):
                x['_id'] = str(x['_id'])
                return x
            data = [p(x) for x in self.db[collection].find(query)]
            return data
        except Exception:
            return None

    def store(self, collection, data):
        try:
            for x in data['result']:
                if x['cmd'] == 'create':
                    x.pop('_id')
                    self.db[collection].insert(x)
                elif x['cmd'] == 'delete':
                    if '_id' in x:
                        x['_id'] = ObjectId(x['_id'])
                    x.pop('cmd')
                    #self.db[collection].delete_one({'_id':x['_id']})
                    self.db[collection].delete_many(x)
                elif x['cmd'] == 'update':
                    x['_id'] = ObjectId(x['_id'])
                    x.pop('cmd')
                    self.db[collection].update_one({'_id':x['_id']}, {'$set':x})
                else:
                    return 0
            return 1
        except Exception:
            return 0

    def search(self, collection, raw_query):
        try:
            def pro(x):
                x['_id'] = str(x['_id'])
                return x
            query = {}
            for key in raw_query.keys():
                if key == 'group':
                    query['group'] = re.compile(raw_query[key])
                if key == 'label':
                    query['label'] = re.compile(raw_query[key])
            data = [pro(x) for x in self.db[collection].find(query)]
            return data
        except Exception:
            return None

    def commit_log(self, collection, log):
        log['collection'] = collection
        log['status'] = '0'
        log['time'] = utils.get_current_time()
        self.commit_db['log'].insert(log)

    def commit(self, collection, data):
        try:
            cmd = data['result']['cmd']
            ids = data['result']['ids']
            if cmd == 'create':
                for _id in ids:
                    _id = ObjectId(_id)
                    d = self.db[collection].find_one({'_id':_id})
                    self.commit_db[collection].insert(d)
            elif cmd == 'update':
                for _id in ids:
                    _id = ObjectId(_id)
                    d = self.db[collection].find_one({'_id':_id})
                    self.commit_db[collection].update_one({'_id':_id}, {'$set':d})
            elif cmd == 'delete':
                for _id in ids:
                    _id_o = ObjectId(_id)
                    self.commit_db[collection].delete_one({'_id':_id_o})
            else:
                return 0
            self.commit_log(collection, data['result'])
            return 1
        except Exception:
            return 0

    def copydb(self, fromhost):
        try:
            self.client.drop_database(self.db_name)
            self.client.admin.command('copydb', fromdb=self.db_name,
                    todb=self.db_name, fromhost=fromhost)
            return 1
        except Exception:
            return 0

if __name__ == '__main__':
    mongo = Mongo('test')
    data = {'result':{'cmd':'create', 'ids':['001', '002', '003'],
        'comment':'xxx'}}
    mongo.commit('tt', data)
    '''
    mongo.create_collection('dialogue')
    data = {'result':{'cmd':'delete', 'ids':['5a09401f72ebad51948616bc']}}
    mongo.commit('dialogue', data)
'''




