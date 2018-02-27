#!/usr/bin/env python3
import os,sys
import pycrfsuite

class Feature():
    def __init__(self):
        pass

    def word2features(self, sent, i):
        word = sent[i]
        features = ['word='+word]
        return features

    def sent2features(self, sent):
        return [self.word2features(sent, i) for i in range(len(sent))]

class Data():
    def __init__(self):
        self.data_path = 'data'
        self.F = Feature()

    def string2crf(self, string, entity_type):
        entity = 0
        begin = 0
        string = string.strip()
        sent = []
        labels = []
        for i in range(len(string)):
            if '[' == string[i]:
                entity = 1
                begin = 1
                continue
            if ']' == string[i]:
                entity = 0
                continue
            if entity == 1:
                if begin == 1:
                    if string[i+1] == ']':
                        sent.append(string[i])
                        labels.append('S-'+entity_type)
                    else:
                        sent.append(string[i])
                        labels.append('B-'+entity_type)
                    begin = 0
                elif string[i+1] == ']':
                    sent.append(string[i])
                    labels.append('E-'+entity_type)
                else:
                    sent.append(string[i])
                    labels.append('I-'+entity_type)
            else:
                sent.append(string[i])
                labels.append('O')
        return self.F.sent2features(sent), labels

    def load_data(self, data_path, entity_type):
        data = []
        with open(data_path) as f:
            for line in f:
                data.append(self.string2crf(line, entity_type))
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
        tagger.set(sent)
        labels = tagger.tag(sent)
        print(tagger.probability(labels))
        return labels


if __name__ == '__main__':
    d = Data()
    data = d.load_data('data/train.txt', 'PER')
    crf = CRF()
    crf.train_model(data, 'test.model')

    while 1:
        sent = input('input:')
        F = Feature()
        sent = F.sent2features(list(sent.strip()))
        labels = crf.test_model('test.model', sent)
        print(labels)
