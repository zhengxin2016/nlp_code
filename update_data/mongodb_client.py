#!/usr/bin/env python3

import os, sys
from pymongo import MongoClient
import random
from bson.objectid import ObjectId
from solr import SOLR
#sys.path.append("..")
#from module_database.mongo_solr import SOLR

class ReadData():
    def __init__(self, ip, port, db_name):
        self.db_name = db_name
        self.db = MongoClient(ip, port)[db_name]
        self.solr_url = 'http://'+ ip +':8999/solr'
        self.solr = SOLR(self.solr_url)

    def intention_answer(self, intention):
        try:
            core_name = 'zx_' + self.db_name + '_dialogue'
            select = 'intention_str:'+intention
            fields = ['answers', 'emotion_url', 'media', 'timeout']
            data = [x for x in self.solr.query_solr(core_name, select, fields,
                1).docs]
            data = data[0]
            return {'answer':random.sample(data['answers'], 1)[0], 'emotion':
                    data['emotion_url'][0], 'media':data['media'][0],
                    'timeout':data['timeout'][0]}
        except Exception:
            return {'answer':None, 'emotion':None, 'media':None, 'timeout':None}

    def intention_questions(self, intention, question, max_num = 10):
        try:
            if intention == '' or question == '':
                return None
            select = 'intention_str:'+intention+' AND '+'question:'+question
            fields = ['question']
            core = 'zx_' + self.db_name + '_dialogue'
            data = [x['question'][0] for x in self.solr.query_solr(core,
                select, fields, max_num).docs]
            return data
        except Exception:
            return None

    def intention_pair_questions(self, intention, super_intention, question,
            max_num = 10):
        try:
            if intention == '' or question == '':
                return None
            if super_intention == '':
                super_intention = 'null'
            select = 'super_intention_str:' + super_intention + \
                    ' AND intention_str:'+intention+' AND question:'+question
            fields = ['question']
            core = 'zx_' + self.db_name + '_dialogue'
            data = [x['question'][0] for x in self.solr.query_solr(core,
                select, fields, max_num).docs]
            return data
        except Exception:
            return None

    def solr_questions(self, core_name, question='', max_num = 10,
            fields=['_id', 'question']):
        try:
            def pro_data(data):
                for key in data.keys():
                    data[key] = data[key][0]
                return data
            if question == '':
                return None
            data = [pro_data(x) for x in self.solr.query_question_solr(core_name,
                question, fields, max_num).docs]
            return data
        except Exception:
            return None

    def solr_id2answers(self, core_name, _id):
        try:
            select = '_id_str:'+_id
            fields = ['answers', 'emotion_url', 'media', 'timeout']
            data = [x for x in self.solr.query_solr(core_name, select, fields,
                1).docs]
            data = data[0]
            return {'answer':random.sample(data['answers'], 1)[0], 'emotion':
                    data['emotion_url'][0], 'media':data['media'][0],
                    'timeout':data['timeout'][0]}
        except Exception:
            return {'answer':None, 'emotion':None, 'media':None, 'timeout':None}

    def qa_questions(self, question='', max_num = 10):
        core_name = 'zx_' + self.db_name + '_qa'
        fields = ['_id', 'question']
        return self.solr_questions(core_name, question, max_num, fields)

    def qa_id2answers(self, _id):
        core_name = 'zx_' + self.db_name + '_qa'
        return self.solr_id2answers(core_name, _id)

    def sale_questions(self, question='', max_num = 10):
        core_name = 'zx_' + self.db_name + '_sale'
        fields = ['_id', 'question', 'type']
        return self.solr_questions(core_name, question, max_num, fields)

    def sale_id2answers(self, _id):
        core_name = 'zx_' + self.db_name + '_sale'
        return self.solr_id2answers(core_name, _id)

    def sale_id2description(self, _id):
        try:
            select = '_id_str:'+_id
            fields = ['description']
            core_name = 'zx_' + self.db_name + '_sale'
            data = [x for x in self.solr.query_solr(core_name, select, fields,
                1).docs]
            data = data[0]
            return data['description']
        except Exception:
            return None

    def sale_type2answers(self, t=''):
        try:
            def pro_data(data):
                data['_id'] = data['_id'][0]
                data['type'] = data['type'][0]
                data['emotion_url'] = data['emotion_url'][0]
                data['media'] = data['media'][0]
                data['timeout'] = data['timeout'][0]
                return data
            if t:
                select = 'type_str:'+t
            else:
                select = 'type_str:*'
            fields = ['_id','answers','type','emotion_url','media','timeout']
            core_name = 'zx_' + self.db_name + '_sale'
            max_num = 20
            data = [pro_data(x) for x in self.solr.query_solr(core_name,
                select, fields, max_num).docs]
            return data
        except Exception:
            return None

    def sale_2_questions(self, question='', max_num = 10):
        core_name = 'zx_' + self.db_name + '_sale_2'
        fields = ['_id', 'question']
        return self.solr_questions(core_name, question, max_num, fields)

    def sale_2_id2answers(self, _id):
        core_name = 'zx_' + self.db_name + '_sale_2'
        return self.solr_id2answers(core_name, _id)

    def greetings_questions(self, question='', max_num = 10):
        core_name = 'zx_' + self.db_name + '_greeting'
        fields = ['_id', 'question']
        return self.solr_questions(core_name, question, max_num, fields)

    def greetings_id2answers(self, _id):
        core_name = 'zx_' + self.db_name + '_greeting'
        return self.solr_id2answers(core_name, _id)

    def interaction_questions(self, question='', max_num = 10):
        core_name = 'zx_' + self.db_name + '_interaction'
        fields = ['_id', 'question']
        return self.solr_questions(core_name, question, max_num, fields)

    def interaction_id2answers(self, _id):
        core_name = 'zx_' + self.db_name + '_interaction'
        return self.solr_id2answers(core_name, _id)

    def refuse2chat(self):
        try:
            core_name = 'zx_' + self.db_name + '_refuse2chat'
            select = '*:*'
            fields = ['answers', 'emotion_url', 'media', 'timeout']
            max_num = 10
            data = [x for x in self.solr.query_solr(core_name, select, fields,
                max_num).docs]
            data = random.sample(data, 1)[0]
            return {'answer':random.sample(data['answers'], 1)[0], 'emotion':
                    data['emotion_url'][0], 'media':data['media'][0],
                    'timeout':data['timeout'][0]}
        except Exception:
            return {'answer':None}

    def common_interaction_questions(self, question='', max_num = 10):
        core_name = 'zx_common_interaction'
        fields = ['_id', 'question']
        return self.solr_questions(core_name, question, max_num, fields)

    def common_interaction_id2answers(self, _id):
        core_name = 'zx_common_interaction'
        return self.solr_id2answers(core_name, _id)

