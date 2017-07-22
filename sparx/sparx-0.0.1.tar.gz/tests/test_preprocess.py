from sparx.preprocess import *
import pandas as pd
import numpy as np

data = pd.read_csv('data/iris.csv')
query = {'name': 'Sam', 'age': 20 }


def test_strip_non_alphanum():
    assert strip_non_alphanum("hello world, India;") == ['hello', 'world', 'India', '']


def test_unique_identifier():
	assert unique_identifier(data) == ['Unnamed: 0']

def test_unique_identifier_empty():
	assert unique_identifier(data[["Sepal.Length","Sepal.Width",\
		"Petal.Length","Petal.Width","Species"]]) == []

def test_date_split():
	assert date_split("march/1/1980") == {'second': '00', 'hour': '00', 'year':\
	 '1980', 'day': '01', 'minute': '00', 'month': '03'}

def test_date_split():
	assert date_split("march-1-1980") == {'second': '00', 'hour': '00', 'year':\
	 '1980', 'day': '01', 'minute': '00', 'month': '03'}

def test_unique_value_count():
	assert unique_value_count(data) == {'Sepal.Length': {5.5: 7, 6.5: 5,\
	4.7999999999999998: 5, 5.0: 10, 6.0: 6, 7.0: 1, 7.2999999999999998: 1,\
	7.5999999999999996: 1, 5.5999999999999996: 6, 4.5999999999999996: 4,\
	5.0999999999999996: 9, 4.4000000000000004: 3, 6.0999999999999996: 6,\
	5.2000000000000002: 4, 4.7000000000000002: 2, 4.2999999999999998: 1,\
	6.2000000000000002: 4, 7.7000000000000002: 4, 5.9000000000000004: 3,\
	7.2000000000000002: 3, 6.7999999999999998: 3, 5.7000000000000002: 8,\
	6.9000000000000004: 4, 6.2999999999999998: 9, 5.7999999999999998: 7,\
	4.9000000000000004: 6, 6.5999999999999996: 2, 7.4000000000000004: 1,\
	7.9000000000000004: 1, 5.4000000000000004: 6, 6.4000000000000004: 7,\
	6.7000000000000002: 8, 7.0999999999999996: 1, 5.2999999999999998: 1, 4.5: 1}, 
	'Unnamed: 0': {1: 1, 2: 1, 3: 1, 4: 1, 5: 1, 6: 1, 7: 1, 8: 1, 9: 1, 10: 1,\
	11: 1, 12: 1, 13: 1, 14: 1, 15: 1, 16: 1, 17: 1, 18: 1, 19: 1, 20: 1, 21: 1,\
	22: 1, 23: 1, 24: 1, 25: 1, 26: 1, 27: 1, 28: 1, 29: 1, 30: 1, 31: 1, 32: 1,\
	33: 1, 34: 1, 35: 1, 36: 1, 37: 1, 38: 1, 39: 1, 40: 1, 41: 1, 42: 1, 43: 1,\
	44: 1, 45: 1, 46: 1, 47: 1, 48: 1, 49: 1, 50: 1, 51: 1, 52: 1, 53: 1, 54: 1,\
	55: 1, 56: 1, 57: 1, 58: 1, 59: 1, 60: 1, 61: 1, 62: 1, 63: 1, 64: 1, 65: 1,\
	66: 1, 67: 1, 68: 1, 69: 1, 70: 1, 71: 1, 72: 1, 73: 1, 74: 1, 75: 1, 76: 1,\
	77: 1, 78: 1, 79: 1, 80: 1, 81: 1, 82: 1, 83: 1, 84: 1, 85: 1, 86: 1, 87: 1,\
	88: 1, 89: 1, 90: 1, 91: 1, 92: 1, 93: 1, 94: 1, 95: 1, 96: 1, 97: 1, 98: 1,\
	99: 1, 100: 1, 101: 1, 102: 1, 103: 1, 104: 1, 105: 1, 106: 1, 107: 1, 108: 1,\
	109: 1, 110: 1, 111: 1, 112: 1, 113: 1, 114: 1, 115: 1, 116: 1, 117: 1, 118: 1,\
	119: 1, 120: 1, 121: 1, 122: 1, 123: 1, 124: 1, 125: 1, 126: 1, 127: 1, 128: 1,\
	129: 1, 130: 1, 131: 1, 132: 1, 133: 1, 134: 1, 135: 1, 136: 1, 137: 1, 138: 1,\
	139: 1, 140: 1, 141: 1, 142: 1, 143: 1, 144: 1, 145: 1, 146: 1, 147: 1, 148: 1,\
	149: 1, 150: 1},\
	'Petal.Width': {1.5: 12, 1.0: 7, 2.0: 6, 2.3999999999999999: 3, 0.5: 1,\
	0.10000000000000001: 5, 2.2999999999999998: 8, 1.3999999999999999: 8,\
	1.8999999999999999: 5, 2.2000000000000002: 3, 1.3: 13, 1.8: 12,\
	0.29999999999999999: 7, 1.2: 5, 1.6000000000000001: 4, 1.1000000000000001: 3,\
	2.5: 3, 0.59999999999999998: 1, 0.20000000000000001: 29, 0.40000000000000002: 7,\
	2.1000000000000001: 6, 1.7: 2},\
	'Petal.Length': {1.5: 13, 4.5: 8, 3.0: 1, 4.0: 5, 5.0: 4, 5.5: 3, 1.0: 1,\
	1.1000000000000001: 1, 3.8999999999999999: 3, 1.8999999999999999: 2,\
	4.0999999999999996: 3, 4.5999999999999996: 3, 5.5999999999999996: 6,\
	5.4000000000000004: 2, 5.0999999999999996: 8, 5.7000000000000002: 3, 6.0: 2,\
	3.7000000000000002: 1, 5.2000000000000002: 2, 5.2999999999999998: 2,\
	3.7999999999999998: 1, 4.2000000000000002: 4, 6.4000000000000004: 1,\
	5.7999999999999998: 3, 	6.7000000000000002: 2, 6.9000000000000004: 1,\
	5.9000000000000004: 2, 1.7: 4, 4.7999999999999998: 4, 	4.4000000000000004: 4,\
	6.0999999999999996: 3, 1.3999999999999999: 13, 	3.5: 2, 1.3: 7,\
	6.5999999999999996: 1, 1.6000000000000001: 7, 4.9000000000000004: 5,\
	4.7000000000000002: 5, 1.2: 2, 4.2999999999999998: 2, 3.6000000000000001: 1,\
	3.2999999999999998: 2, 6.2999999999999998: 1},\
	'Sepal.Width': {2.5: 8, 3.5: 6, 2.0: 1, 3.0: 26, 2.3999999999999999: 3,\
	3.8999999999999999: 2,	2.2999999999999998: 4, 4.0999999999999996: 1,\
	3.7999999999999998: 6, 2.6000000000000001: 5, 	2.2000000000000002: 3,\
	3.2999999999999998: 6, 4.2000000000000002: 1, 4.4000000000000004: 1,\
	3.3999999999999999: 12, 2.8999999999999999: 10, 3.7000000000000002: 3,\
	3.2000000000000002: 13, 	2.7000000000000002: 9, 3.6000000000000001: 4,\
	3.1000000000000001: 11, 2.7999999999999998: 14, 4.0: 1},\
	'Species': {'setosa': 50, 'versicolor': 50, 'virginica': 50}}

