#!/usr/bin/env python3

import os
import sys
import bottle
import json
import traceback
from mongodb_client import Mongo
from update_solr import Update
from data_backup import Data_backup, DATA_PATH
from restart_classify import restart_sys
import automata 

def count_data(db, collection, query):
    mongo = Mongo(db)
    data = mongo.count(collection)
    result = json.dumps({'result':data}, ensure_ascii=False, sort_keys=True)
    return result.encode('utf-8')

def load_group(db, collection, query):
    mongo = Mongo(db)
    if collection == 'dialogue':
        data = mongo.load_dialogue_business() 
    else:
        data = mongo.load_group(collection)
    result = json.dumps({'result':data}, ensure_ascii=False, sort_keys=True)
    return result.encode('utf-8')

def load_label(db, collection, query):
    mongo = Mongo(db)
    if type(query) == bytes:
        query = query.decode('utf-8')
    try:
        query = json.loads(query)
    except Exception:
        traceback.print_exc()
        return {'result':'query format error : not json'}
    if type(query) != dict:
        return {'result':'query format error : not dict'}
    if 'group' in query.keys():
        group = query['group']
    else:
        group = ''
    if collection == 'dialogue':
        data = mongo.load_dialogue_intention(group)
    else:
        data = mongo.load_label(collection, group)
    result = json.dumps({'result':data}, ensure_ascii=False, sort_keys=True)
    return result.encode('utf-8')

def load_data(db, collection, query):
    mongo = Mongo(db)
    if type(query) == bytes:
        query = query.decode('utf-8')
    try:
        query = json.loads(query)
    except Exception:
        traceback.print_exc()
        return {'result':'query format error : not json'}
    if type(query) != dict:
        return {'result':'query format error : not dict'}
    if collection == 'dialogue':
        data = mongo.load_dialogue_data(query)
    else:
        data = mongo.load_data(collection, query)
    result = json.dumps({'result':data}, ensure_ascii=False, sort_keys=True)
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
        traceback.print_exc()
        return {'result':'data format error : not json'}
    if type(data) != dict:
        return {'result':'data format error : not dict'}
    if collection == 'dialogue':
        result = mongo.store_dialogue(data['result'])
    else:
        result = mongo.store(collection, data['result'])
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
        traceback.print_exc()
        return {'result':'query format error : not json'}
    if type(query) != dict:
        return {'result':'query format error : not dict'}
    if collection == 'dialogue':
        data = mongo.search_dialogue(query)
    else:
        data = mongo.search_data(collection, query)
    result = json.dumps({'result':data}, ensure_ascii=False, sort_keys=True)
    result = result.encode('utf-8')
    return result

def commit(db, collection, query):
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
        traceback.print_exc()
        return {'result':'data format error : not json'}
    if type(data) != dict:
        return {'result':'data format error : not dict'}
    if not mongo.commit(collection, data):
        return {'result':'xxerror'} 
    return {'result':'ok'}

def create(db, collection, query):
    mongo = Mongo(db)
    if not mongo.create_collection(collection):
        return {'result':'xxerror'} 
    return {'result':'ok'}

def delete_db(db):
    mongo = Mongo(db)
    if not mongo.delete_db():
        return {'result':'error'} 
    return {'result':'ok'}

def delete_collection(db, collection):
    mongo = Mongo(db)
    if not mongo.delete_collection(collection):
        return {'result':'error'} 
    return {'result':'ok'}

def update_develop(db, log_id):
    up = Update('127.0.0.1', db)
    if not up.update():
        return {'result':'update data error'}
    backup = Data_backup(db)
    if not backup.data_dump(DATA_PATH, log_id):
        return {'result':'data dump error'}
    #if not restart_sys(db):
    #    return {'result':'restart system error'}
    return {'result':'ok'}

def restore_develop(db, log_id):
    backup = Data_backup(db)
    if not backup.data_restore(DATA_PATH, log_id):
        return {'result':'error'}
    return {'result':'ok'}

def search(db, collection, query):
    mongo = Mongo(db)
    if type(query) == bytes:
        query = query.decode('utf-8')
    try:
        query = json.loads(query)
    except:
        traceback.print_exc()
        return {'result':'query format error'}
    if type(query) != dict:
        return {'result':'query format error'}
    data = mongo.search(collection, query)
    result = json.dumps({'result':data}, ensure_ascii=False, sort_keys=True)
    result = result.encode('utf-8')
    return result

def load_graph(scene):
    try:
        mongo = Mongo(scene+'_test')
        mongo_automata = automata.Mongo_automata('127.0.0.1', 'automata_test')
        config = mongo_automata.load_graph_config(scene_id=scene)
        if not config:
            return {'result':'scene_id error'}
        nodes = mongo.search('instruction', {'fields':['instruction', '_id']})
        edges = mongo.search('automata', {'fields':['intent', '_id']})
        #nodes = list(map(lambda x:x['instruction'], nodes))
        #edges = list(map(lambda x:x['intent'], edges))

        result = json.dumps({'config':config, 'instruction':nodes,
            'automata':edges}, ensure_ascii=False, sort_keys=True)
        result = result.encode('utf-8')
        return result
    except:
        traceback.print_exc()
        return {'result':'error'}

