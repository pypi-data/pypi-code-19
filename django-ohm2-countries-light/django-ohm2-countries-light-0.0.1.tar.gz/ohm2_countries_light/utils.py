from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.translation import ugettext as _
from django.db.models import Q
from ohm2_handlers_light import utils as h_utils
from ohm2_handlers_light.definitions import RunException
from . import models as ohm2_countries_light_models
from . import errors as ohm2_countries_light_errors
from . import settings
import os, time, random


random_string = "Re4Wwe69YRenGntPO8ADErMBs1Y4hCLQ"

	

def create_country(name, official_name, alpha_2, alpha_3, numeric, **kwargs):
	kwargs["name"] = name.strip().title()
	kwargs["official_name"] = official_name.strip().title()
	kwargs["alpha_2"] = alpha_2.strip()
	kwargs["alpha_3"] = alpha_3.strip()
	kwargs["numeric"] = numeric

	flag_small = kwargs.get("flag_small")
	if flag_small:
		kwargs["flag_small"] = process_country_flag_small_image(flag_small)	
		
	return h_utils.db_create(ohm2_countries_light_models.Country, **kwargs)

def process_country_flag_small_image(image, **kwargs):
	split = image.rsplit(".", 1)
	if len(split) != 2:
		return image

	filename, extension = split[0].strip(), split[1].strip().lower()

	if extension == "png":
		suffix, format, mime = ".png", "PNG", "image/png"

	else:
		suffix, format, mime = ".jpg", "JPEG", "image/jpg"

	info = {
		"max_width": 48,
		"max_height": 48,
		"suffix": suffix,
		"format": format,
		"mime": mime,
		"quality": 95,
	}
	return h_utils.process_uploaded_image(image, **info)

def get_country(**kwargs):
	return h_utils.db_get(ohm2_countries_light_models.Country, **kwargs)

def get_or_none_country(**kwargs):
	return h_utils.db_get_or_none(ohm2_countries_light_models.Country, **kwargs)

def filter_country(**kwargs):
	return h_utils.db_filter(ohm2_countries_light_models.Country, **kwargs)		


def update_country(country, **kwargs):
	params = {}

	flag_small = kwargs.get("flag_small")
	if flag_small:
		params["flag_small"] = process_country_flag_small_image(flag_small)	

	return h_utils.db_update(country, **params)

