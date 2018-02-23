#!/usr/bin/env python3
import os,sys
import re

class Percentage():
    def __init__(self):
        self.pct_r = self.get_pct_r()

    def get_pct_r(self):
        pct_r = u'[零一二三四五六七八九十百千万亿几]{0,30}分之[零一二三四五六七八九十百几0-9０-９]{0,30}|[0-9０-９.]{1,20}[%％]{1}|[0-9０-９两一二三四五六七八九十\.]{1,15}个百分点'
        return pct_r

    def find_pct(self, string):
        T_list = ['O'] * len(string)
        ite = re.finditer(self.pct_r, string)
        if ite:
            for _ in ite:
                T_list[_.start()] = 'B-PCT'
                for i in range(_.start() + 1, _.end() - 1):
                    T_list[i] = 'I-PCT'
                T_list[_.end() - 1] = 'E-PCT'
        return T_list

if __name__ == '__main__':
    pct = Percentage()
    string = '存款利率是百分之四，贷款利率是5%'
    print(string)
    print(pct.find_pct(string))
    while 1:
        string = input('input:')
        print(pct.find_pct(string.strip()))
