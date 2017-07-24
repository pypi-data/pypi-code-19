#!/usr/bin/env python
"""
This is a module that executes ml tasks from parsed xml
"""
from .parser import Parser
from sklearn.preprocessing import scale
from sklearn.preprocessing import StandardScaler
from .YeoJohnson import YeoJohnson
from sklearn.model_selection import train_test_split
from sklearn.model_selection import KFold
from sklearn.metrics import accuracy_score, mean_squared_error, cohen_kappa_score, r2_score, roc_curve
from math import sqrt
import numpy as np

class TaskExecuter(object):

	def __init__(self, filename, data, labels):
		"""
		Initializer for the task executer, the Initializer tries to run the machine learning method
		described in the given file on the given data

		:param str filename: path to the xml file
		:param ndarray data: numpy array of train and test data
		:param ndarray labels: numpy array of labels
		"""

		self.data = data
		self.labels = labels
		self.filename = filename
		self.parser = Parser()
		self.parser.parse_file(filename)
		self.pre_process()
		self.experiments = self.parser.get_all_combinations(self.parser.get_variables())
		

	def train(self):
		"""
		Trains the model according to the xml file
		"""

		if(int(self.parser.get_splits()) == 1):
			self.train_data, self.test_data, self.train_labels, self.test_labels = self.split()
			self.train()
		kf = KFold(n_splits=int(self.parser.get_splits()))
		i = 0
		results = []
		for train_index, test_index in kf.split(self.data):
			print("Fold: {}".format(i))
			self.train_data, self.test_data = self.data[train_index], self.data[test_index]
			self.train_labels, self.test_labels = self.labels[train_index], self.labels[test_index]
			predictions, scores = self._train()
			current_result = self.evaluate(predictions, scores)
			results.append(current_result)
			i += 1
		results = np.array(results)
		mean = np.mean(results, axis=0)
		print("Average Results {}".format(mean))



	def pre_process(self):
		"""
		Function applies pre processing methods before learning the model.
		"""

		methods = self.parser.get_preprocessing_methods()
		for method in methods:
			if method == 'scale':
				self.data = scale(self.data)
			if method == 'center':
				scaler = StandardScaler()
				self.data = scaler.fit_transform(self.data)
			if method == 'YeoJohnson':
				yeo_johnson = YeoJohnson()
				self.data = yeo_johnson.fit(self.data, 0.01)

	def split(self):
		"""
		Function that splits the data into train and test

		:returns: quadruple of train data, labels, test data, and labels
		:rtype: list(ndarray)
		"""

		partition_rate = self.parser.get_partition_rate()
		return train_test_split(self.data, self.labels, train_size=float(partition_rate))

	def _train(self):
		"""
		Function that trains the model

		:returns: tuple of ndarrays first predictions, and second is scores
		:rtype: tuple(ndarray)
		"""

		method = self.parser.get_method_name()
		if method == 'LinearSVM':
			predictions, scores = self._train_svm()
		if method == 'RandomForest':
			predictions, scores = self._train_random_forest()
		if method == 'LinearRegression':
			predictions, scores = self._train_linear_regression()
		if method == 'CART':
			predictions, scores = self._train_CART()
		if method == 'MultiLayerPerceptron':
			predictions, scores = self._train_multilayer_perceptorn()
		if method == 'StochasticGradientBoosting':
			predictions, scores = self._train_gradient_boosting()
		return predictions, scores
		

	def evaluate(self, labels, scores):
		"""
		Method that evaluates the trained model
		:param ndarray labels: numpy array of the labels
		:param ndarray scores: numpy array of he predicted scores

		:returns: numpy array of metrics depending on the xml file
		:rtype: ndarray
		"""
		results = []
		metric = self.parser.get_evaluation_metric()
		if metric == 'Accuracy' or metric == 'automatic':
			accuracy = accuracy_score(self.test_labels, labels)
			results.append(accuracy)
			if metric == 'Accuracy':
				print("Accuracy: {}".format(accuracy))
				return accuracy
		if metric == 'RMSE' or metric == 'automatic':
			rmse = sqrt(mean_squared_error(self.test_labels, labels))
			results.append(rmse)
			if metric == 'RMSE':
				print("RMSE: {}".format(rmse))
				return rmse
		if metric == 'Kappa' or metric == 'automatic':
			kappa = cohen_kappa_score(self.test_labels, labels)
			results.append(kappa)
			if metric == 'Kappa':
				print("Kappa: {}".format(kappa))
				return kappa
		if metric == 'Rsquared' or metric == 'automatic':
			r2 = r2_score(self.test_labels, labels)
			results.append(r2)
			if metric == 'Rsquared':
				print("R2: {}".format(r2_score))
				return r2
		if metric == 'ROC' or metric == 'automatic':
			print(self.test_labels.shape)
			print(scores.shape)
			print(scores)
			fpr, tpr, thresholds =roc_curve(self.test_labels, scores)
			results.append(fpr)
			results.append(tpr)
			results.append(thresholds)
			if metric == 'Rsquared':
				print("fpr: {}, tpr: {}, thresholds: {}".format(fpr, tpr, thresholds))
				return fpr, tpr, thresholds
		if metric == 'automatic':
			print("Accuracy: {}, RMSE: {}, Kappa: {}, R2: {}, fpr: {}, tpr: {}, thresholds: {}".format(
				  accuracy, rmse, kappa, r2, fpr, tpr, thresholds))
			return results

	def _train_svm(self):
		"""
		Method only used internally to train a specific model

		:returns: tuple of numpy arrays containing predictions and scores.
		:rtype: tuple(ndarray)
		"""
		from sklearn.svm import LinearSVC
		for experiment in self.experiments:
			model = LinearSVC(C=experiment['cost'])
			model.fit(self.train_data, self.train_labels)
			predictions = model.predict(self.test_data)
			scores = model.decision_function(self.test_data)
		return predictions, scores

	def _train_random_forest(self):
		"""
		Method only used internally to train a specific model

		:returns: tuple of numpy arrays containing predictions and scores.
		:rtype: tuple(ndarray)
		"""
		from sklearn.ensemble import RandomForestClassifier
		for experiment in self.experiments:
			print(experiment)
			model = RandomForestClassifier(n_estimators=int(experiment['randomlySelectedPredictors']))
			model.fit(self.train_data, self.train_labels)
			predictions = model.predict(self.test_data)
			scores = model.decision_function(self.test_data)
		return predictions, scores

	def _train_linear_regression(self):
		"""
		Method only used internally to train a specific model

		:returns: tuple of numpy arrays containing predictions and scores.
		:rtype: tuple(ndarray)
		"""
		from sklearn.linear_model import LinearRegression
		print(self.experiments)
		for experiment in self.experiments:
			print(experiment)
			model = LinearRegression(fit_intercept=experiment['intercept'])
			model.fit(self.train_data, self.train_labels)
			predictions = model.predict(self.test_data)		
			scores = model.decision_function(self.test_data)
		return predictions, scores

	def _train_CART(self):
		"""
		Method only used internally to train a specific model

		:returns: tuple of numpy arrays containing predictions and scores.
		:rtype: tuple(ndarray)
		"""
		from sklearn.tree import DecisionTreeClassifier
		model = DecisionTreeClassifier()
		model.fit(self.train_data, self.train_labels)
		predictions = model.predict(self.test_data)	
		scores = model.decision_function(self.test_data)
		return predictions, scores

	def _train_multilayer_perceptorn(self):
		"""
		Method only used internally to train a specific model

		:returns: tuple of numpy arrays containing predictions and scores.
		:rtype: tuple(ndarray)
		"""
		from sklearn.neural_network import MLPClassifier
		first_value = None
		for experiment in self.experiments:
			if first_value is None:
				first_value = int(experiment['hiddenUnits'])
				continue
			print(experiment)
			model = MLPClassifier(hidden_layer_sizes=(first_value, int(experiment['hiddenUnits'])), beta_1=experiment['weightDecay'])
			model.fit(self.train_data, self.train_labels)
			predictions = model.predict(self.test_data)	
			scores = model.decision_function(self.test_data)
			first_value = None
		return predictions, scores
	
	def _train_gradient_boosting(self):
		"""
		Method only used internally to train a specific model

		:returns: tuple of numpy arrays containing predictions and scores.
		:rtype: tuple(ndarray)
		"""
		from sklearn.ensemble import GradientBoostingClassifier
		print(self.experiments)
		for experiment in self.experiments:
			print(experiment)
			model = GradientBoostingClassifier(max_depth=int(experiment['maxTreeDepth']), learning_rate=experiment['shrinkage'],
											   n_estimators=int(experiment['numberTrees']), min_samples_leaf=int(experiment['minTerminalNodeSize']))
			model.fit(self.train_data, self.train_labels)
			predictions = model.predict(self.test_data)		
			scores = model.decision_function(self.test_data)
		return predictions, scores








				

		