def test_count_missing_column():
	assert count_missing(data["Sepal.Length"]) == 0
'''	
def test_count_missing_dataframe():
	assert count_missing(data) == ('Sepal.Length': 0, 'Sepal.Width' :0, 'Petal.Length': 0, 'Petal.Width': 0, 'Species': 0)
	'''
							

def test_dict_query_string_dict():
	assert dict_query_string(query) == "age=20&name=Sam"

def test_dict_query_string_dictvalues():
	assert dict_query_string({'name': 'Sam', 'age': 20 }) == "age=20&name=Sam"

def test_describe_string():
	assert describe(data, "Species") == False

def test_describe_numeric():
	assert describe(data, "Sepal.Length") == {'max': 7.9000000000000004,\
	'mean': 5.843333333333335, 'median': 5.8, 'min': 4.2999999999999998}

def test_has_keywords():
	assert has_keywords(pd.Series(['Curd ', 'GOOG APPL MS', 'A B C', 'T Test is']),thresh=1) == True

def test_has_keywords_false():
	assert has_keywords(pd.Series(['Curd ', 'GOOG APPL MS', 'A B C', 'T Test is'])) == False

def test_missing_percent_column():
	assert missing_percent(data["Sepal.Width"]) == 0

def test_is_categorical_false():
	assert is_categorical(data["Sepal.Length"]) == False

def test_is_categorical_true():
	assert is_categorical(data["Species"]) == True

def test_is_date_true():
	assert is_date(pd.Series(['Jul 31, 2009', '2010-01-10', None])) == True

def test_is_date_false():
	assert is_date(pd.Series(['Jul 31, 2009', '2010-101-10', None])) == False


'''
def test_missing_percent_dataframe():
	assert missing_percent(data) == [Unnamed       0.0
Sepal.Length    0.0
Sepal.Width     0.0
Petal.Length    0.0
Petal.Width     0.0
Species         0.0
dtype: float64]
'''
def test_strip_non_alphanum():
	assert strip_non_alphanum("epqenw49021[4;;ds..,.,uo]mfLCP'X'") ==\
	['epqenw49021', '4', 'ds', 'uo', 'mfLCP', 'X', '']

def test_word_freq_count():
	assert word_freq_count("hello how are you") == {'a': 1, ' ': 3, 'e': 2,\
	'h': 2, 'l': 2, 'o': 3, 'r': 1, 'u': 1, 'w': 1, 'y': 1}

def test_ignore_stopwords():
	assert ignore_stopwords("I am basically a lazy person and i hate computers") ==\
	['I', ' ', 'm', ' ', 'b', 'c', 'l', 'l', 'y', ' ', ' ', 'l', 'z', 'y', ' ', 'p',\
	'e', 'r', 'o', 'n', ' ', 'n', 'd', ' ', ' ', 'h', 't', 'e', ' ', 'c',\
	'o', 'm', 'p', 'u', 't', 'e', 'r']

'''def test_ignore_outlier():
	assert ignore_outlier(df) ==\
		{        0    1   2\
        ... 0    1    1   0\
        ... 2    1   14  10\
        ... 3    3  100  11\
        ... 5   50   10  13\
        ... 6  100   11  14\
        ... 7  101   91  18\
        ... 8  111   16  19\
        ... 9  300   13   1}
     '''


