import numpy as np
from statsmodels.regression.linear_model import OLS


class OLSUngarStyle(object):
	def get_scores_and_p_values(self, tdm, category):
		'''
		Parameters
		----------
		tdm: TermDocMatrix
		category: str, category name

		Returns
		-------
		pd.DataFrame(['coef', 'p-val'])
		'''
		X = tdm._X
		y = (tdm.get_category_names_by_row() == category).astype(int) * 2 - 1
		pX = X/X.sum(axis=1)
		ansX = pX.copy()
		ansX = 2 * np.sqrt(np.array(ansX) + 3./8)
		res = OLS(ansX, y).fit()
		return res
