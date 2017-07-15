from __future__ import unicode_literals

from django.db import models
from multiselectfield import MultiSelectField

class MetaImage(models.Model):
    image_alt = models.CharField(max_length=255)
    image_title = models.CharField(max_length=255)
    image_url = models.CharField(max_length=255)
    class Meta:
            verbose_name = 'Meta Image'
            verbose_name_plural = 'Meta Image'

class SiteInformation(models.Model):
    site_name = models.CharField(max_length=255)
    site_slogan = models.CharField(max_length=255)
    email_id = models.CharField(max_length=255)
    logo_image_alt_text = models.CharField(max_length=255)
    class Meta:
            verbose_name = 'Site Information'
            verbose_name_plural = 'Site Information'

class OpenGraph(models.Model):
    CONTENT_DETERMINER = (
    ('ignore','Ignore'),
    ('automatic','Automatic'),
    ('an','An'),
    ('a','A'),
    ('the','The'),
    )
    site_name = models.CharField(max_length=255)
    content_type = models.CharField(max_length=255)
    page_url = models.CharField(max_length=255)
    content_title = models.CharField(max_length=255)
    content_description = models.TextField()
    content_title_determiner = models.CharField(choices=CONTENT_DETERMINER, max_length=255)
    content_modification_date_time = models.DateTimeField()
    see_also = models.CharField(max_length=255)
    image = models.ImageField(help_text="Image for OpenGraph")
    image_url = models.CharField(max_length=255)
    secure_image_url = models.CharField(max_length=255)
    image_type = models.CharField(max_length=255)
    image_width = models.CharField(max_length=255)
    image_height = models.CharField(max_length=255)
    logitude = models.CharField(max_length=255)
    latitude = models.CharField(max_length=255)
    street_number = models.CharField(max_length=255)
    locality = models.CharField(max_length=255)
    region = models.CharField(max_length=255)
    zip_code = models.CharField(max_length=255)
    email = models.EmailField(max_length=255)
    phone_number = models.CharField(max_length=255)
    fax_number = models.CharField(max_length=255)
    class Meta:
            verbose_name = 'Open Graph'
            verbose_name_plural = 'Open Graph'

class GoogleVerification(models.Model):
    meta_tag = models.CharField(max_length=255)
    file_upload = models.FileField()
    verification_file = models.CharField(max_length=255)
    verification_file_content = models.CharField(max_length=255)
    class Meta:
            verbose_name = 'Google Verification'
            verbose_name_plural = 'Google Verification'

class BingVerification(models.Model):
    meta_tag = models.CharField(max_length=255)
    file_upload = models.FileField()
    verification_file = models.CharField(max_length=255)
    verification_file_content = models.CharField(max_length=255)
    class Meta:
            verbose_name = 'Bing Verification'
            verbose_name_plural = 'Bing Verification'

class BasicTags(models.Model):
    meta_title = models.CharField(max_length=255)
    meta_description = models.TextField()
    meta_keywords = models.TextField()
    class Meta:
            verbose_name = 'Basic Tags'
            verbose_name_plural = 'Basic Tags'

class AdvancedTags(models.Model):
    META_ROBOT = (
    ('Allow search engines to index this page (assumed).', 'Allow search engines to index this page (assumed).'),
    ('Allow search engines to follow links on this page (assumed).', 'Allow search engines to follow links on this page (assumed).'),
    ('Prevents search engines from indexing this page.', 'Prevents search engines from indexing this page.'),
    ('Prevents search engines from following links on this page.', 'Prevents search engines from following links on this page.'),
    ('Prevents cached copies of this page from appearing in search results.', 'Prevents cached copies of this page from appearing in search results.'),
    ('Prevents descriptions from appearing in search results, and prevents page caching.', 'Prevents descriptions from appearing in search results, and prevents page caching.'),
    ('Blocks the Open Directory Project description from appearing in search results.', 'Blocks the Open Directory Project description from appearing in search results.'),
    ('Prevents Yahoo! from listing this page in the Yahoo! Directory.', 'Prevents Yahoo! from listing this page in the Yahoo! Directory.'),
    ('Prevent search engines from indexing images on this page.', 'Prevent search engines from indexing images on this page.'),
    ('Prevent search engines from offering to translate this page in search results.', 'Prevent search engines from offering to translate this page in search results.'),
    ('Provides search engines with specific directions for what to do when this page is indexed.', 'Provides search engines with specific directions for what to do when this page is indexed.')
    )
    CONTENT_RATING = (
    ('none', 'None'),
    ('general', 'General'),
    ('mature', 'Mature'),
    ('restricted', 'Restricted'),
    ('14 years or older', '14 years or older'),
    ('safe for kids', 'Safe for kids')
    )
    REFERRER_POLICY = (
    ('none', 'None'),
    ('no referrer', 'No Referrer'),
    ('origin', 'Origin'),
    ('No Refrerer when downgrade', 'No Refrerer when downgrade'),
    ('origin when cross origin', 'Origin when cross origin'),
    ('unsafe url', 'Unsafe Url')
    )
    REVISIT_AFTER = (
    ('none','None'),
    ('days','Days'),
    ('weeks', 'Weeks'),
    ('months', 'Months'),
    ('years', 'Years')
    )
    meta_robot = MultiSelectField(choices=META_ROBOT, max_length=255)
    news_keywords = models.CharField(max_length=255)
    standout = models.CharField(max_length=255)
    content_rating = models.CharField(choices=CONTENT_RATING, max_length=255)
    referrer_policy = models.CharField(choices=REFERRER_POLICY, max_length=255)
    generator = models.CharField(max_length=255)
    rights = models.CharField(max_length=255)
    image = models.ImageField(max_length=255)
    shortlink_url = models.CharField(max_length=255)
    original_source = models.CharField(max_length=255)
    previous_page_url = models.CharField(max_length=255)
    next_page_url = models.CharField(max_length=255)
    content_language = models.CharField(max_length=255)
    geo_position = models.CharField(max_length=255)
    geo_place_name = models.CharField(max_length=255)
    geo_region = models.CharField(max_length=255)
    icbm = models.CharField(max_length=255)
    refresh = models.CharField(max_length=255)
    revisit_after_interval = models.CharField(choices=REVISIT_AFTER, max_length=255)
    pragma = models.CharField(max_length=255)
    cache_control = models.CharField(max_length=255)
    expires = models.CharField(max_length=255)
    class Meta:
            verbose_name = 'Advanced Tags'
            verbose_name_plural = 'Advanced Tags'
