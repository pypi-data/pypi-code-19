import requests, json, pandas, io, ast, urllib, webbrowser
	
_map_url = "http://alanlucero.kissr.com/feeds.csv"
_ver_url = "http://alanlucero.kissr.com/latestVer.txt"
_content = requests.get(_map_url).content
_feedmap = pandas.read_csv(io.StringIO(_content.decode('utf-8')))
_instructions = 'http://infrontfinance.com/support-downloads/infront-desktop-api-for-python'
_latestVer = urllib.request.urlopen(_ver_url)
_latestVer = _latestVer.read()
_latestVer = _latestVer.decode('utf-8')
_localVer = "1.0.8"

# Version check
def ToInstructions():
	print("There is a new version of Infront Desktop API. Would you like to upgrade to version " + _latestVer + "?")
	answer = input("(y/n):")
	if answer == "y":
		webbrowser.open(_instructions)
	else:
		pass

def VersionUpdate():
	latest_major, latest_minor, latest_patch = _latestVer.split('.')
	local_major, local_minor, local_patch = _localVer.split('.')

	if latest_major > local_major:
		ToInstructions()

	elif latest_major == local_major:
		if latest_minor > local_minor:
			ToInstructions()
		elif latest_minor == local_minor:
			if latest_patch > local_patch:
				ToInstructions()
	else:
		pass

# User credentials
def InfrontConnect(user,password):
	#version control
	VersionUpdate()
	global _username
	_username = user
	global _password
	_password = password
	print('\n Connected to Infront Desktop API for Python 3 version ' + _localVer)
	print('**Disclaimer** \n End-User agrees not to redistribute any such Information and to comply with any \n restrictions placed on such information by the providers thereof, hereunder but \n not limited to acceptance of and compliance with Data Providers’ and/or other \n third party license agreements. \n Customer agrees to indemnify and keep indemnified Infront and its affiliates harmless \n from and against any loss, damage, liability, cost, charges and expenses, including \n reasonable legal fees, arising out of any breach on part of Customer with respect to \n its obligations to obtain prior approvals from appropriate Data Providers and to \n comply with any applicable, conditions, restrictions, or limitations imposed by such \n Data Providers. ')

# Converts user input string to feed and ticker
def FeedParser(string):
	feed_id,_ = string.split(':')
	feednu = int(_feedmap['feednu'][_feedmap['feedcode'] == feed_id])
	return feednu

def TickerParser(string):
	_,ticker_id = string.split(':')
	return ticker_id

def ListToJSON(string):
	_instruments = []
	for inst in string:
		_dict =  {"ticker": TickerParser(inst),"feed": FeedParser(inst)}
		_instruments.append(_dict)

	return _instruments

#GetHistory(["OSS:STL"],["LAST"],"2017-01-13","2017-01-18")
def GetHistory(tickers,fields,start_date,end_date):

	if type(tickers) is not list:
		raise ValueError('You need to input a feed and market symbol as a list with items of type string. \n E.g. ["LSE:AAL","OSS:STL"]')
	if type(fields) is not list:
		raise ValueError('Fields inputs must be of a list with items of type string. \n E.g. ["last","volume","turnover"]')
	if type(start_date) is not str:
		raise ValueError("'start_date' input must be a string in the format 'YYYY-MM-DD' ")
	if type(end_date) is not str:
		raise ValueError("'end_date' input must be a string in the format 'YYYY-MM-DD' ")

	numItems = len(tickers)
	for items in range(len(fields)):
		if fields[items] == 'volume':
			fields[items] = 'prev_volume'
	
	fields.append('date')

	req_payload = {
  "user": _username,
  "password": _password,
  "context": "user specific context",
	  "historical_request": {
		"fields": fields,
		"start_date": start_date,
		"end_date": end_date,
		"instruments": ListToJSON(tickers)
	  }
	}

	req_post = requests.post("https://eod.infrontservices.com/historical/requests", json = req_payload, verify = True).text
	req_resp = dict(ast.literal_eval(req_post))
	req_url = req_resp['historical_response']['full_response_url']
	req_get = requests.get(req_url).text
	req_dic = ast.literal_eval(req_get)

	while req_dic['error_code'] != 0:
		if req_dic['error_code'] == 1:
			req_get = requests.get(req_url).text
			req_dic = ast.literal_eval(req_get)

		elif req_dic['error_code'] > 1:
			print('**ERROR 10** \n Potential reasons: \n 1) Invalid syntax in the GetHistory() request \n  2) API access not granted .')

		else:
			break

	hist_data = req_dic['historical_data']

	out = {}
	for item in range(numItems):
		
		fetch = hist_data[item]
		name = fetch['ticker']
		unpack = fetch['historical_trades']
		data = pandas.DataFrame(unpack)
		data.set_index('date',inplace = True)

		out.update({name:data})

	return out

#ToMatrixFrom(MySymbols,field) / MySymbols = dict of DFs / field = string, e.g. "last"

def ToMatrixForm(MySymbols, field):
	firstItem = next(iter(MySymbols))
	base = MySymbols[firstItem][field].rename(firstItem)
	skip = base.name
	for key in MySymbols:
		if key != skip:
			toAdd = MySymbols[key][field].rename(key)
			base = pandas.concat([base,toAdd], axis = 1, join = 'inner')
	return base
