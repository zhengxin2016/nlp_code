#!/usr/bin/env python3
import os,sys
import re

class Day():
    def __init__(self):
        self.resource_path = 'resource'
        self.day_r = self.get_day()
        print(self.day_r)

    def get_day(self):
        day_r = ')([0-9０-９〇零一二三四五六七八九十壹贰叁肆伍陆柒捌玖拾正元腊]{1,4}[年月日号]){1,3}(?!'
        pre_error = []
        suf_error = []
        with open(self.resource_path+'/pre_error.txt') as f:
            for line in f:
                pre_error.append(line.strip())
        with open(self.resource_path+'/suf_error.txt') as f:
            for line in f:
                suf_error.append(line.strip())
        day_r = '(?<!'+'|'.join(pre_error)+day_r+'|'.join(suf_error)+')'
        fes = '(' + self.get_festival() + ')'
        return day_r + '|' + fes

    def get_festival(self):
        fes = []
        with open(self.resource_path + '/festival.txt')as f:
            for line in f:
                fes.append(line.strip())
        return '|'.join(list(set(fes)))

    def find_day(self, string):
        T_list = ['O'] * len(string)
        ite = re.finditer(self.day_r, string)
        if ite:
            for _ in ite:
                T_list[_.start()] = 'B-DAY'
                for i in range(_.start() + 1, _.end()-1):
                    T_list[i] = 'I-DAY'
                T_list[_.end()-1] = 'E-DAY'
        return T_list

if __name__ == '__main__':
    day = Day()
    string = '今年国庆节放几天假？'
    print(string)
    print(day.find_day(string))
    while 1:
        string = input('input:')
        print(day.find_day(string.strip()))