def store_graph(scene):
    mongo = Mongo(scene+'_test')
    mongo_automata = automata.Mongo_automata('127.0.0.1', 'automata_test')
    data = ''
    for line in bottle.request.body.readlines():
        if type(line) == bytes:
            line = line.decode('utf8')
        data += line
    if data == '':
        return {'result':'data null'}
    try:
        data = json.loads(data)
    except:
        traceback.print_exc()
        return {'result':'data format error : not json'}
    if type(data) != dict:
        return {'result':'data format error : not dict'}
    try:
        if not mongo_automata.insert_graph_config(data['config']):
            return {'result':'update config error'}
        if not mongo.store('instruction', data['instruction']):
            return {'result':'update instruction error'}
        if not mongo.store('automata', data['automata']):
            return {'result':'update automata error'}
    except:
        traceback.print_exc()
        return {'result':'error'}
    return {'result':'ok'}

def commit_graph_config(scene):
    try:
        mongo_test = automata.Mongo_automata(db_name='automata_test')
        mongo = automata.Mongo_automata(db_name='automata')
        data = mongo_test.load_graph_config(scene)
        if not mongo.insert_graph_config(data):
            return {'result':'commit error'}
        return {'result':'ok'}
    except:
        traceback.print_exc()
        return {'result':'error'}

CMD = {'count_data':count_data,
        'load_group':load_group,
        'load_label':load_label,
        'load_data':load_data,
        'store_data':store_data,
        'search_data':search_data,
        'commit':commit,
        'create':create,
        'delete_db':delete_db,
        'delete_collection':delete_collection,
        'update_develop':update_develop,
        'restore_develop':restore_develop,
        'search_automata':search,
        'search_edit':search,
        'search_commit':search,
        }

@bottle.route('/:mode/:cmd/:db/:collection/:query', methods=['GET', 'POST'])
def cmd_5(mode='', cmd='', db='', collection='', query=''):
    if mode != 'read':
        return {'result':'error'}
    if cmd not in CMD.keys():
        return {'result':'cmd error'}
    return CMD[cmd](db, collection, query)

@bottle.route('/:cmd/:db/:collection/:query', methods=['GET', 'POST'])
def cmd_4(cmd='', db='', collection='', query=''):
    if cmd not in CMD.keys():
        return {'result':'cmd error'}
    #/search_automata/db_name/collection/{}
    if cmd in ['search_commit']:
        return CMD[cmd](db, collection, query)
    return CMD[cmd](db+'_test', collection, query)

@bottle.route('/:cmd/:db/:collection', method=['GET','POST'])
def cmd_3(cmd='', db='', collection=''):
    if cmd in ['store_data', 'commit', 'create']:
        return CMD[cmd](db+'_test', collection, '')
    elif cmd in ['update_develop', 'restore_develop']:
        return CMD[cmd](db, collection) #collection => log_id
    elif cmd in ['delete_collection']:
        return CMD[cmd](db+'_test', collection)
    else:
        return {'result':'error'}

@bottle.route('/:cmd/:scene', method=['GET','POST'])
def cmd_2(cmd='', scene=''):
    if cmd in ['delete_db']:
        return CMD[cmd](scene+'_test')
    elif cmd == 'show_graph':
        result = automata.show_graph(scene)
        if result == 1:
            return bottle.static_file(scene+'.png', '.')
        elif result == 0:
            return {'result':'scene_id error'}
        else:
            return {'result':scene+'config data error'}
    elif cmd == 'load_graph_config':
        try:
            mongo = automata.Mongo_automata('127.0.0.1', 'automata_test')
            config = mongo.load_graph_config(scene_id=scene)
            if not config:
                return {'result':'scene_id error'}
            result = json.dumps({'result':config}, ensure_ascii=False,
                    sort_keys=True)
            return result.encode('utf-8')
        except:
            traceback.print_exc()
            return {'result':'error'}
    elif cmd == 'load_graph':
        return load_graph(scene)
    elif cmd == 'store_graph':
        return store_graph(scene)
    elif cmd == 'commit_graph_config':
        return commit_graph_config(scene)
    else:
        return {'result':'error'}

@bottle.route('/:cmd', method=['GET','POST'])
def cmd_1(cmd=''):
    if cmd == 'store_graph_config':
        #return store_graph()
        return {'result':'not used'}
    else:
        return {'result':'error'}

if __name__ == '__main__':
    bottle.run(host='0.0.0.0', port=1234)
