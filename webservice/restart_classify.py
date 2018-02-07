#!/usr/bin/env python3
import os,sys

def restart_sys(field):
    Mode = ['bank', 'bank_psbc', 'suning', 'ecovacs']
    if field not in Mode:
        if field == 'suning_biu':
            field = 'suning'
        else:
            print('!!!error arg:', argv[1])
            return 0

    parent_path = '/home/ecovacs/nlp_git/SY1792-EcoNLP/nlp_framework'
    shell_path = parent_path + '/rnn_text_classification/restart.sh'
    cmd = "echo 'ecovacs01!' | sudo -S bash " + shell_path + " " + field + " " + parent_path
    #print('CMD: ' + cmd)
    try:
        os.system(cmd)
        return 1
    except:
        traceback.print_exc()
        return 0

if __name__ == '__main__':
    restart_sys('bank_psbc')
