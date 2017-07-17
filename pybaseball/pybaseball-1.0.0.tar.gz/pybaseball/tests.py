import statcast

try:
	statcast.get_statcast() # no date args
	statcast.get_statcast('2017-06-06') # one date arg
	order_one = statcast.get_statcast('2017-06-06', '2017-06-10') # two date args
	order_two = statcast.get_statcast('2017-06-10', '2017-06-06')

	try: # this one SHOULD fail
		statcast.get_statcast('2016-26-06', '2016-28-06') # two improperly formatted date strings
		statcast.get_statcast('2016-26-06') # one improperly formatted date string
		print("Something failed with statcast.get_statcast()")
	except:
		pass

	print("Statcast passes all tests")

except:
	print("Something failed with statcast.get_statcast()")


import league_batting_stats
try:
	#make sure it works with no input (should return most recent date or season's data)
	league_batting_stats.batting_stats()
	league_batting_stats.batting_stats_range()
	#make sure range works with just one date provided (should give data from date 1 to date 1)
	league_batting_stats.batting_stats_range('2015-08-08')
	#range should work
	league_batting_stats.batting_stats_range('2015-08-08', '2015-08-15')
	#same w/ reversed range
	league_batting_stats.batting_stats_range('2015-08-15', '2015-08-08')
	#make sure bad datestrings raise errors:
	try:
		league_batting_stats.batting_stats_range('2015-18-08', '2015-19-08')
		print("batting code failed to catch bad datestrings")
	except:
		pass
	print("batting stats passes all tests")
except:
	print("batting stats fails at least one test")

import league_pitching_stats
try:
	#make sure it works with no input (should return most recent date or season's data)
	league_pitching_stats.pitching_stats()
	league_pitching_stats.pitching_stats_range()
	#make sure range works with just one date provided (should give data from date 1 to date 1)
	league_pitching_stats.pitching_stats_range('2015-08-08')
	#range should work
	league_pitching_stats.pitching_stats_range('2015-08-08', '2015-08-15')
	#same w/ reversed range
	league_pitching_stats.pitching_stats_range('2015-08-15', '2015-08-05')
	#make sure bad datestrings raise errors:
	try:
		league_pitching_stats.pitching_stats_range('2015-18-08', '2015-19-08')
		print("pitching code failed to identify bad datestrings")
	except:
		pass
	print("pitching stats passes all tests")
except:
	print('pitching stats fails at least one tests')
