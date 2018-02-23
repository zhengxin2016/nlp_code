#!/usr/bin/env python3
import os,sys
import re

class Time_Peroid():
    def __init__(self):
        self.tpd_r = self.get_tpd_r()

    def get_tpd_r(self):
        return '(?!个)[过]{0,1}[0-9０-９两一二三四五六七八九十个半]{1,3}(年|小时|分钟|刻钟|秒钟)(之后|以后|过后|后){0,1}'

    def find_tpd(self, string):
        T_list = ['O']*len(string)
        ite = re.finditer(self.tpd_r, string)
        if ite:
            for _ in ite:
                T_list[_.start()] = 'B-TPD'
                for i in range(_.start() + 1, _.end() - 1):
                    T_list[i] = 'I-TPD'
                T_list[_.end() - 1] = 'E-TPD'
        return T_list

if __name__ == '__main__':
    tpd = Time_Peroid()
    string = '十分钟之后再来'
    print(string)
    print(tpd.find_tpd(string))
    while 1:
        string = input('input:')
        print(tpd.find_tpd(string.strip()))

