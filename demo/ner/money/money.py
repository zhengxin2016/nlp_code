#!/usr/bin/env python3
import os,sys
import re

class Money():
    def __init__(self):
        self.resource_path = 'resource'
        self.money_set = set()
        self.digital_set = set()
        self.get_money()
        self.mon_r = self.get_money_r()

    def get_money(self):
        with open(self.resource_path+'/money_cn.txt') as f:
            for line in f:
                self.money_set.add(line.strip())
        with open(self.resource_path+'/money_en.txt') as f:
            for line in f:
                self.money_set.add(line.strip())
        with open(self.resource_path+'/digital.txt') as f:
            for line in f:
                self.digital_set.add(line.strip())

    def get_money_r(self):
        money_1 = u'([0-9０-９两零一二三四五六七八九十百千万亿兆几壹贰叁肆伍陆柒捌玖拾]{1}[0-9０-９,，两零一二三四五六七八九十百千万亿兆几壹贰叁肆伍陆柒捌玖拾\.]'
        money_2 = u')){1,3}[0-9０-９两零一二三四五六七八九]{0,1}'
        mon_r = u'{0,30}(元|块|分|人民币|角|毛|RMB){1}(?!儿|去|形|钟|'
        suf_error = []
        with open(self.resource_path+'/suf_error.txt') as f:
            for line in f:
                suf_error.append(line.strip())
        return money_1 + mon_r + '|'.join(suf_error) + money_2

    def find_money(self, string):
        T_list = ['O'] * len(string)
        ite = re.finditer(self.mon_r, string)
        if ite:
            for _ in ite:
                T_list[_.start()] = 'B-MNY'
                for i in range(_.start() + 1, _.end() - 1):
                    T_list[i] = 'I-MNY'
                T_list[_.end() -  1] = 'E-MNY'
        stop = 0
        for i in range(len(string)):
            if i >= stop:
                for j in range(len(string), i, -1):
                    if string[i:j] in self.money_set:
                        if i > 0 and string[i-1] in self.digital_set:
                            for k in range(i-1, -1, -1):
                                if string[k] in self.digital_set and k != 0:
                                    T_list[k] = 'I-MNY'
                                elif string[k] in self.digital_set and k == 0:
                                    T_list[k] = 'B-MNY'
                                else:
                                    T_list[k+1] = 'B-MNY'
                                    break
                            T_list[j-1] = 'E-MNY'
                            for k in range(i, j-1):
                                T_list[k] = 'I-MNY'
                            stop = j
                            break
        return T_list

if __name__ == '__main__':
    mny = Money()
    string = '我要取1000块钱,存两万美元'
    print(string)
    print(mny.find_money(string))
    while 1:
        string = input('input:')
        print(mny.find_money(string.strip()))





