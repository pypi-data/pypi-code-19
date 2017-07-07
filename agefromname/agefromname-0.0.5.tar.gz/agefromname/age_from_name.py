import os
from datetime import datetime

import numpy as np
import pandas as pd


class InvalidSexException(Exception):
	pass


class AgeFromName(object):
	def __init__(self, mortality_df=None, year_of_birth_df=None):
		'''
		:param mortality_df: pd.DataFrame, optional
		:param year_of_birth_df: pd.DataFrame, optional
		'''
		if mortality_df is None:
			self._mortality_df = pd.read_csv(self._get_data_path('mortality_table.csv.gz'))
		else:
			self._mortality_df = mortality_df
		if year_of_birth_df is None:
			self._year_of_birth_df = pd.read_csv(self._get_data_path('year_of_birth_counts.csv.gz'))
		else:
			self._year_of_birth_df = year_of_birth_df

	def _get_data_path(self, file_name):
		return os.path.join(os.path.dirname(__file__), 'data', file_name)

	def prob_male(self, first_name, current_year = datetime.now().year, minimum_age=0):
		'''
		:param first_name: str, First name
		:param current_year: int, optional, defaults to current year
		:param minimum_age: int, optional, defaults to 0
		:return: float, probability person is male
		'''
		male_count = self.get_estimated_counts(first_name, 'm', current_year, minimum_age).sum()
		female_count = self.get_estimated_counts(first_name, 'f', current_year, minimum_age).sum()
		if male_count + female_count == 0: return 0.5
		prob = male_count*1./(male_count + female_count)
		return prob

	def prob_female(self, first_name, current_year = datetime.now().year, minimum_age=0):
		return 1 - self.prob_male(first_name, current_year, minimum_age)

	def get_estimated_counts(self,
	                         first_name,
	                         sex=None,
	                         current_year=datetime.now().year,
	                         minimum_age=0):
		'''
		:param first_name: str, First name
		:param sex: str, m or f for sex. None to ignore, by default.
		:param current_year: int, optional, defaults to current year
		:param minimum_age: int, optional, defaults to 0
		:return: pd.Series, with int indices indicating years of
			birth, and estimated counts of total population with that name and birth year
		'''
		first_name = first_name.lower()
		sex = self._check_and_normalize_gender(sex)

		if sex is not None:
			cur_df = (self._year_of_birth_df[self._birth_year_df_mask(current_year, first_name, minimum_age, sex)]
			          [['year_of_birth', 'count']])
			year_stats = (self._mortality_df[self._mortality_df.as_of_year == current_year]
			              [['year_of_birth', sex + '_prob_alive']])
			cur_df['prob_alive'] = np.interp(cur_df.year_of_birth,
			                                 year_stats.year_of_birth,
			                                 year_stats[sex + '_prob_alive'])
			cur_df['estimated_count'] = cur_df['prob_alive'] * cur_df['count']
			return cur_df.set_index('year_of_birth')['estimated_count']
		else:
			m_df = self.get_estimated_counts(first_name, 'm', current_year, minimum_age)
			f_df = self.get_estimated_counts(first_name, 'f', current_year, minimum_age)
			to_ret = pd.merge(pd.DataFrame(m_df),
			                  pd.DataFrame(f_df),
			                  how='outer',
			                  left_index=True,
			                  right_index=True,
			                  suffixes=['_m', '_f']).fillna(0).sum(axis=1)
			to_ret.name = 'estimated_count'
			return to_ret

	def _check_and_normalize_gender(self, gender):
		if gender is None: return gender
		try:
			gender.lower()
		except:
			raise InvalidSexException('The parameter sex must be "m" or "f" and not "%s".' % gender)
		if gender.lower() not in ('m', 'f'):
			raise InvalidSexException('The parameter sex must be "m" or "f" and not "%s".' % gender)
		return gender.lower()

	def _birth_year_df_mask(self, current_year, first_name, minimum_age, sex):
		mask = ((self._year_of_birth_df.first_name == first_name)
		        & (self._year_of_birth_df.year_of_birth
		           <= (current_year - minimum_age)))
		if sex is not None:
			mask &= (self._year_of_birth_df.sex == sex)
		return mask

	def argmax(self, first_name, sex, current_year=datetime.now().year, minimum_age=0):
		'''
		:param first_name: str, First name
		:param sex: str, m or f for sex
		:param current_year: int, optional, defaults to current year
		:param minimum_age: int, optional, defaults to 0
		:return: int, the most likely year of birth
		'''
		return self.get_estimated_counts(first_name, sex, current_year, minimum_age).argmax()

	def get_estimated_distribution(self,
	                               first_name,
	                               sex,
	                               current_year=datetime.now().year,
	                               minimum_age=0):
		'''
		:param first_name: str, First name
		:param sex: str, m or f for sex
		:param current_year: int, optional, defaults to current year
		:param minimum_age: int, optional, defaults to 0
		:return: pd.Series, with int indices indicating years of
			birth, and the estimated percentage of the total population of people who share sex and
			first name who were born that year.
		'''
		age_counts = self.get_estimated_counts(first_name, sex, current_year, minimum_age)
		to_ret = age_counts / age_counts.sum()
		to_ret.name = 'estimate_percentage'
		return to_ret
