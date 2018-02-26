#!/usr/bin/env python3
import os,sys
import pycrfsuite

class Feature():
    def __init__(self):
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

    def sent2features(self, sent):
        sent_crf = ['start3', 'start2', 'start1'] + sent +\
                ['stop1', 'stop2', 'stop3']
        return [self.word2features(sent_crf, i) for i in range(len(sent))]

class Data():
    def __init__(self):
        self.data_path = 'data'
        self.F = Feature()

    def string2crf(self, string):
        PER = 0
        B = 0
        string = string.strip()
        sent = []
        labels = []
        for i in range(len(string)):
            if '[' == string[i]:
                PER = 1
                B = 1
                continue
            if ']' == string[i]:
                PER = 0
                continue
            if PER == 1:
                if B == 1:
                    if string[i+1] == ']':
                        sent.append(string[i])
                        labels.append('S-PER')
                    else:
                        sent.append(string[i])
                        labels.append('B-PER')
                    B = 0
                elif string[i+1] == ']':
                    sent.append(string[i])
                    labels.append('E-PER')
                else:
                    sent.append(string[i])
                    labels.append('I-PER')
            else:
                sent.append(string[i])
                labels.append('O')
        return self.F.sent2features(sent), labels

    def load_data(self, data_path):
        data = []
        with open(data_path) as f:
            for line in f:
                data.append(self.string2crf(line))
        return data

class CRF():
    def __init__(self):
        pass

    def train_model(self, train_data, model_path):
        trainer = pycrfsuite.Trainer(verbose=False)
        for xseq, yseq in train_data:
            trainer.append(xseq, yseq)
        trainer.set_params({
            'c1': 1.0,
            'c2': 1e-3,
            'max_iterations': 50,
            'feature.possible_transitions': True
            })
        trainer.params()
        trainer.train(model_path)

    def test_model(self, model_path, sent):
        tagger = pycrfsuite.Tagger()
        tagger.open(model_path)
        labels = tagger.tag(sent)
        return labels


if __name__ == '__main__':
    d = Data()
    data = d.load_data('data/train.txt')
    crf = CRF()
    crf.train_model(data, 'test.model')

    while 1:
        sent = input('input:')
        F = Feature()
        sent = F.sent2features(list(sent.strip()))
        labels = crf.test_model('test.model', sent)
        print(labels)
