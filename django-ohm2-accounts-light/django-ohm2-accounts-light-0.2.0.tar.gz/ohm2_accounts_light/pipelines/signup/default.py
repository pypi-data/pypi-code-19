from ohm2_accounts_light import utils as ohm2_accounts_light
import os


def default(request, user, username, email, password, previous_outputs, *args, **kwargs):
	output = {}
	
	output["authtoken"] = ohm2_accounts_light.get_or_create_authtoken(user)
	
	return (user, output)
