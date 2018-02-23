#!/usr/bin/env python3
import os,sys
import re

class Location():
    def __init__(self):
        self.resource_path = 'resource'
        self.loc_set = set()
        self.pass4loc = set()
        self.get_all_loc()

    def get_all_loc(self):
        loc_onesuf = {'省', '市', '镇', '盟', '县', '州', '区'}
        with open(self.resource_path+'/pass4loc.txt') as f:
            for line in f:
                line = line.strip()
                self.pass4loc.add(line)

        with open(self.resource_path+'/loc_oversea.txt') as f:
            for line in f:
                line_list = line.strip('#').split()
                for _ in line_list:
                    self.loc_set.add(_)

        with open(self.resource_path+'/loc_country.txt') as f:
            for line in f:
                line = line.strip()
                self.loc_set.add(line)

        with open(self.resource_path+'/loc_add.txt') as f:
            for line in f:
                line = line.strip()
                self.loc_set.add(line)

        with open(self.resource_path+'/loc_cn.txt') as f:
            for line in f:
                loc, loc_x, level = line.strip().split('\t')
                loc = re.sub('\(.*?\)|（.*?）', '', loc)
                if level == '1' or level == '2' or level == '3':
                    if loc[-1] in loc_onesuf:
                        self.loc_set.add(loc[:-1])
                    else:
                        self.loc_set.add(loc)

    def find_loc(self, string):
        stop = 0
        T_list = ['O'] * len(string)
        for i in range(len(string)):
            if i >= stop:
                for j in range(len(string), i, -1):
                    if string[i:j] in self.pass4loc:
                        stop = j
                        break
                    if string[i:j] in self.loc_set:
                        T_list[i] = 'B-LOC'
                        T_list[j-1] = 'E-LOC'
                        for k in range(i+1, j-1):
                            T_list[k] = 'I-LOC'
                        stop = j
                        break
        return T_list


if __name__ == '__main__':
    loc = Location()
    string = '我来自中国'
    print(string)
    print(loc.find_loc(string))
    while 1:
        string = input('input:')
        print(loc.find_loc(string.strip()))





