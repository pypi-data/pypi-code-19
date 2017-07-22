"""datacost.py : Cost-Sensitive Data Measures

This module can be used to calculate various cost-sensitive measurements.
It is mainly intended for use in machine learning algorithms.

"""
import math

def cost_labelling_positive(num_positive, num_negative, cost_matrix):
  """Used to calculate the cost of labelling every data point as positive.

  Args:
    num_positive (int): The number of positive data points.
    num_negative (int): The number of negative data points.
    cost_matrix (dict): Every cost. e.g., {'TP':1, 'TN':0, 'FP':1, 'FN':5}

  Returns:
    (num): The cost of labelling every data point as positive.

  Raises:
    TypeError: If an incorrect number of arguments are passed.
    KeyError: If the passed cost_matrix is missing a cost.

  """
  if len(locals()) < 3:
    raise TypeError('Too few arguments.')
  elif len(locals()) > 3:
    raise TypeError('Too many arguments.')

  if any(k not in cost_matrix for k in ('TP', 'TN', 'FP', 'FN')):
    raise KeyError('A cost is missing from the passed cost matrix.')

  return num_positive * cost_matrix['TP'] + num_negative * cost_matrix['FP']

def cost_labelling_negative(num_positive, num_negative, cost_matrix):
  """Used to calculate the cost of labelling every data point as negative.

  Args:
    num_positive (int): The number of positive data points.
    num_negative (int): The number of negative data points.
    cost_matrix (dict): Every cost. e.g., {'TP':1, 'TN':0, 'FP':1, 'FN':5}

  Returns:
    (num): The cost of labelling every data point as negative.

  Raises:
    TypeError: If an incorrect number of arguments are passed.
    KeyError: If the passed cost_matrix is missing a cost.

  """
  if len(locals()) < 3:
    raise TypeError('Too few arguments.')
  elif len(locals()) > 3:
    raise TypeError('Too many arguments.')

  if any(k not in cost_matrix for k in ('TP', 'TN', 'FP', 'FN')):
    raise KeyError('A cost is missing from the passed cost matrix.')

  return num_negative * cost_matrix['TN'] + num_positive * cost_matrix['FN']

def expected_cost(num_positive, num_negative, cost_matrix):
  """Used to calculate the expected cost for a set of data points.

  Args:
    num_positive (int): The number of positive data points.
    num_negative (int): The number of negative data points.
    cost_matrix (dict): Every cost. e.g., {'TP':1, 'TN':0, 'FP':1, 'FN':5}

  Returns:
    (num): The expected cost for the given data points.

  Raises:
    TypeError: If an incorrect number of arguments are passed.
    KeyError: If the passed cost_matrix is missing a cost.

  """
  if len(locals()) < 3:
    raise TypeError('Too few arguments.')
  elif len(locals()) > 3:
    raise TypeError('Too many arguments.')
                                                                     
  if any(k not in cost_matrix for k in ('TP', 'TN', 'FP', 'FN')):
    raise KeyError('A cost is missing from the passed cost matrix.')

  c_p = cost_labelling_positive(num_positive, num_negative, cost_matrix)
  c_n = cost_labelling_negative(num_positive, num_negative, cost_matrix)

  return (2 * c_p * c_n)/(c_p + c_n)

def expected_cost_after_split(class_supports, cost_matrix):
  """Used to calculate the expected cost for a set of splitted data points.

  Args:
    class_supports (list<dict>): The class supports for each split where the
      i'th split corresponds to the (i-1)'th element of the list. For example,
      the second split could be {'positive' : 2, 'negative' : 6}.
    cost_matrix (dict): Every cost. e.g., {'TP':1, 'TN':0, 'FP':1, 'FN':5}

  Returns:
    (num): The expected cost for the set of splitted data points.

  Raises:
    TypeError: If an incorrect number of arguments are passed.
    KeyError: If the passed cost_matrix is missing a cost or the passed
      class supports is missing either of the keys: 'positive' or 'negative'.

  """
  if len(locals()) < 2:
    raise TypeError('Too few arguments.')
  elif len(locals()) > 2:
    raise TypeError('Too many arguments.')
                                                                     
  if any(k not in cost_matrix for k in ('TP', 'TN', 'FP', 'FN')):
    raise KeyError('A cost is missing from the passed cost matrix.')

  for child_class_supports in class_supports:
    if any(k not in child_class_supports for k in ('positive', 'negative')):
      raise KeyError('Class supports missing either positive or negative key.')

  child_expected_costs = []
  for supports in class_supports:
    num_positive = supports['positive']
    num_negative = supports['negative']
    child_cost = expected_cost(num_positive, num_negative, cost_matrix)
    child_expected_costs.append(child_cost)

  return sum(child_expected_costs)

def expected_cost_per_record(num_positive, num_negative, cost_matrix):
  """Used to calculate the expected cost per data point.

  Args:
    num_positive (int): The number of positive data points.
    num_negative (int): The number of negative data points.
    cost_matrix (dict): Every cost. e.g., {'TP':1, 'TN':0, 'FP':1, 'FN':5}

  Returns:
    (num): The expected cost per data point.

  Raises:
    TypeError: If an incorrect number of arguments are passed.
    KeyError: If the passed cost_matrix is missing a cost.

  """
  if len(locals()) < 3:
    raise TypeError('Too few arguments.')
  elif len(locals()) > 3:
    raise TypeError('Too many arguments.')
                                                                     
  if any(k not in cost_matrix for k in ('TP', 'TN', 'FP', 'FN')):
    raise KeyError('A cost is missing from the passed cost matrix.')

  expected_cost_all = expected_cost(num_positive, num_negative, cost_matrix)
  num_data_points = num_positive + num_negative

  return expected_cost_all / num_data_points
