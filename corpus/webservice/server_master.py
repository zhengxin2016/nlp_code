#!/usr/bin/env python3

import os
import sys
import bottle
import json
from mongodb_client import Mongo
from update_solr import Update
from data_backup import Data_backup, DATA_PATH
from restart_classify import restart_sys

def update_master(db, log_id):
    mongo = Mongo(db)
    if not mongo.copydb('10.89.100.14'):
        return {'result':'copydb error'}
    up = Update('127.0.0.1', db)
    if not up.update():
        return {'result':'update data error'}
    backup = Data_backup(db)
    if not backup.data_dump(DATA_PATH, log_id):
        return {'result':'data dump error'}
    #if not restart_sys(db):
    #    return {'result':'restart system error'}
    return {'result':'ok'}

def restore_master(db, log_id):
    backup = Data_backup(db)
    if not backup.data_restore(DATA_PATH, log_id):
        return {'result':'error'}
    return {'result':'ok'}

CMD = {
        'update_master':update_master,
        'restore_master':restore_master,
        }

@bottle.route('/:cmd/:db/:log_id', method=['GET','POST'])
def cmd_3(cmd='', db='', log_id=''):
    if cmd in ['update_master', 'restore_master']:
        return CMD[cmd](db, log_id)
    else:
        return {'result':'error'}

if __name__ == '__main__':
    bottle.run(host='0.0.0.0', port=1234)
