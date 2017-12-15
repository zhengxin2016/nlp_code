#!/usr/bin/env python3

import os
import sys
import bottle
import json
from mongodb_client import Mongo
from update_solr import Update


def update_master(db):
    mongo = Mongo(db)
    if not mongo.copydb('10.89.100.14'):
        return {'result':'error'}
    up = Update('127.0.0.1', db)
    if not up.update('master'):
        return {'result':'error'}
    return {'result':'ok'}

CMD = {
        'update_master':update_master,
        }

@bottle.route('/:cmd/:db', method=['GET','POST'])
def cmd_2(cmd='', db=''):
    if cmd == 'update_master':
        return CMD[cmd](db)
    else:
        return {'result':'error'}

if __name__ == '__main__':
    bottle.run(host='0.0.0.0', port=1234)
