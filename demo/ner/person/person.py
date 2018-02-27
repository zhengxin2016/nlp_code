#!/usr/bin/env python3
import os,sys
import pycrfsuite
import base_crf

class Feature(base_crf.Feature):
    def __init__(self):
        super().__init__()
        self.resource_path = 'resource'
        self.load_resource()

    def load_resource(self):
        self.english_set = set()
        self.math_set = set()
        self.number_set = set()
        self.punctuation_set = set()
        with open(self.resource_path+'/english.txt') as f:
            for line in f:
                self.english_set.add(line.strip())
        with open(self.resource_path+'/math.txt') as f:
            for line in f:
                self.math_set.add(line.strip())
        with open(self.resource_path+'/number.txt') as f:
            for line in f:
                self.number_set.add(line.strip())
        with open(self.resource_path+'/punctuation.txt') as f:
            for line in f:
                self.punctuation_set.add(line.strip())

    def judge_char(self, char):
        if char in self.punctuation_set:
            return 'pun'
        elif char in self.number_set:
            return 'num'
        elif char in self.english_set:
            return 'abc'
        elif char in self.math_set:
            return 'mth'
        else:
            return 'oth'

    def word2features(self, sent, i):
        sent = ['start3', 'start2', 'start1'] + sent +\
                ['stop1', 'stop2', 'stop3']
        j = i + 3
        word = sent[j]
        word_L2 = sent[j-2]
        word_L1 = sent[j-1]
        word_R1 = sent[j+1]
        word_R2 = sent[j+2]
        word_R3 = sent[j+3]
        word_char = self.judge_char(sent[j])
        features = [
                'word='+word,
                '-1:word=' + word_L1,
                '-2:word=' + word_L2,
                '+1:word=' + word_R1,
                '+2:word=' + word_R2,
                '+3:word=' + word_R3,
                '-1,0:word=' + word_L1 + word,
                '0,+1:word=' + word + word_R1,
                '-1,+1:word=' + word_L1 + word_R1,
                'char_type=' + word_char,
                ]
        return features

class Data(base_crf.Data):
    def __init__(self):
        super().__init__()
        self.F = Feature()


if __name__ == '__main__':
    d = Data()
    data = d.load_data('data/train.txt', 'PER')
    crf = base_crf.CRF()
    crf.train_model(data, 'test.model')

    while 1:
        sent = input('input:')
        F = Feature()
        sent = F.sent2features(list(sent.strip()))
        labels = crf.test_model('test.model', sent)
        print(labels)
