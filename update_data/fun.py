#!/usr/bin/env python3

Emotion = {'null':'null',
        '晕':'dizzy.gif',
        '委屈':'sad.gif',
        '萌哭':'weep.gif',
        '调皮':'mischief.gif',
        '大笑':'laugh.gif',
        '尴尬':'awkward.gif',
        '亲亲':'kiss.gif',
        '花痴':'love.gif',
        '贱笑':'simle.gif',
        '贪财':'money.gif',
        '大哭':'cry.gif',
        '常态':'mood_full.gif',
        }

def clean_str(string):
    if not type(string) is str:
        string = str(int(string))
    string = string.strip()
    string = string.replace(',', '，')
    string = string.replace('?', '？')
    string = string.replace('!', '！')
    return string

def question_pro(q):
    q = q.replace(',', '')
    q = q.replace('?', '')
    q = q.replace('!', '')
    q = q.replace('，', '')
    q = q.replace('？', '')
    q = q.replace('！', '')
    q = q.replace('。', '')
    return q

def questions_pro(qs):
    for i in range(len(qs)):
        qs[i] = question_pro(qs[i])
        qs[i] = qs[i].lower()
    return qs

#带处理'/'的split()
def split_pro(string, c):
    string = string.replace(' ', '')
    string = string.replace('//', '/')
    string = string.strip('/')
    s = string.split(c)
    for i in range(len(s)):
        s[i] = s[i].strip()
    if '' in s:
        s.remove('')
    return s

