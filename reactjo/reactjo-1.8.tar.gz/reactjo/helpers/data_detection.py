def get_type(string):
	curly = string.find('{')
	square= string.find('[')
	paren = string.find('(')
	types = [curly, square]
	existing_types = []
	
	for t in types:
		if t != -1:
			existing_types.append(t)
			type_pos = sorted(existing_types)
			typ = string[type_pos[0]]

	opposites = {'{':'}','[':']', '(':')'}
	opposite = opposites[typ]
	
	return {
		'typ': typ,
		'opposite': opposite,
		'index': type_pos[0]
	}

def get_brackets(string, start = 0):
	typ = get_type(string[start:])
	block_start = start + typ['index']
	
	pos = block_start

	depth = 0
	while depth != -1:
		closing = string.find(typ['opposite'], pos + 1)
		child   = string.find(typ['typ']     , pos + 1)

		if child == -1:
			depth -= 1
			pos = closing
		elif child < closing:
			depth += 1
			pos = child
		else:
			depth -= 1
			pos = closing

	return { 'start': block_start, 'stop': pos }

def list_index_positions(string, start, stop):
	li = string[start:stop]
	positions = []
	quoted = False
	nested = 0
	
	for i, c in enumerate(li):
		# ignore commas in strings
		if c in ['"', "'"]:
			quoted = not quoted

		# find child elements
		elif c in ['[','{','('] and len(positions) > 0:
			nested += 1
		elif c in [']','}',')']:
			nested -= 1

		# this is index 0
		elif c == '[' and len(positions) == 0:
			positions.append(i + start + 1)
		# add any remaining indices detected.
		elif c == ',' and quoted == False and nested <= 0:
			positions.append(i + start + 1)

	return positions

def detect_duplicate(target, content):
	raw_compare = target.find(content) != -1
	if raw_compare:
		return True
	else:
		clean_content = (content
			.replace('\n','')
			.replace('\t','')
			.replace(',','')
			.replace(' ','')
			.replace('"','')
			.replace("'",""))

		return target.find(clean_content) != -1