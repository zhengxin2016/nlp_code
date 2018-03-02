#!/usr/bin/env python3

import os, sys
import traceback
import re
import json
from pymongo import MongoClient
from bson.objectid import ObjectId
import utils

class Mongo():
    def __init__(self, db_name):
        self.db_name = db_name
        self.client = MongoClient('127.0.0.1', 27017)
        self.db = self.client[self.db_name]
        if self.db_name.endswith('_test'):
            self.commit_db_name = self.db_name[:-5]
            self.commit_db = self.client[self.commit_db_name]
        else:
            self.commit_db_name = self.db_name
            self.commit_db = self.db
    '''
    client = MongoClient('127.0.0.1', 27017)
    client.drop_database('t')
    client.admin.command('copydb', fromdb='test', todb='t', fromhost='xx')
    db = client['t']
    #db.command('cloneCollection', **{'cloneCollection':'test.dialogue', 'from':'127.0.0.1:27017'})
    '''
    def delete_db(self):
        try:
            self.client.drop_database(self.db_name)
            self.client.drop_database(self.commit_db_name)
            return 1
        except:
            traceback.print_exc()
            return 0

    def delete_collection(self, collection):
        try:
            self.db[collection].drop()
            self.commit_db[collection].drop()
            return 1
        except:
            traceback.print_exc()
            return 0

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
            data = [{'label':x['super_intention'] +'_'+ x['intention'],
                '_id':str(x['_id'])} for x in self.db.dialogue.find(query)]
            return data
        except Exception:
            return None

    def load_dialogue_data(self, query):
        try:
            def p(x):
                x['_id'] = str(x['_id'])
                return x
            if 'group' in query.keys():
                query['business'] = query['group']
                query.pop('group')
            if 'label' in query.keys():
                intention = query['label']
                query['super_intention'] = intention.split('_')[0]
                query['intention'] = intention.split('_')[1]
                query.pop('label')
            if '_id' in query:
                query['_id'] = ObjectId(query['_id'])
            data = [p(x) for x in self.db.dialogue.find(query)]
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
                elif key == 'label':
                    query['$or'] = [{'super_intention':re.compile(raw_query[key])},
                            {'intention':re.compile(raw_query[key])}]
                else:
                    query[key] = re.compile(raw_query[key])
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
            data = [{'label':x['label'], '_id':str(x['_id'])} for x in
                    self.db[collection].find(query)]
            return data
        except Exception:
            return None

    def load_data(self, collection, query):
        try:
            def p(x):
                x['_id'] = str(x['_id'])
                return x
            if '_id' in query:
                query['_id'] = ObjectId(query['_id'])
            data = [p(x) for x in self.db[collection].find(query)]
            return data
        except Exception:
            return None

    def store(self, collection, data):
        try:
            for x in data['result']:
                if x['cmd'] == 'create':
                    x.pop('cmd')
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

    def search_data(self, collection, raw_query):
        try:
            def pro(x):
                x['_id'] = str(x['_id'])
                return x
            query = {}
            for key in raw_query.keys():
                query[key] = re.compile(raw_query[key])
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
                    if d is None:
                        continue
                    self.commit_db[collection].delete_one({'_id':_id})
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
            traceback.print_exc()
            return 0

    def copydb(self, fromhost):
        try:
            self.client.drop_database(self.db_name)
            self.client.admin.command('copydb', fromdb=self.db_name,
                    todb=self.db_name, fromhost=fromhost)
            return 1
        except Exception:
            return 0

    def search(self, collection, raw_query):
        try:
            def pro(x):
                if '_id' in x:
                    x['_id'] = str(x['_id'])
                return x
            query = {}
            if 'exact' in raw_query:
                for key in raw_query['exact']:
                    query[key] = raw_query['exact'][key]
                    if key == '_id':
                        query[key] = ObjectId(query[key])
            if 'regex' in raw_query:
                for key in raw_query['regex']:
                    query[key] = re.compile(raw_query['regex'][key])
            if 'fields' in raw_query and raw_query['fields'] != []:
                fields = {}
                for key in raw_query['fields']:
                    fields[key] = 1
                if '_id' not in raw_query['fields']:
                    fields['_id'] = 0
                data = [pro(x) for x in self.db[collection].find(query, fields)]
            else:
                data = [pro(x) for x in self.db[collection].find(query)]
            return data
        except Exception:
            return None

    def search_new(self, raw_query):
        '''
        {
        "collection":"instruction",
        "query":{"exact":{}, "regex":{}},
        "sort"{"instruction":1}
        "page_index":2,
        "page_size":10,
        "limit":5,
        "fields":[],
        }
        '''
        #data=[x for x in self.db.instruction.find({},{'_id':0}).limit(5).skip(2)]
        query = '''[{"$match":{"category":"process", "instruction":{"$regex":"api_call_"}}}, {"$project":{"instruction":1, "_id":0}}]'''
        query = json.loads(query)
        data=[x for x in self.db.instruction.aggregate(query)]
        for d in data:
            #print(d['instruction'])
            print(d)
        #print(help(self.db.instruction.map_reduce))
        data=[x for x in self.db.instruction.find({},{'instruction':1, '_id':0})]
        print(data)


if __name__ == '__main__':
    '''
    mongo = Mongo('test_test')
    data = {'result':{'cmd':'create', 'ids':['001', '002', '003'],
        'comment':'xxx'}}
    mongo.commit('tt', data)
    data = {'result':[{'cmd':'update', '_id':'5a376ff472ebad1d8560ea0d', 'label':'test0'}]}
    r = mongo.store('tt', data)
    print(r)
    mongo.create_collection('dialogue')
    data = {'result':{'cmd':'delete', 'ids':['5a09401f72ebad51948616bc']}}
    mongo.commit('dialogue', data)
    '''
    mongo = Mongo('automata')
    mongo.search_automata_new({})




