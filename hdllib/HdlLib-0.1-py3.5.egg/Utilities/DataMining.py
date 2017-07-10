

import os, sys
from sklearn import linear_model
import numpy as np
import string
#import matplotlib.pyplot as plt

#=======================================================================
def LinearRegression(ModelValues, Variable="DimX*DimY"):
	"""
	Return dictionary of string linear mathematical expression for each values type in ModelValues.
	"""
	ModelTemplate=string.Template("${Slope}*"+str(Variable)+"+${Intercept}")
	LinearExpressions={}

	Colors=('blue', 'red', 'green')
	for RscType, Values in ModelValues.items():
		if len(Values)==0: continue
		X,Y=[],[]
		for x,y in Values:
			X.append(x)
			Y.append(y)

		X = np.array(X)
		Y = np.array(Y)
#			plt.scatter(X,Y)

		Regression = linear_model.LinearRegression()
		Regression.fit(X[:,np.newaxis], Y)

		LinearExpressions[RscType]=ModelTemplate.safe_substitute(Slope='{0:.3f}'.format(float(Regression.coef_)), Intercept='({0:.3f})'.format(float(Regression.intercept_)))

#			X_test = np.linspace(np.min(X), np.max(X), 100)
#			plt.plot(X_test, Regression.predict(X_test[:,np.newaxis]), color=Colors.pop(), linewidth=3)

#		plt.show()
	return LinearExpressions
	
	
	
	
	
	
	
	
	
	
	
