#!/usr/bin/env python3

import os,sys
import json
from elasticsearch_client import ES
import time

def update(filepath):
    index_name = 'demo'
    type_name = 'person'
    index_mappings = \
    {'mappings':{
        'person':{'properties':
            {'subj':{'type':'keyword'},
             'height':{'type':'integer'},
             'weight':{'type':'integer'},
             'po':{'type':'nested',
                 'properties':{
                     'pred':{'type':'keyword'},
                     'obj':{'type':'keyword'}}
                 }
             }
            }
        }
    }
    es = ES()
    es.delete_index(index_name)
    es.create_index(index_name, index_mappings)
    count = 0
    t0 = time.time()
    with open(filepath) as f:
        actions =[]
        for line in f:
            count += 1
            line = line.strip()
            #es.insert(index_name=index_name, type_name=type_name, data=line)
            data = {'_index':index_name,
                    '_type':type_name,
                    '_source':line}
            actions.append(data)
        es.bulk(actions)
    print('total:', count)
    print('time:', time.time()-t0)

if __name__ == '__main__':
    update('./data/Person.json')