if __name__ == '__main__':
    rd = ReadData('127.0.0.1', 27017, 'bank_ccb')
    print('XXXXXXXXXXXXX 存款五万以下 XXXXXXXXXXXXXXXXXXXXXXX')
    print('[存款五万以下] answer:', end=' ')
    print(rd.intention_answer('存款五万以下'))
    print('[存款五万以下] question_list:', end=' ')
    #print(rd.intention_questions('存款五万以下','我要存三万'))
    print(rd.intention_pair_questions('存款五万以下','', '我要存三万'))

    print('XXXXXXXXXXXXXX qa XXXXXXXXXXXXXXXXXXXXXX')
    a = rd.qa_questions(question='个人网银', max_num=5)[0]
    print(a)
    print(rd.qa_id2answers(a['_id']))

    print('XXXXXXXXXXXXX greeting XXXXXXXXXXXXXXXXXXXX')
    a = rd.greetings_questions(question='你好', max_num=5)[0]
    print(a)
    print(rd.greetings_id2answers(a['_id']))

    print('XXXXXXXXXXXXX sale_2 XXXXXXXXXXXXXXXXXXXX')
    a = rd.sale_2_questions(question='不要', max_num=5)[0]
    print(a)
    print(rd.sale_2_id2answers(a['_id']))

    print('XXXXXXXXXXXXXXXX sale XXXXXXXXXXXXXXXXXXXXXXXXX')
    a = rd.sale_questions(question='好冷', max_num=5)[0]
    print(a)
    print(rd.sale_id2answers(a['_id']))
    print(rd.sale_id2description(a['_id']))
    print(rd.sale_type2answers('微信银行')[0])
    print('XXXXXXXXXXXXXXXXX refuse2chat XXXXXXXXXXXXXXXXXX')
    rd = ReadData('127.0.0.1', 27017, 'ecovacs')
    print(rd.refuse2chat())
    print('XXXXXXXXXXXXXXXXX solr XXXXXXXXXXXXXXXXXX')
    rd = ReadData('127.0.0.1', 27017, 'bank_ccb')
    for x in rd.interaction_questions('你真笨', 3):
        print(x['question'], rd.interaction_id2answers(x['_id']))
    for x in rd.common_interaction_questions('你真笨', 3):
        print(x['question'], rd.common_interaction_id2answers(x['_id']))







