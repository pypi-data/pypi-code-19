from django.db import models
from django.conf import settings
from django.contrib.sites.models import Site
from django.template.defaultfilters import slugify
from mmogo.core.category.models import Category, Tag
from mmogo.core.constants import DEFAULT_STATUS
from django_countries.fields import CountryField
from mmogo.core.models import BaseModel

class Company(BaseModel, models.Model):
	website = models.CharField(
		max_length=200, 
		blank=True, 
		null=True,
		help_text=""
	)
	email = models.CharField(
		max_length=200, 
		blank=True, 
		null=True,
		help_text=""
	)
	facebook = models.CharField(
		max_length=200, 
		blank=True, 
		null=True,
		help_text=""
	)
	twitter = models.CharField(
		max_length=200, 
		blank=True, 
		null=True,
		help_text=""
	)
	linkedin = models.CharField(
		max_length=200, 
		blank=True, 
		null=True,
		help_text=""
	)
	blog = models.CharField(
		max_length=20, 
		blank=True, 
		null=True,
		help_text=""
	)
	physical_address = models.TextField(
		blank=True, 
		null=True,
		help_text=""
	)
	postal_address = models.TextField(
		blank=True, 
		null=True,
		help_text=""
	)
	founded = models.CharField(
		max_length=50, 
		blank=True, 
		null=True,
		help_text=""
	)
	city = models.CharField(
		max_length=20, 
		blank=True, 
		null=True,
		help_text=""
	)
	province = models.CharField(
		max_length=20, 
		blank=True, 
		null=True,
		help_text=""
	)
	country = CountryField(
		blank_label='(Select Country)'
	)
	can_follow = models.BooleanField(default=False)
	follow_disabled = models.BooleanField(default=False)

	class Meta:
		abstract = True

	def __str__(self):
		if self.subtitle:
			return %s + ' - ' + %s % (self.title, self.subtitle)
		else:
			return %s % (self.title)
