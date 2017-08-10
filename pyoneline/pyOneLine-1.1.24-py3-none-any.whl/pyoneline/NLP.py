#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jun  1 09:51:15 2017

@author: zhoumingzhen
"""

import os
import fileinput
import numpy as np
from snownlp import SnowNLP
from pypinyin import lazy_pinyin
from warnings import warn
from gensim import corpora
from gensim import models
from gensim import similarities
try:
    import jieba
    import jieba.analyse
    import jieba.posseg as pseg                        
except ImportError:
    warn('JieBa import failed!')
import pandas as pd


class BasicNLP(object):
    def __init__(self, sentence = '', words_path = '', stop_words_path = ''):
        self.sentence = sentence
        self.s = SnowNLP(sentence)
        if words_path != '':
            jieba.load_userdict(words_path)   # Load user dict
        if stop_words_path != '':    
            jieba.analyse.set_stop_words(stop_words_path) 
    
    @property
    def posSeg(self):
        pos = pseg.cut(self.sentence)
        return pos
    
    @property
    def jianti(self):
        han = self.s.han
        return han
    
    """The sentiments is about commodity evaluate"""
    @property
    def sentiments(self):
        score = self.s.sentiments
        return score
    
    def shortKey(self, topK = None):
        keywords = jieba.analyse.extract_tags(self.sentence, 
                                              topK = topK, 
                                              allowPOS=("n",),
                                              withWeight = False)
        return keywords
    
    def longKey(self, topK = None):
        keywords = jieba.analyse.textrank(self.sentence, topK = topK)  
        return keywords
    
    def summary(self, topK = 5):
        summary = self.s.summary(topK)
        return summary
    
    def pinyin(self, isFlag = 0):
        pinyin = lazy_pinyin(self.sentence,isFlag)
        return pinyin 
        
        
class HighNLP(BasicNLP):
    def __init__(self, doc_path, words_path = '', stop_words_path = ''):
        #try:
            self.data = list(map(lambda x: BasicNLP(x, words_path = words_path, 
                                 stop_words_path = stop_words_path).shortKey(), 
                                 fileinput.FileInput(doc_path)))
            self.dictionary = corpora.Dictionary(self.data)
            """Get doc's bow vector"""
            self.corpus = list(map(lambda x: self.dictionary.doc2bow(x), 
                                   self.data))
        #except:
            #raise("Not input doc_path")
    
    '''
    def tfidf(self, model_path = './tfidf_model'):
        """Get doc's tf-idf vector, 
           through tfidf[bow_vector] to 
           check word's tf and idf value
        """
        tfidf = models.TfidfModel(self.corpus)
        if not os.path.exists(model_path):os.makedirs(model_path)
        tfidf.save(model_path)
        print("Hint:tfidf_model has saved to", model_path)
        return tfidf
    
    # BM25 default return topK
    def sim(self, query:str, topK = 3) -> dict:
        query_keys = BasicNLP(query).shortKey()
        s = SnowNLP(self.data)
        score = s.sim(query_keys)
        sort_score = sorted(score)[::-1][:topK]
        doc_index = np.array(score).argsort().tolist()[::-1][:topK]
        doc_score = dict(zip(doc_index,  sort_score)) 
        return doc_score
    '''
    
    def train_lsi(self, dict_path, model_path , matrix_path, num_topics = 3):
        self.dictionary.save(dict_path)
        lsi_model = models.LsiModel(self.corpus, id2word = self.dictionary, 
                        num_topics = num_topics)
        lsi_model.save(model_path)
        lsi_matrix = similarities.MatrixSimilarity(lsi_model[self.corpus])
        lsi_matrix.save(matrix_path)
        print("save ok!")
     
     
    @staticmethod
    def lsi_sim(query, dict_path, model_path,matrix_path, topK =2):
        if not os.path.exists(model_path) or not os.path.exists(matrix_path): 
            return "No train!"
        else:
            bow_dict = corpora.Dictionary.load(dict_path)
            lsi_model = models.LsiModel.load(model_path)
            lsi_matrix = similarities.MatrixSimilarity.load(matrix_path)            
            query_bow = bow_dict.doc2bow(BasicNLP(query).shortKey())
            lsi_score = lsi_matrix[lsi_model[query_bow]]
            sort_score = sorted(lsi_score)[::-1][:topK]
            doc_index = np.array(lsi_score).argsort().tolist()[::-1][:topK]
            doc_score = dict(zip(doc_index,  sort_score))
            return doc_score
        
        


if __name__ == '__main__':
    '''
    
    dict_path = '/Users/zhoumingzhen/Anaconda_test_set/bow_dict'
    model_path = '/Users/zhoumingzhen/Anaconda_test_set/lsi_model' 
    matrix_path = '/Users/zhoumingzhen/Anaconda_test_set/lsi_matrix'
    
    """训练文本输入"""
    nlp = HighNLP('/Users/zhoumingzhen/Anaconda_test_set/gem_a3.csv', 
                  '/Users/zhoumingzhen/Anaconda_test_set/words.txt',
                  '/Users/zhoumingzhen/Anaconda_test_set/stop_words.txt') 
    """训练实例化"""
    #nlp.train_lsi(dict_path, model_path,matrix_path, ) 
    """测试"""
    
    
    score_dict = nlp.lsi_sim("", dict_path, model_path, matrix_path, 10)    
    print(score_dict)
    
    data = pd.read_csv("/Users/zhoumingzhen/Anaconda_test_set/gem_a3.csv", header = None)
    print(data.shape)
    print(data.ix[list(score_dict.keys())])
    '''
    '''
    data = pd.read_csv("/Users/zhoumingzhen/Anaconda_test_set/gem_a3.csv", header = None)
     
    data = data[1].ix[range(10,100)].values
    res = list(map(lambda x: BasicNLP(x).shortKey(), data))
    print(res)
    '''
    
    
    
    
    
    
