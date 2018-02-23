#!/usr/bin/env python3
import os,sys
import re

class Number():
    def __init__(self):
        self.num_r = self.get_num_r()

    def get_num_r(self):
        return '[0-9０-９两零一二三四五六七八九十百千万亿兆〇壹贰叁肆伍陆柒捌玖拾佰仟]+'

    def find_num(self, string):
        T_list = ['O'] * len(string)
        ite = re.finditer(self.num_r, string)
        if ite:
            for _ in ite:
                T_list[_.start()] = 'B-NUM'
                for i in range(_.start() + 1, _.end() - 1):
                    T_list[i] = 'I-NUM'
                T_list[_.end() - 1] = 'E-NUM'
                if _.start() == _.end() - 1:
                    T_list[_.start()] = 'S-NUM'
        return T_list

if __name__ == '__main__':
    num = Number()
    string = '100+100'
    print(string)
    print(num.find_num(string))
    while 1:
        string = input('input:')
        print(num.find_num(string.strip()))

