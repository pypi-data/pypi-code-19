def print_lol(the_list):
	'''This is text'''
	for each_movie in the_list:
		if isinstance(each_movie, list):
			print_lol(each_movie)
		else:
			print(each_movie)