def invert_dict(dictionary):
	new_dict = {}
	for key in dictionary:
		new_dict[dictionary[key]] = key

	return new_dict


def merge_dicts(*dictionaries, **kwargs):
	"""
	Merge an arbitrary number of dictionaries, in such a way that values found
	in dictionaries that appear earlier in the parameter list take precedence.

	If the only kwarg ``recursive`` is True, then sub-dictionaries are merged
	in the same way, otherwise a dictionary-valued entries completely overwrite
	one another.
	"""
	recursive = kwargs.pop('recursive', True)
	if recursive:
		return merge_dicts_recursive(*dictionaries)
	return merge_dicts_nonrecursive(*dictionaries)


def merge_dicts_nonrecursive(*dictionaries):
	"""
	Merge an arbitrary number of dictionaries, in such a way that values found
	in dictionaries that appear earlier in the parameter list take precedence.
	Note that sub-dictionaries are treated as simple values -- the
	sub-dictionary that takes precedence completely overwrites the other(s),
	rather than being recursively merged.
	"""
	merged = {}
	for dictionary in reversed(dictionaries):
		merged.update(dictionary)
	return merged


def merge_dicts_recursive(*dictionaries):
	"""
	Merge an arbitrary number of dictionaries, in such a way that values found
	in dictionaries that appear earlier in the parameter list take precedence.
	Note that sub-dictionaries are recursively merged in the same way.
	"""
	merged = {}
	for dictionary in reversed(dictionaries):
		for key in dictionary:

			# If this key corresponds to a sub-dictionary, both within the
			# merged dict so far and in the current dict to merge in, then we
			# recurse, so that those sub-dicts are merged well 
			both_vals_are_dicts = (
				key in merged and isinstance(merged[key], dict) 
				and isinstance(dictionary[key], dict)
			)

			if both_vals_are_dicts:
				merged[key] = merge_dicts(dictionary[key], merged[key])

			else:
				merged[key] = dictionary[key]

	return merged


def dzip(*dictionaries):
	'''
	Like zip, but for dictionaries.  Produce a dictionary whose keys are 
	given by the intersection of input dictionaries' keys, and whose
	values are are tuples of the input dicts corresponding values.
	'''

	# Define the dzip of no dictionaries to be an empty dictionary
	if len(dictionaries) == 0:
		return {}

	# Get the keys common to all dictionaries
	keys = set(dictionaries[1])
	for d in dictionaries[1:]:
			keys &= set(d)

	# Make the zipped dictionary
	return {
		key : tuple([d.get(key, None) for d in dictionaries])
		for key in keys
	}


def select(dictionary, fields, require=True):
    """
    Create a new dict by copying selected `fields` from the original
    dict `dictionary`.  If `require` is True, then a field that doesn't exist
    in the original dict will cause a KeyError; otherwise it passes over
    missing keys
    silently.
    """
    new_dict = {}
    for field in fields:
        try:
            new_dict[field] = dictionary[field]
        except KeyError:
            if require:
                raise

    return new_dict

