#!/usr/bin/env python3

import os,sys
import traceback
from pymongo import MongoClient
from solr import SOLR
from solr import SOLR_CORE_NAME

class Update_data():
    def __init__(self, db_name, solr_name=SOLR_CORE_NAME, ip='127.0.0.1',
            port=27017):
        self.db_name = db_name
        self.db = MongoClient(ip, port)[db_name]
        self.solr_url = 'http://'+ ip +':8999/solr'
        self.solr_core = solr_name
        self.solr = SOLR(self.solr_url)

    def write_data2solr(self, collection_name):
        query = 'scene_str:'+self.db_name + ' AND topic_str:' + collection_name
        self.solr.delete_solr_by_query(self.solr_core, query)
        for x in self.db[collection_name].find():
            data_one = x.copy()
            data_one['scene'] = self.db_name
            data_one['topic'] = collection_name
            data_one['_id'] = str(data_one['_id'])
            if collection_name in ['refuse2chat', 'sentiment']:
                self.solr.update_solr(data_one, self.solr_core)
                continue
            if 'super_intention' in data_one:
                if data_one['super_intention'] == '':
                    data_one['super_intention'] = 'null'
            data_one.pop('equal_questions')
            for q in x['equal_questions']:
                data_one['question'] = q
                data_one['question_ik'] = q
                data_one['question_cn'] = q
                self.solr.update_solr(data_one, self.solr_core)

Scene = {
        'bank_psbc':['dialogue', 'qa', 'greeting', 'sale', 'sale_2',
            'refuse2chat', 'interaction'],
        'suning_biu':['dialogue', 'qa', 'greeting', 'refuse2chat',
            'interaction'],
        'ecovacs':['dialogue', 'qa', 'greeting', 'sale', 'sale_2',
            'refuse2chat', 'interaction'],
        'bookstore':['qa', 'automata', 'instruction'],
        'common':['interaction', 'sentiment'],
        }
def update(argv):
    if len(argv) != 2:
        print('!!!The number of args is wrong!!!')
        return 0
    if argv[1] == 'all':
        Mode = list(Scene.keys())
    elif argv[1] not in Scene.keys():
        print('!!!error arg:', argv[1])
        return 0
    else:
        Mode = [argv[1]]
    for mode in Mode:
        print('########## '+mode+' START ###########')
        up = Update_data(mode)
        for collection in Scene[mode]:
            print('--------'+collection+' starting--------')
            up.write_data2solr(collection)
            print('--------'+collection+' ok-----------')
        print('########## '+mode+' END ###########')

if __name__ == '__main__':
    update(sys.argv)






