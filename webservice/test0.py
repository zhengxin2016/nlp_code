#!/usr/bin/env python3

import os,sys
from pymongo import MongoClient
from bson.objectid import ObjectId

class Mongo():
    def __init__(self, db_name):
        self.db_name = db_name
        self.db = MongoClient('127.0.0.1', 27017)[self.db_name]

    def fun(self):
        self.db.tt.drop()
        data1 = {'_id':ObjectId('5a1265ef72ebad1314a19926'), 'label':'添加你好', 'equal_questions':['添加你好11','添加你好21','添加你好3']}
        data2 = {'_id':ObjectId('5a1265ef72ebad1314a19927'), 'label':'修改你好', 'equal_questions':['修改你好1','修改你好22','修改你好3']}
        data3 = {'_id':ObjectId('5a1265ef72ebad1314a19928'), 'label':'删除你好', 'equal_questions':['删除你好1','删除你好2','删除你好33']}
        self.db.tt.insert(data1)
        self.db.tt.insert(data2)
        self.db.tt.insert(data3)
        self.db.tt.delete_one({'_id':ObjectId('5a1265ef72ebad1314a19928')})

        self.db.log.drop()
        log1 = {'collection':'tt', 'cmd':'create', 'ids':['5a1265ef72ebad1314a19926'], 'comment':'add', 'status':'0', 'time':'01'}
        log2 = {'collection':'tt', 'cmd':'create', 'ids':['5a1265ef72ebad1314a19927'], 'comment':'add', 'status':'0', 'time':'02'}
        log3 = {'collection':'tt', 'cmd':'create', 'ids':['5a1265ef72ebad1314a19928'], 'comment':'add', 'status':'0', 'time':'03'}
        log4 = {'collection':'tt', 'cmd':'delete', 'ids':['5a1265ef72ebad1314a19928'], 'comment':'del', 'status':'0', 'time':'04'}
        #log1 = {'collection':'tt', 'cmd':'update', 'ids':['5a1265ef72ebad1314a19926'], 'comment':'add', 'status':'todo', 'time':'01'}
        #log2 = {'collection':'tt', 'cmd':'update', 'ids':['5a1265ef72ebad1314a19927'], 'comment':'add', 'status':'todo', 'time':'02'}
        #log3 = {'collection':'tt', 'cmd':'update', 'ids':['5a1265ef72ebad1314a19928'], 'comment':'add', 'status':'todo', 'time':'03'}
        self.db.log.insert(log1)
        self.db.log.insert(log2)
        self.db.log.insert(log3)
        self.db.log.insert(log4)

if __name__ == '__main__':
    m = Mongo('test')
    m.fun()
