#!/usr/bin/env python3
import os,sys
import traceback
from sys import argv

def restart_sys(field):
    Mode = ['bank', 'bank_psbc', 'suning', 'ecovacs']
    if field not in Mode:
        if field == 'suning_biu':
            field = 'suning'
        else:
            print('!!!error arg:', argv[1])
            return 0

    shell_path = '/home/ecovacs/nlp_git/SY1792-EcoNLP/nlp_framework/rnn_text_classification'
    shell_file = shell_path + '/restart.sh'
    cmd = "echo 'ecovacs01!' | sudo -S bash " + shell_file + " " + field + " " + shell_path
    #print('CMD: ' + cmd)
    try:
        r = os.system(cmd)
        if r:
            return 0
        return 1
    except:
        traceback.print_exc()
        return 0

if __name__ == '__main__':
    script, field = argv
    print(restart_sys(field))
