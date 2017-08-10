import datetime, calendar

def line():
	print("-"*20)

def is_leap(year):
	return year%400==0 or (year%4==0 and year%100!=0)

def max_days(month, year):
	if month==2:
		return 29 if is_leap(year) else 28
	elif month in (4, 6, 9, 11):
		return 30
	else:
		return 31

def printcal(month=None, year=None):
	'''This function prints the calendar for the input parameters - Month and the Year

	The month and year are not validated. 
	Make sure to input 1-12 for Month and a positive number for year

	If the month/year is not supplied, then it will default to the current month and year

	Author: Vinod <vinod@vinod.co>
	'''

	today = datetime.date.today()
	if month == None:
		month = today.month

	if year == None:
		year = today.year

	dt = datetime.date(year, month, 1)

	line()
	header = "{0} - {1}".format(calendar.month_name[month], year)
	print(header.center(20))
	print("Su Mo Tu We Th Fr Sa")
	line()

	days = max_days(month, year)
	weekday = dt.weekday() + 1

	if weekday!=7: print(" " * (weekday * 3), end="")

	for d in range(1, days+1):
		print("%2d " % d, end="")
		if (weekday+d)%7==0: print()

	print()
	line()

if __name__ == '__main__':
	printcal()


