import os.path,re,nltk
from nltk.tokenize import word_tokenize
class Dictionary:
	path = "/usr/share/dict" # change to allow custom dictionaries to be used (windows support?)
	tags = dict(adjective="ADJ",adposition="ADP",adverb="ADV",conjunction="CONJ",determiner="DET",article="DET",noun="NOUN",numeral="NUM",particle="PRT",pronoun="PRON",verb="VERB",punctuation=".")

	def __init__(self,file):
		with open(os.path.join(Dictionary.path,file)) as f:
			self.words = [nltk.pos_tag(word_tokenize(line.strip()),tagset="universal")[0] for line in f.readlines()]

	def search(self,filter_id=None,params=[],wordset=[]):
		if filter_id==None or filter_id == 0: # no filter, just return the list
			return wordset
		elif filter_id == 1: # starts with X
			nwordset = []
			sletter = params.pop(0)
			for word in wordset:
				if word[0].lower().startswith(sletter):
					nwordset.append(word)
			try:
				return self.search(params.pop(0),params,nwordset)
			except IndexError as e:
				return nwordset
		elif filter_id == 2: # is a/an X
			nwordset = []
			postag = Dictionary.tags.get(params.pop(0),'')
			for word in wordset:
				if word[1]==postag:
					nwordset.append(word)
			try:
				return self.search(params.pop(0),params,nwordset)
			except IndexError as e:
				return nwordset
		else:
			print("Invalid filter ID",filter_id)

	def _parseArgs(self,method,args):
		params = []
		for param in args:
			if type(param)==list:
				params.extend(param)
			else:
				params.append(param)
		return self.search(method,params,self.words)

	def getWords(self):
		return self._parseArgs(0,[])

	def startsWith(self,*args):
		return self._parseArgs(1,args)

	def wordType(self,*args):
		return self._parseArgs(2,args)
