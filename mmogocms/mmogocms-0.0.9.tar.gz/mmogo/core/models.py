from django.db import models
from django.conf import settings
from django.contrib.sites.models import Site
from django.template.defaultfilters import slugify
from mmogo.core.categories.models import Category, Tag


class BaseModel(models.Model):
	title = models.CharField(
		max_length=200,
		help_text=""
	)
	slug = models.SlugField()
	subtitle = models.CharField(
		max_length=200, 
		blank=True, 
		null=True, 
		help_text=""
	)
	description = models.TextField(
		blank=True, 
		null=True
	)
	category = models.ManyToManyField(
		Category, 
		blank=True, 
		null=True, 
		help_text=""
	)
	tags = tags = TaggableManager(
		blank=True
	)
	image = models.ImageField(
		blank=True,
        null=True,
	)
	image_source = models.CharField(
		max_length=200,
		blank=True,
		null=True,
		help_text=""
	)
	sites = models.ManyToManyField(
		Site,
		blank=True,
		null=True,
		help_text=""
	)
	owner = models.ForeignKey(
		settings.AUTH_USER_MODEL, 
		related_name='%(app_label)s_%(class)s_user',
		editable=False
	)
	created_at = models.DateTimeField(
		auto_now_add=True,
		editable=False
	)
	updated_at = models.DateTimeField(
		auto_now=True,
		editable=False
	)
	status = models.IntegerField(default=constants.DEFAULT_STATUS)
	can_comment = models.BooleanField(default=False)
	anonymous_comment = models.BooleanField(default=False)
	comment_disabled = models.BooleanField(default=False)
	like_enabled = models.BooleanField(default=False)
	anonymous_like = models.BooleanField(default=False)
	like_disabled = models.BooleanField(default=False)
	future_publish = models.DateTimeField(        
		blank=True,
        null=True,
	)
	future_unpublish = models.DateTimeField(        
		blank=True,
        null=True,
	)
	
	def save(self, *args, **kwargs):
		if self.site is None:
			self.sites = Site.objects.get_current()
		self.slug = slugify(self.title)
		super(BaseModel, self).save(*args, **kwargs)

	class Meta:
		abstract = True

	def __str__(self):
		if self.subtitle:
			return self.title + ' - ' + self.subtitle
		else:
			return '%s' % (self.title)
