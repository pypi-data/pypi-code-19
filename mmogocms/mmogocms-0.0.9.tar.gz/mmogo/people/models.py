from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.template.defaultfilters import slugify
from django_countries.fields import CountryField

SECURITY_QUESTION_CHOICES = (
	('first_pet_name', 'What was the name of your first pet?'),
)

class Profile(models.Model):
    	user = models.OneToOneField(User)
    	other_name = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        help_text=""
    )
    	about = models.TextField(
        blank=True,
        null=True,
        help_text=""
    )
    	employer = models.CharField(
		max_length=200,
		blank=True,
		null=True,
		help_text=""
	)
    	position = models.CharField(
		max_length=200,
		blank=True,
		null=True,
		help_text=""
	)
    	gender = models.CharField(
		max_length=200,
		blank=True,
		null=True,
		help_text=""
	)
    	ethnicity = models.CharField(
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
		max_length=200,
		blank=True,
		null=True,
		help_text=""
	)
    	image = models.CharField(
		max_length=200,
		blank=True,
		null=True,
		help_text=""
	)
    	cover_image = models.CharField(
		max_length=200,
		blank=True,
		null=True,
		help_text=""
	)
	mobile = models.CharField(
		max_length=20,
		blank=True,
		null=True,
		help_text=""
	)
	email_activation_code = models.TextField(
        blank=True,
        null=True,
        help_text=""
    )
	mobile_activation_code = models.CharField(
		max_length=100,
        blank=True,
        null=True,
        help_text=""
    )
	two_facter_enabled = models.BooleanField(default=False)
	security_question = models.CharField(
		max_length=100,
        blank=True,
        null=True,
        help_text="",
		choices=SECURITY_QUESTION_CHOICES
    )
	security_question_answer = models.CharField(
		max_length=100,
        blank=True,
        null=True,
        help_text=""
    )
    	def __str__(self):
        	return self.user.first_name + ' ' + self.user.last_name