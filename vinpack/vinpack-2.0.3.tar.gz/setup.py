import setuptools

setuptools.setup(
	name = "vinpack",
	version = "2.0.3",
	packages = ["vinpack"],
	package_dir = {"vinpack": "./vinpack"},
	license = "MIT",
	author = "Vinod",
	maintainer = "Vinod",
	author_email = "vinod@vinod.co",
	maintainer_email = "vinod@vinod.co",
	url = "http://vinod.co",
	description = "The module vinpack.dateutils has a print_cal() function along with few other.",
	long_description = """The package vinpack has only one module 'dateutils' with the following members:

is_leap(year)
	-> returns True/False for a leap year/ non-leap year

max_days(month, year)
	-> returns the maximum number of days in the given month of the year

printcal(month=None, year=None)
	-> prints the calendar for the given month and year
	-> prints the calendar for current month/year if not specified"""
	

	)