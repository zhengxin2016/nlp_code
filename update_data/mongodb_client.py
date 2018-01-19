#!/usr/bin/env python3

import os, sys
import traceback
from pymongo import MongoClient
import random
from bson.objectid import ObjectId
from solr import SOLR
#sys.path.append("..")
#from module_database.mongo_solr import SOLR
from solr import SOLR_CORE_NAME

'''
bank      :dialogue, qa, greeting, sale, sale_2, interaction, refuse2chat
bank_ccb  :dialogue, qa, greeting, sale, sale_2, interaction, refuse2chat
bank_psbc :dialogue, qa, greeting, sale, sale_2, interaction, refuse2chat
ecovacs   :dialogue, qa, greeting, sale, sale_2, interaction, refuse2chat
suning_biu:dialogue, qa, greeting, interaction, refuse2chat
common    :interaction, sentiment
'''

class SearchData():
    def __init__(self, ip='127.0.0.1', solr_core=SOLR_CORE_NAME):
        self.solr_url = 'http://'+ ip +':8999/solr'
        self.solr_core = solr_core
        self.solr = SOLR(self.solr_url)

    def search_answer(self, select='*:*', scene=[], topic=[]):
        try:
            fields = ['answers', 'emotion_url', 'media', 'timeout']
            if scene != []:
                select_part = '(scene_str:'+' OR scene_str:'.join(scene) + ')'
                select = select_part + ' AND ' + select
            if topic != []:
                select_part = '(topic_str:'+' OR topic_str:'.join(topic) + ')'
                select = select_part + ' AND ' + select
            data = [x for x in self.solr.query_solr(self.solr_core, select,
                fields, 1).docs]
            data = data[0]
            return {'answer':random.sample(data['answers'], 1)[0], 'emotion':
                    data['emotion_url'][0], 'media':data['media'][0],
                    'timeout':data['timeout'][0]}
        except:
            traceback.print_exc()
            return {'answer':None, 'emotion':None, 'media':None, 'timeout':None}

    def search_questions(self, select='*:*', scene=None, topic=None,
            fields=['question'], max_num=10):
        try:
            def pro_data(data):
                for key in data.keys():
                    data[key] = data[key][0]
                return data
            if scene != []:
                select_part = '(scene_str:'+' OR scene_str:'.join(scene) + ')'
                select = select_part + ' AND ' + select
            if topic != []:
                select_part = '(topic_str:'+' OR topic_str:'.join(topic) + ')'
                select = select_part + ' AND ' + select
            data = [pro_data(x) for x in self.solr.query_solr(self.solr_core,
                select, fields, max_num).docs]
            return data
        except:
            traceback.print_exc()
            return None

    def sale_id2description(self, _id, scene):
        try:
            select = 'scene_str:' + scene + ' AND _id_str:'+_id
            fields = ['description']
            data = [x for x in self.solr.query_solr(self.solr_core, select,
                fields, 1).docs]
            data = data[0]
            return data['description']
        except:
            traceback.print_exc()
            return None

    def sale_type2answers(self, scene, t=''):
        try:
            def pro_data(data):
                for key in data.keys():
                    data[key] = data[key][0]
                return data
            if t:
                select = 'scene_str:'+ scene +' AND type_str:'+t
            else:
                select = 'scene_str' + scene + ' AND type_str:*'
            fields = ['_id','answers','type','emotion_url','media','timeout']
            max_num = 20
            data = [pro_data(x) for x in self.solr.query_solr(self.solr_core,
                select, fields, max_num).docs]
            return data
        except:
            traceback.print_exc()
            return None

if __name__ == '__main__':
    s = SearchData()

    print('--------------- intention_answer ------------------------')
    intention = '取款'
    select = 'intention_str:'+intention
    r = s.search_answer(select=select, scene=['bank_psbc'],
            topic=['dialogue'])
    print(intention, r)

    print('\n--------------- intention_questions ------------------------')
    intention = '取款'
    question = '我要取钱'
    select = 'intention_str:' + intention + ' AND question_ik:' + question
    r = s.search_questions(select=select, scene=['bank_psbc'],
            topic=['dialogue'], fields=['question'], max_num=10)
    print(intention, question, r)

    print('\n-------------- intention_pair_questions -------------------')
    super_intention = 'null'
    intention = '取款'
    question = '我要取钱'
    select = 'super_intention_str:' + super_intention + ' AND intention_str:'+\
            intention + ' AND question_ik:' + question
    r = s.search_questions(select=select, scene=['bank_psbc'],
            topic=['dialogue'], fields=['question'], max_num=10)
    print(intention, question, r)

    print('\n--------------- qa_questions ------------------------')
    #sale_questions
    #sale_2_questions
    #greetings_questions
    #interaction_questions
    question = '信用卡活动'
    select = 'question_ik:' + question
    r = s.search_questions(select=select, scene=['bank_psbc'], topic=['qa'],
            fields=['_id', 'question'], max_num=10)
    print(question, r)

    print('\n--------------- qa_id2answer ------------------------')
    #sale_id2answers
    #sale_2_id2answers
    #greetings_id2answers
    #interaction_id2answers
    _id = r[0]['_id']
    select = '_id_str:' + _id
    r = s.search_answer(select=select, scene=['bank_psbc'], topic=['qa'])
    print(_id, r)

    print('\n--------------- sale_id2description ------------------------')
    r = s.search_questions(select='question_ik:我抢钱', scene=['bank_psbc'], topic=['sale'],
            fields=['_id', 'question'], max_num=10)
    _id = r[0]['_id']
    r = s.sale_id2description(_id, 'bank_psbc')
    print(_id, r)

    print('\n--------------- sale_type2answer ------------------------')
    type_str = '理财产品'
    r = s.sale_type2answers('bank_psbc', type_str)
    print(type_str, r)

    print('\n--------------- refuse2chat ------------------------')
    select = '*:*'
    r = s.search_answer(select=select, scene=['bank_psbc'],
            topic=['refuse2chat'])
    print(r)

    print('\n--------------- sentiment_answer ------------------------')
    label = 'Joy'
    select = 'label_str:' + label
    r = s.search_answer(select=select, scene=['common'], topic=['sentiment'])
    print(label, r)












