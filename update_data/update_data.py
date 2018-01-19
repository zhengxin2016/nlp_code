#!/usr/bin/env python3

import os
import sys
import xlrd
import shutil
from pymongo import MongoClient
from fun import clean_str, split_pro
from dialogue import Dialogue
from qa import Qa
from greeting import Greeting
from sale import Sale
from sale_2 import Sale_2
from refuse2chat import Refuse2chat
from interaction import Interaction
import common

class Update_data():
    def __init__(self, ip = '', port = '', db_name = ''):
        self.ip = ip
        self.port = port
        self.db_name = db_name
        self.client = MongoClient(ip, port)
        self.db = self.client[db_name]

    def update_dialogue(self):
        print('--------dialogue starting--------')
        d = Dialogue(self.ip, self.port, self.db_name)
        d.update()
        print('--------dialogue ok--------------')

    def update_qa(self):
        print('--------qa starting--------')
        q = Qa(self.ip, self.port, self.db_name)
        q.update()
        print('--------qa ok--------------')

    def update_greeting(self):
        print('--------greeting starting--------')
        g = Greeting(self.ip, self.port, self.db_name)
        g.update()
        print('--------greeting ok--------')

    def update_sale(self):
        print('--------sale starting--------')
        s = Sale(self.ip, self.port, self.db_name)
        s.update()
        print('--------sale ok--------')

    def update_sale_2(self):
        print('--------sale_2 starting--------')
        s = Sale_2(self.ip, self.port, self.db_name)
        s.update()
        print('--------sale_2 ok--------')

    def update_refuse2chat(self):
        print('--------refuse2chat starting--------')
        s = Refuse2chat(self.ip, self.port, self.db_name)
        s.update()
        print('--------refuse2chat ok--------')

    def update_interaction(self):
        print('--------interaction starting--------')
        i = Interaction(self.ip, self.port, self.db_name)
        i.update()
        print('--------interaction ok--------------')

    def copy_mongodb(self):
        print('--------copydb starting--------')
        self.client.drop_database(self.db_name+'_test')
        self.client.admin.command('copydb', fromdb=self.db_name,
                todb=self.db_name+'_test')
        print('--------copydb ok--------------')


def update(ip, port, mode):
    up = Update_data(ip, port, mode)
    Scene = {
            'bank':[up.update_dialogue, up.update_qa,
                up.update_greeting, up.update_sale,
                up.update_sale_2, up.update_refuse2chat,
                up.update_interaction],
            'bank_ccb':[up.update_dialogue, up.update_qa,
                up.update_greeting, up.update_sale,
                up.update_sale_2, up.update_refuse2chat,
                up.update_interaction],
            'bank_psbc':[up.update_dialogue, up.update_qa,
                up.update_greeting, up.update_sale,
                up.update_sale_2, up.update_refuse2chat,
                up.update_interaction],
            'suning_biu':[up.update_dialogue, up.update_qa,
                up.update_greeting,up.update_refuse2chat,
                up.update_interaction],
            'water':[up.update_dialogue, up.update_qa,
                up.update_greeting, up.update_refuse2chat,
                up.update_interaction],
            'ecovacs':[up.update_dialogue, up.update_qa,
                up.update_greeting, up.update_sale,
                up.update_sale_2, up.update_refuse2chat,
                up.update_interaction],
            'ule':[up.update_dialogue, up.update_qa,
                up.update_greeting, up.update_refuse2chat,
                up.update_interaction],
        }
    for f in Scene[mode]:
        f()
    up.copy_mongodb()

def update_common(ip, port):
    print('--------common starting--------')
    interaction = common.Interaction(ip, port)
    repeat = common.Repeat(ip, port)
    copydb = common.Copydb(ip, port)
    interaction.update()
    repeat.update()
    copydb.copy_mongodb()
    print('--------common ok-----------')

def update_sentiment(ip. port):
    print('--------sentiment starting-------')
    sen = Sentiment(ip, port)
    sen.update()
    print('--------sentiment ok-----------')


if __name__ == '__main__':
    ip = '127.0.0.1'
    port = 27017
    Mode = ['bank', 'bank_ccb', 'bank_psbc', 'suning_biu', 'ecovacs']
    if len(sys.argv) != 2:
        print('!!!The number of args is wrong!!!')
        assert(0)
    if sys.argv[1] == 'all':
        mode = Mode
    elif sys.argv[1] not in Mode:
        print('!!!error arg:', sys.argv[1])
        assert(0)
    else:
        mode = [sys.argv[1]]
    for m in mode:
        print('########## '+m+' START ###########')
        update(ip, port, m)
        print('########## '+m+' END ###########')
    if sys.argv[1] == 'all':
        update_common(ip, port)
    print('(^_^) '+ str(mode) +' all ok...')






