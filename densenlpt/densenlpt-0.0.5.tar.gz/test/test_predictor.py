from densenlpt import Dict2dense,Predictor
import numpy as np

def test_Predictor():
	datapath = 'test/test_data'
	dictionary_save_path = 'test/test_data'

	modelobj = Predictor()
	loadpath ="test/test_data"
	modelobj.randomforestmodel_load(loadpath)

	modelobj.dictionary = modelobj.load_dict(dictionary_save_path)

	words = '今日は宮崎県から長崎までを旅行して、最後の締めに美味しい博多ラーメンが食べたいなあ'
	answer = modelobj.onebyonepredict(words)
	assert answer[0] == np.array([1])

	words = '今日は地下鉄を使って通勤しよう'
	answer2 = modelobj.onebyonepredict(words)
	assert answer2[0] == np.array([0])