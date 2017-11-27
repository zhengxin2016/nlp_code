#!/usr/bin/env python3
import os,sys
import datetime

def get_current_time():
    t = datetime.datetime.today()
    t = t.strftime("%Y_%m_%d_%H_%M_%S") 
    return t


if __name__ == '__main__':
    get_current_time()
