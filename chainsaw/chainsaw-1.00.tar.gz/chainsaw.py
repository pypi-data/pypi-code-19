"""chainsaw.py : Decision Tree Splitting Functions

This module can be used to find the best split for some data based on several
splitting criteria. It is mainly intended for use in machine learning
algorithms.

"""
import wattle
import entro
import datacost as dc

def gain_ratio_split(node, minimum_records):
  """Finds and returns the best split based on gain ratio.
  
  Args:
    node (wattle.Node): The node to calculate the best split for.
    minimum_records (Number): The minimum number of child records.

  Returns:
    (wattle.Split_Test): The best split based on gain ratio.

  """

  # These values will get updated if a better split is found.
  best_gain_ratio = 0
  best_split = None

  # Get the support values for the passed node. This is used to measure the
  # original entropy. The entro module requires the supports to be a list, not
  # a dict. It also requires the removal of zero-values for supports. 
  parent_supports = node.class_supports
  parent_supports = [x for x in parent_supports.values() if x != 0]

  # Iterate over every possible split.
  for split in node.get_possible_splits():

    # Get the class support counts for each resulting child.
    temp_node = node # This temp node gets split.
    child_support_dicts = temp_node.get_split_supports(split_test = split)
    child_supports = [list(x.values()) for x in child_support_dicts]
    if any(sum(supports) < minimum_records for supports in child_supports):
      continue

    # The entro module requires the zero support values to be removed.
    for i in range(len(child_supports)):
      child_supports[i] = [x for x in child_supports[i] if x != 0]

    # Calculate the gain ratio for this split. If it's better than the best so
    # far, update the best split to be this split.
    gain_ratio = entro.gain_ratio(child_supports, parent_supports)
    if gain_ratio > best_gain_ratio:
      best_gain_ratio = gain_ratio
      best_split = split

  if best_gain_ratio > 0:
    return best_split
  else:
    return None

def cost_reduction_split(node, positive_class, cost_matrix):
  """Finds and returns the best split based on expected cost.

  Args:
    node (wattle.Node): The node to calculate the best split for.
    positive_class (string): The name of the class which is the positive class.
    cost_matrix (dict): The cost matrix represented like: {'TP':1,'TN':0} etc.

  Returns:
    (wattle.Split_Test): The best split based on expected cost.

  """
  # Calculate the expected cost of the parent.
  num_positive = node.num_positive()
  num_negative = node.num_negative()
  parent_cost = dc.expected_cost(num_positive, num_negative, cost_matrix)

  # These values will get updated if a better split is found.
  best_cost = float('inf')
  best_split = None

  # Iterate over every possible split.
  for split in node.get_possible_splits():

    # Get the class support counts for each resulting child.
    child_supports = node.get_split_supports(split, posneg=True)

    # If the cost of this split is better than the current best, update the
    # current best split to be this split.
    split_cost = dc.expected_cost_after_split(child_supports, cost_matrix)
    if split_cost < best_cost:
      best_cost = split_cost
      best_split = split
  
  if best_cost < parent_cost:
    return best_split
  else:
    return None
