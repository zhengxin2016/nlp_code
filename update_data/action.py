#!/usr/bin/env python3

import os,sys
import xlrd
import shutil
from fun import clean_str, split_pro, Emotion

Data = {}
def read_data(filepath):
    #label questions
    book = xlrd.open_workbook(filepath)
    for sheet in book.sheets():
        for i in range(1, sheet.nrows):
            if sheet.row(i)[0].value == '':
                continue
            line = [clean_str(x.value) for x in sheet.row(i)]
            questions = split_pro(line[1], '/')
            if line[0] not in Data.keys():
                Data[line[0]] = questions
            else:
                Data[line[0]] += questions

def write_data(dirpath):
    if os.path.exists(dirpath):
        shutil.rmtree(dirpath)
    os.mkdir(dirpath)
    for key in Data.keys():
        f = open(os.path.join(dirpath, key), 'w', encoding='utf-8')
        for s in Data[key]:
            f.write(s+'\n')
        f.close()

if __name__ == '__main__':
    read_data('data_suning_biu/action.xlsx')
    write_data('action_data')
