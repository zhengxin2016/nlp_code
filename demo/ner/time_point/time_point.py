#!/usr/bin/env python3
import os,sys
import re

class Time_Point():
    def __init__(self):
        self.resource_path = 'resource'
        self.tpt_r = self.get_tpt()

    def get_tpt(self):
        time_pre = '(大后天|明天|后天|每天|每周一|每周二|每周三|每周四|每周五|每周六|每周日){0,1}' \
                   '(黎明|拂晓|清晨|早晨|早上|上午|中午|正午|下午|黄昏|傍晚|晚上|午夜){0,1}(?<!'
        time_suf = '(am|pm|a.m|am.|a.m.|pm|p.m|pm.|p.m.){0,1}(?!'
        tpt_r = ')[0-9０-９两一二三四五六七八九十]{1,3}[:：点时][,，整半过]{0,1}([0-9０-９一二三四五六七八九十]{1,3}[分秒刻]{0,1}){0,2}'
        pre_error = []
        suf_error = []
        with open(self.resource_path+'/pre_error.txt')as f:
            for line in f:
                pre_error.append(line.strip())
        with open(self.resource_path+'/suf_error.txt')as f:
            for line in f:
                suf_error.append(line.strip())
        return time_pre + '|'.join(pre_error) + tpt_r + time_suf + '|'.join(suf_error)+')'

    def find_tpt(self, string):
        T_list = ['O'] * len(string)
        ite = re.finditer(self.tpt_r, string)
        if ite:
            for _ in ite:
                T_list[_.start()] = 'B-TPT'
                for i in range(_.start()+1,_.end()-1):
                    T_list[i] = 'I-TPT'
                T_list[_.end()-1] = 'E-TPT'
        return T_list

if __name__ == '__main__':
    tpt = Time_Point()
    string = '明天下午三点放假'
    print(tpt.find_tpt(string))
    while 1:
        string = input('input:')
        print(tpt.find_tpt(string.strip()))
