# Should add commas and a space if necessary, remove if unnecessary.
def soft_comma(item1, item2):
	if item1[-1] == ',':
		item1 = item1[:-1]
	
	if item2[0] == ',':
		item2 = item2[1:]

	return item1 + ', ' + item2
	