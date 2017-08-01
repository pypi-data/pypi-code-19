from django.core.management.base import BaseCommand, CommandError
from ohm2_handlers_light import utils as h_utils
from ohm2_countries_light import utils as ohm2_countries_light_utils
from ohm2_countries_light import settings
from collections import defaultdict
import os, pycountry

class Command(BaseCommand):
	
	def add_arguments(self, parser):
		pass #parser.add_argument('-f', '--foo')

	def handle(self, *args, **options):
		# foo = options["foo"]
		
		"""
		files = defaultdict(dict)
		sizes = ["16", "24", "32", "48"]

		
		for c in pycountry.countries:

			alpha_2 = c.alpha_2.lower()
			name = c.name
			
			files[name] = defaultdict(dict)
			for size in sizes:
				files[name][size] = True


			for size in sizes:
				size_dst_path = os.path.join(settings.FLAGS_BASE_PATH, size, alpha_2 + ".png")	

				files[name][size] &= os.path.isfile(size_dst_path)

		
		
		all_around = []
		not_around = []
		for country, sizes in files.items():
			all_exist = True
			for v in sizes.values():
				all_exist &= v
			

			print(country, sizes)	



			if all_exist:
				all_around.append(country)
			else:
				not_around.append(country)

		print(sorted(all_around))
		"""


		"""
		
		files = defaultdict(dict)
		
		
		for c in pycountry.countries:

			alpha_2 = c.alpha_2.lower()
			name = c.name
			
			files[name] = defaultdict(bool)

			dst_path = os.path.join("/Users/tonra/Downloads/flags-normal", alpha_2 + ".png")
			files[name] = os.path.isfile(dst_path)
			print(dst_path)
		
		
		all_around = []
		not_around = []
		for country, exist in files.items():
			if exist:
				all_around.append(country)
			else:
				not_around.append(country)

		print(sorted(not_around), len(not_around))

		"""

		files = defaultdict(dict)
		
		
		for c in pycountry.countries:

			alpha_2 = c.alpha_2.lower()
			name = c.name
			
			files[name] = defaultdict(bool)

			dst_path = os.path.join(settings.FLAGS_BASE_PATH, alpha_2 + ".png")
			files[name] = os.path.isfile(dst_path)
		
		
		all_around = []
		not_around = []
		for country, exist in files.items():
			if exist:
				all_around.append(country)
			else:
				not_around.append(country)

		print(sorted(not_around), len(not_around))



			