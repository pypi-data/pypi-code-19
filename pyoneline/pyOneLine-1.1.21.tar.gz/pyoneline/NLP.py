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
        keywords = jieba.analyse.extract_tags(self.sentence, topK = topK)
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
    def __init__(self, doc_path = ''):
        try:
            self.data = list(map(lambda x: BasicNLP(x).shortKey(), fileinput.FileInput(doc_path)))
            self.dictionary = corpora.Dictionary(self.data)
            """Get doc's bow vector"""
            self.corpus = list(map(lambda x: self.dictionary.doc2bow(x), self.data))
        except:
            raise("Not input doc_path")
    
    def tfidf(self, model_path = './tfidf_model'):
        """Get doc's tf-idf vector, through tfidf[bow_vector] to check word's tf and idf value"""
        tfidf = models.TfidfModel(self.corpus)
        if not os.path.exists(model_path):
            tfidf.save(model_path)
            print("Hint:tfidf_model has saved to", model_path)
        return tfidf
    
    """BM25 default return top 10""" 
    def sim(self, query:str, topK = 3) -> dict:
        query_keys = BasicNLP(query).shortKey()
        s = SnowNLP(self.data)
        score = s.sim(query_keys)
        sort_score = sorted(score)[::-1][:topK]
        doc_index = np.array(score).argsort().tolist()[::-1][:topK]
        doc_score = dict(zip(doc_index,  sort_score)) 
        return doc_score
    
    def __lsi(self, num_topics, model_path):
        lsi_model = models.LsiModel(self.corpus, id2word = self.dictionary, num_topics = num_topics)
        lsi_matrix = similarities.MatrixSimilarity(lsi_model[self.corpus])
        if not os.path.exists(model_path):
            lsi_matrix.save(model_path)
            print("Hint:lsi_matrix has saved to", model_path)
        return lsi_model
    
    def lsi_sim(self, query, num_topics = 3, model_path = './lsi_matrix', topK = 3):
        query_keys = BasicNLP(query).shortKey()
        query_bow = self.dictionary.doc2bow(query_keys)
        lsi_model = self.__lsi(num_topics = num_topics, model_path = model_path)
        query_vec = lsi_model[query_bow]
        lsi_matrix = similarities.MatrixSimilarity.load(model_path)
        lsi_score = lsi_matrix[query_vec]
        sort_score = sorted(lsi_score)[::-1][:topK]
        doc_index = np.array(lsi_score).argsort().tolist()[::-1][:topK]
        doc_score = dict(zip(doc_index,  sort_score))
        return doc_score
        


if __name__ == '__main__':
    nlp = HighNLP('./words')
    print(nlp.lsi_sim("周杰伦"))
    
    
    
