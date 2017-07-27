from ohm2_accounts_light import utils as ohm2_accounts_light_utils

def login(backend, user, response, *args, **kwargs):
	
	if backend.name == "facebook":
			
		if kwargs.get("is_new", False):

			pipeline_options = {}
			
			picture = response.get("picture", {})
			if picture:
				data = picture.get("data")
				url = data.get("url")	
				if url:
					pipeline_options["profile_url"] = url
		

			ohm2_accounts_light_utils.run_signup_pipeline(backend.strategy.request, user, **pipeline_options)

	
	return {}