from natto import MeCab
from gensim import corpora, matutils
import pandas as pd
import csv
import os
import sys
import time
from sklearn.ensemble import RandomForestClassifier

class Dict2dense:
	def __init__(self, 
		datapath=None, 
		dictionary_save_path=None, 
		no_below=None, 
		no_above=None, 
		keep_n=None,
		data_number=None,
		dict_filter=False):
		self.datapath = datapath
		self.dictionary_save_path=dictionary_save_path
		self.no_below=no_below
		self.no_above=no_above
		self.keep_n=keep_n
		self.data_number=data_number
		self.dict_filter=dict_filter

	def create_dict(self):
		nm = MeCab('-Owakati')
		train_raw_data =[]
		train_label =[]
		for k in range(self.data_number):

		    csvdata = pd.read_csv(os.path.join(self.datapath,'data{}.csv'.format(k)), header=None)

		    for i in csvdata[0]:
		        train_raw_data.append(i)
		    for i in csvdata[1]:
		        train_label.append(i)

		raw_word_list =[]

		with open(os.path.join(self.datapath,'sentences.csv'), 'r') as f:
		    reader = csv.reader(f)
		    header = next(reader)
		    for row in reader:
		        raw_word_list.append(row) 

		wakati_by_sentnces_list = []

		for i in range(len(raw_word_list)):
		    wakati_by_sentnces_list.append([n.surface for n in nm.parse(raw_word_list[i][0], as_nodes=True) if n.is_nor()])
		        
		full_wakati_words = []
		for i in range(len(raw_word_list)):
		    for j in [n.surface for n in nm.parse(raw_word_list[i][0], as_nodes=True) if n.is_nor()]:
		        full_wakati_words.append(j)

		print("number of scentences is ",len(raw_word_list))
		print("number of wakati_gaki",len(full_wakati_words))


		dictionary = corpora.Dictionary(wakati_by_sentnces_list)
		print(dictionary)
		print()

		if self.dict_filter:		
			print("filter is on. dictionaly will be fillter")
			dictionary.filter_extremes(no_below=self.no_below, no_above=self.no_above, keep_n=self.keep_n)
			print(dictionary)
		else:
			print("filter is off. dictionaly will not fillter")		
		print()
		
		key_index=[]

		for i in dictionary.token2id.keys():
		    key_index.append(i)

		print()
		print("part of new dict contents")
		print("===========")
		print("word：ID")
		for i in range(5):
		    print(key_index[i],":",dictionary.token2id[key_index[i]])
		print("===========")
		print()

		dictionary.save_as_text(os.path.join(self.dictionary_save_path,'dictionary.txt'))
		print("new dict saved at {}".format(os.path.join(self.dictionary_save_path,'dictionary.txt')))
		print()

		dense =[]
		for j in train_raw_data:
			tmp = dictionary.doc2bow(list(j))
			dense.append(list(matutils.corpus2dense([tmp], num_terms=len(dictionary)).T[0])) 

		print()
		print("length of dense:",len(dense))
		print("length of train_label:",len(train_label))
		print("all procedure is successfly finished")

		return dense, train_label, dictionary


	def load_dict(self):
		return corpora.Dictionary.load_from_text(os.path.join(self.dictionary_save_path,'dictionary.txt'))

class Predictor:
	def __init__(self, 
		dense=None,
		train_label=None,
		dictionary=None,
		estimator=None):
		self.dense = dense
		self.train_label = train_label
		self.dictionary = dictionary
		self.estimator = estimator

	def randomforestmodel_initial_train(self):
		self.estimator = RandomForestClassifier()
		print("Random forest model initialized...")
		self.estimator.fit(self.dense, self.train_label)
		print("First-training of Random forest model is completed.")

	def randomforestmodel_retrain(self,dense=None, train_label=None, dictionary=None, estimator=None):
		self.estimator.fit(dense, train_label)
		print("Re-training of Random forest model is completed.")

	def onebyonepredict(self,analisys_words=None):
		test_dense = []
		test_tmp = self.dictionary.doc2bow(list(analisys_words))
		test_dense.append(list(matutils.corpus2dense([test_tmp], num_terms=len(self.dictionary)).T[0])) #vector by doc2bow corpas
		label_predict = self.estimator.predict(test_dense[0])
		print("Label prediction is complete. answer is :",label_predict[0])
		return label_predict

