'''By default the function returns desktop user agents
	Arguments:
	type = "mobile" to get mobile useragents
'''
import json
import random
ua = json.load(open('useragents.json'))

def get_ua(type='web'):		
	print(random.choice(ua[type]))
	return random.choice(ua[type])