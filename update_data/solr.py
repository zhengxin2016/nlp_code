#!/usr/bin/env python3

import os,sys
from SolrClient import SolrClient
import requests
import json
import shutil
from pymongo import MongoClient
home_dir = os.path.expanduser('~')

class SOLR():
    def __init__(self, url):
        self.url = url
        self.solr = SolrClient(self.url)
        self.solr_home = home_dir+'/solr-7.1.0/server/solr/'

    def solr_core_exists(self, core_name):
        url = self.url + '/admin/cores?action=STATUS&core='+core_name
        response = requests.get(url)
        r = response.json()
        if r['status'][core_name]:
            return 1
        else:
            return 0

    def create_solr_core(self, core_name):
        core_dir = os.path.join(self.solr_home, core_name)
        if os.path.exists(core_dir):
            shutil.rmtree(core_dir)
        os.makedirs(core_dir)
        src_dir = os.path.join(self.solr_home,
                'configsets/_default/conf')
                #'configsets/sample_techproducts_configs/conf')
        dst_dir = os.path.join(core_dir, 'conf')
        shutil.copytree(src_dir, dst_dir)
        url1 = self.url + '/admin/cores?action=CREATE&name='+core_name
        url2 = '&instanceDir='+ self.solr_home + core_name
        r = requests.get(url1+url2)
        #print(r.text)

    def delete_solr_core(self, core_name):
        url1 = self.url + '/admin/cores?action=UNLOAD&core='+core_name
        url2 = '&deleteIndex=true&deleteDataDir=true&deleteInstanceDir=true'
        r = requests.get(url1+url2)
        #print(r.text)

    def update_solr(self, data, core_name):
        url = self.url + '/' + core_name + '/update?wt=json'
        headers = {'Content-Type':'application/json', 'Connection':'close'}
        params = {'boost':1.0, 'overwrite':'true', 'commitWithin':1000}
        data = {'add':{'doc':data}}
        r = requests.post(url, headers=headers, params=params, json=data)
        #print(r.text)

    def delete_solr_by_id(self, core_name, _id):
        url = self.url + '/' + core_name + '/update?wt=json'
        headers = {'Content-Type':'application/xml'}
        params = {'commit':'true'}
        data = "<delete><id>"+_id+"</id></delete>"
        data = data.encode('utf8')
        r = requests.post(url, headers=headers, params=params, data=data)
        #print(r.text)

    def delete_solr_by_query(self, core_name, query):
        url = self.url + '/' + core_name + '/update?wt=json'
        headers = {'Content-Type':'application/xml'}
        params = {'commit':'true'}
        data = "<delete><query>"+query+"</query></delete>"
        data = data.encode('utf8')
        r = requests.post(url, headers=headers, params=params, data=data)
        print(r.text)

    def query_question_solr(self, core_name, question, fields, num):
        query = {
                'q':'question:'+question,
                'fl':fields,
                'rows':num,
                }
        res = self.solr.query(core_name, query)
        return res

    def query_solr(self, core_name, select, fields, num):
        query = {
                'q':select,
                'fl':fields,
                'rows':num,
                }
        res = self.solr.query(core_name, query)
        return res


def mongo():
    data = []
    db = MongoClient('127.0.0.1', 27017)['bank']
    for x in db['interaction'].find({},{'question':1}):
        data.append({'id':str(x['_id']), 'question':x['question']})
    return data

if __name__ == '__main__':
    URL = 'http://localhost:8999/solr'
    solr = SOLR(URL)
    core_name = 'test_core'
    #solr.delete_solr_core(core_name)
    #solr.create_solr_core(core_name)
    #Data = mongo()
    #for data in Data:
    #    solr.update_solr(data, core_name)
    query = 'intention:取款'
    solr.delete_solr_by_query(core_name, query)
    
    print('ok')
    while 1:
        question = input('question:')
        res = solr.query_question_solr(core_name, question, ['id', 'question'], 10)
        for x in res.docs:
            print(x['question'])




