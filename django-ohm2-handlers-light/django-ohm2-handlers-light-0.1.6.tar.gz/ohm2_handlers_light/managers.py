from django.db import models
from . import utils as h_utils


class OHM2HandlersLightManager(models.Manager):
	
	def create(self, *args, **kwargs):
		if kwargs.get("identity") is None:
			kwargs["identity"] = h_utils.db_unique_random(self.model)
		return super(OHM2HandlersLightManager, self).create(*args, **kwargs)
	
	def save(self, *args, **kwargs):
		print(args, kwargs)
		return super(OHM2HandlersLightManager, self).save(*args, **kwargs)