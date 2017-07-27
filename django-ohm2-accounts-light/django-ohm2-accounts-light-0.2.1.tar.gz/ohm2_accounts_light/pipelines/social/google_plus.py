from ohm2_accounts_light import utils as ohm2_accounts_light_utils

def login(backend, user, response, *args, **kwargs):
	
	if backend.name == "google-oauth2":
		
		if kwargs.get("is_new", False):

			pipeline_options = {}
			
			image = response.get("image")
			if image:
				url = image.get("url")
				if url:
					print(url)

			ohm2_accounts_light_utils.run_signup_pipeline(backend.strategy.request, user, **pipeline_options)
		

	
	return {}