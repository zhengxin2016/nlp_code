#!/usr/bin/env python3

import os, sys
import json
from elasticsearch import Elasticsearch
from elasticsearch import helpers
import traceback

class ES():
    def __init__(self, ip='localhost', port=9200):
        self.es = Elasticsearch([{"host":ip, "port":port}])

    def create_index(self, index_name, index_mappings=None):
        if not self.es.indices.exists(index=index_name):
            self.es.indices.create(index=index_name, body=index_mappings)
            print('(create_index) created index: '+index_name)
        else:
            print('(create_index) index exist: '+index_name)

    def delete_index(self, index_name):
        if self.es.indices.exists(index=index_name):
            self.es.indices.delete(index=index_name)
            print('(delete_index) delete index: '+index_name)
        else:
            print('(delete_index) index no exist: '+index_name)


    def insert(self, index_name, type_name, data):
        try:
            self.es.index(index=index_name, doc_type=type_name, refresh=True, body=data)
        except:
            traceback.print_exc()

    def bulk(self, actions):
        try:
            helpers.bulk(self.es, actions)
        except:
            traceback.print_exc()

    def update_by_id(self, index_name, type_name, id, data):
        try:
            body = {'doc':data}
            self.es.update(index=index_name, doc_type=type_name, id=id, body=body, refresh=True)
        except:
            traceback.print_exc()

    def update_by_query(self, index_name, type_name, query, data):
        #NOTE
        try:
            body = {'query':query, 'doc':data}
            self.es.update_by_query(index=index_name, doc_type=type_name, body=body, refresh=True)
        except:
            traceback.print_exc()

    def delete_by_id(self, index_name, type_name, id):
        try:
            self.es.delete(index=index_name, doc_type=type_name, id=id, refresh=True)
        except:
            traceback.print_exc()

    def delete_by_query(self, index_name, type_name, query):
        #NOTE
        try:
            self.es.delete_by_query(index=index_name, doc_type=type_name, body=query, refresh=True)
        except:
            traceback.print_exc()

    def search(self, index_name, type_name, query):
        try:
            return self.es.search(index=index_name, doc_type=type_name, body=query)
        except:
            traceback.print_exc()
            return None


if __name__ == '__main__':
    index_mappings = {'mappings':{
        'user':{'properties':
            {'name_keyword':{'type':'keyword'}, 'name_text':{'type':'text'}}}
        }}
    es = ES()
    es.delete_index('mytest')
    es.create_index('mytest', index_mappings)
    data = {'name_keyword':'Tom cat', 'name_text':'Tom cat', 'age':22, 'about':'xxxx啦啦啦啦啦啦啦111'}
    es.es.index(index='mytest', doc_type='user', body=data, refresh=True)
    print('---------------------')
    query = {'query':{'term':{'name':'Jack'}}}
    query = {'query':{'match_all':{}}}
    result = es.search('mytest', 'user', query)
    print(result)
    for x in result['hits']['hits']:
        print(x['_id'], '\t',  x['_source'])
