#!/usr/bin/env python3

import os
import sys
import bottle
import json
from mongodb_client import Mongo
from update_solr import Update

def count_data(db, collection, query):
    mongo = Mongo(db)
    data = mongo.count(collection)
    result = json.dumps({'result':data}, ensure_ascii=False)
    return result.encode('utf-8')

def load_group(db, collection, query):
    mongo = Mongo(db)
    if collection == 'dialogue':
        data = mongo.load_dialogue_business() 
    else:
        data = mongo.load_group(collection)
    result = json.dumps({'result':data}, ensure_ascii=False)
    return result.encode('utf-8')

def load_label(db, collection, query):
    mongo = Mongo(db)
    if type(query) == bytes:
        query = query.decode('utf-8')
    try:
        query = json.loads(query)
    except Exception:
        return {'result':'query format error'}
    if type(query) != dict:
        return {'result':'query format error'}
    if 'group' in query.keys():
        group = query['group']
    else:
        group = ''
    if collection == 'dialogue':
        data = mongo.load_dialogue_intention(group)
    else:
        data = mongo.load_label(collection, group)
    result = json.dumps({'result':data}, ensure_ascii=False)
    return result.encode('utf-8')

def load_data(db, collection, query):
    mongo = Mongo(db)
    if type(query) == bytes:
        query = query.decode('utf-8')
    try:
        query = json.loads(query)
    except Exception:
        return {'result':'query format error'}
    if type(query) != dict:
        return {'result':'query format error'}
    if collection == 'dialogue':
        data = mongo.load_dialogue_data(query)
    else:
        data = mongo.load_data(collection, query)
    result = json.dumps({'result':data}, ensure_ascii=False)
    return result.encode('utf-8')

def store_data(db, collection, query):
    mongo = Mongo(db)
    data = ''
    for line in bottle.request.body.readlines():
        if type(line) == bytes:
            line = line.decode('utf8')
        data += line
    if data == '':
        return {'result':'data null'}
    try:
        data = json.loads(data)
    except Exception:
        return {'result':'data format error'}
    if type(data) != dict:
        return {'result':'data format error'}
    if collection == 'dialogue':
        result = mongo.store_dialogue(data)
    else:
        result = mongo.store(collection, data)
    if not result:
        return {'result':'error'}
    return {'result':'ok'}

def search_data(db, collection, query):
    mongo = Mongo(db)
    if type(query) == bytes:
        query = query.decode('utf-8')
    try:
        query = json.loads(query)
    except Exception:
        return {'result':'query format error'}
    if type(query) != dict:
        return {'result':'query format error'}
    if collection == 'dialogue':
        data = mongo.search_dialogue(query)
    else:
        data = mongo.search(collection, query)
    result = json.dumps({'result':data}, ensure_ascii=False)
    result = result.encode('utf-8')
    return result

def commit(db, collection, query):
    #collections = ['dialogue', 'greeting', 'qa', 'sale']
    mongo = Mongo(db)
    #if collection not in collections:
    #    return {'result':'error'} 
    data = ''
    for line in bottle.request.body.readlines():
        if type(line) == bytes:
            line = line.decode('utf8')
        data += line
    if data == '':
        return {'result':'data null'}
    try:
        data = json.loads(data)
    except Exception:
        return {'result':'data format error'}
    if type(data) != dict:
        return {'result':'data format error'}
    if not mongo.commit(collection, data):
        return {'result':'xxerror'} 
    return {'result':'ok'}

def create(db, collection, query):
    mongo = Mongo(db)
    if not mongo.create_collection(collection):
        return {'result':'xxerror'} 
    return {'result':'ok'}

def update_develop(db):
    up = Update('127.0.0.1', db)
    if not up.update('develop'):
        return {'result':'error'}
    return {'result':'ok'}

def update_master(db):
    mongo = Mongo(db)
    if not mongo.copydb('10.89.14.142'):
        return {'result':'error'}
    up = Update('127.0.0.1', db)
    if not up.update('master'):
        return {'result':'error'}
    return {'result':'ok'}

CMD = {'count_data':count_data,
        'load_group':load_group,
        'load_label':load_label,
        'load_data':load_data,
        'store_data':store_data,
        'search_data':search_data,
        'commit':commit,
        'create':create,
        'update_develop':update_develop,
        'update_master':update_master,
        }
#DB = ['bank', 'bank_ccb', 'bank_psbc', 'suning_biu', 'ecovacs', 'ule']

@bottle.route('/:mode/:cmd/:db/:collection/:query', methods=['GET', 'POST'])
def cmd_5(mode='', cmd='', db='', collection='', query=''):
    if mode != 'read':
        return {'result':'error'}
    if cmd not in CMD.keys():
        return {'result':'cmd error'}
    #if db not in DB:
    #    return {'result':'db name error'}
    return CMD[cmd](db, collection, query)

@bottle.route('/:cmd/:db/:collection/:query', methods=['GET', 'POST'])
def cmd_4(cmd='', db='', collection='', query=''):
    if cmd not in CMD.keys():
        return {'result':'cmd error'}
    #if db not in DB:
    #    return {'result':'db name error'}
    return CMD[cmd](db+'_test', collection, query)

@bottle.route('/:cmd/:db/:collection', method=['GET','POST'])
def cmd_3(cmd='', db='', collection=''):
    if cmd == 'store_data':
        #if db not in DB:
        #    return {'result':'db name error'}
        return CMD[cmd](db, collection, '')
    elif cmd == 'commit':
        #if db not in DB:
        #    return {'result':'db name error'}
        return CMD[cmd](db, collection, '')
    elif cmd == 'create':
        return CMD[cmd](db, collection, '')
    else:
        return {'result':'error'}

@bottle.route('/:cmd/:db', method=['GET','POST'])
def cmd_2(cmd='', db=''):
    if cmd == 'update_develop':
        return CMD[cmd](db)
    else:
        return {'result':'error'}

if __name__ == '__main__':
    bottle.run(host='0.0.0.0', port=1234)
