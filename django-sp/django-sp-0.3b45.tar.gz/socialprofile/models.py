# -*- coding: utf-8 -*-
"""
Alternative implementation of Django's authentication User model, which allows to authenticate against the OAuth.
This alternative implementation is activated by setting ``AUTH_USER_MODEL = 'socialprofile.SocialProfile'`` in
settings.py, otherwise the default Django or another implementation is used.
"""
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.db import models
from django.utils import timezone
from django.core.validators import RegexValidator
from django.core.mail import send_mail
from django.core.exceptions import ValidationError
from django.contrib.auth.validators import ASCIIUsernameValidator
from django.contrib.auth.models import BaseUserManager, PermissionsMixin, AbstractBaseUser
from django.contrib.auth.models import Group as BaseGroup
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _

from image_cropping.fields import ImageRatioField, ImageCropField

import logging
LOGGER = logging.getLogger(name='socialprofile.models')

class IntegerRangeField(models.IntegerField):
	def __init__(self, verbose_name=None, name=None, min_value=None, max_value=None, **kwargs):
		self.min_value, self.max_value = min_value, max_value
		models.IntegerField.__init__(self, verbose_name, name, **kwargs)
	def formfield(self, **kwargs):
		defaults = {'min_value': self.min_value, 'max_value':self.max_value}
		defaults.update(kwargs)
		return super(IntegerRangeField, self).formfield(**defaults)

class SocialProfileManager(BaseUserManager):
    use_in_migrations = True
 
    def get_by_natural_key(self, username):
		try:
			return self.get(username=username)
		except self.model.DoesNotExist:
			return self.get(is_active=True, email=username)
 
    def _create_user(self, email, password,
                     is_staff, is_superuser, **extra_fields):
        """
        Creates and saves a User with the given email and password.
		
		:param str email: user email
        :param str password: user password
        :param bool is_staff: whether user staff or not
        :param bool is_superuser: whether user admin or not
        :return socialprofile.models.SocialProfile user: user
        :raise ValueError: email is not set
		
        """
        now = timezone.localtime(timezone.now())
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email,
                          is_staff=is_staff, is_active=True,
                          is_superuser=is_superuser, last_login=now,
                          date_joined=now, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        """
        Create and save a SocialProfile with the given email and password.
        :param str email: user email
        :param str password: user password
        :return socialprofile.models.SocialProfile user: regular user
        """
        is_staff = extra_fields.pop("is_staff", False)
        return self._create_user(email, password, False, False,
                                 **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        return self._create_user(email, password, True, True,
                                 **extra_fields)

@python_2_unicode_compatible
class AbstractSocialProfile(AbstractBaseUser, PermissionsMixin):
    """
    Alternative implementation of Django's User model allowing to authenticate against the OAuth.
	
    Inherits from both the AbstractBaseUser and PermissionMixin.
    The following attributes are inherited from the superclasses:
        * password
        * last_login
        * is_superuser
    """
 
    username_validator = ASCIIUsernameValidator()    
	
    GENDER_CHOICES = (
        (_('male'), _('Male')),
        (_('female'), _('Female')),
        (_('other'), _('Other')),
        ('', '')
    )
	
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    username = models.CharField(_('Username'), max_length=30, unique=True, blank=False,
        help_text=_('Required. 30 characters or fewer. Letters, digits and @/./+/-/_ only.'),
        validators=[
            RegexValidator(
                r'^[\w.@+-]+$',
                _('Enter a valid username. This value may contain only '
                  'letters, numbers ' 'and @/./+/-/_ characters.')
            ),
        ],
        error_messages={
            'unique': _("A user with that username already exists."),
        },
    )
    first_name = models.CharField(verbose_name=_('First Name'), max_length=30, blank=True)
    last_name = models.CharField(verbose_name=_('Last Name'), max_length=30, blank=True)
    email = models.EmailField(verbose_name=_('Email Address'), unique=True, max_length=254, blank=False)
    is_staff = models.BooleanField(verbose_name=_('staff status'), default=False,
        help_text=_('Designates whether the user can log into this admin site.'))
    is_active = models.BooleanField(verbose_name=_('active'), default=True,
        help_text=_('Designates whether this user should be treated as active. Unselect this instead of deleting accounts.'))
    date_joined = models.DateTimeField(verbose_name=_('Date Joined'), auto_now_add=True)
    date_modified = models.DateTimeField(verbose_name=_('Date Updated'), auto_now=True)
 
    #status = models.ForeignKey(MembershipStatus, on_delete=models.SET_NULL, null=True, default=1)
    country = models.CharField(verbose_name=_("Country"), max_length=255, blank=True)
    gender = models.CharField(verbose_name=_("Gender"), max_length=10, blank=True, choices=GENDER_CHOICES)
    url = models.URLField(verbose_name=_("Homepage"), help_text=_("Where can we find out more about you?"), max_length=500, blank=True)
    image_url = models.URLField(verbose_name=_("Avatar Picture"), max_length=500, blank=True)
    image = ImageCropField(upload_to='user/', blank=True)
    cropping = ImageRatioField('image', '120x100', allow_fullsize=True)
    cropping_free = ImageRatioField('image', '300x300', free_crop=True, size_warning=True)
    description = models.TextField(verbose_name=_("Description"), help_text=_("Tell us about yourself!"), blank=True)
    manually_edited = models.BooleanField(verbose_name=_("Manually Edited"), default=False)
	
	# Add for Staff Infos
    sort = IntegerRangeField(verbose_name=_("Sort Order"), default=1, min_value=1, max_value=100000000, blank=True)
    visible = models.BooleanField(verbose_name=_("Visible in the Public Pages"), default=False, blank=True)
    title = models.CharField(verbose_name=_("Title"), max_length=500, blank=True)
    role = models.CharField(verbose_name=_("Role"), max_length=500, blank=True)
    function_01 = models.CharField(max_length=200, blank=True)
    function_02 = models.CharField(max_length=200, blank=True)
    function_03 = models.CharField(max_length=200, blank=True)
    function_04 = models.CharField(max_length=200, blank=True)
    function_05 = models.CharField(max_length=200, blank=True)
    function_06 = models.CharField(max_length=200, blank=True)
    function_07 = models.CharField(max_length=200, blank=True)
    function_08 = models.CharField(max_length=200, blank=True)
    function_09 = models.CharField(max_length=200, blank=True)
    function_10 = models.CharField(max_length=200, blank=True)

	# Add Info retrived by Providers
    editByGoogle = models.BooleanField(verbose_name=_("Google Edit User's Info"), default=False, blank=True)
    google_isPlusUser = models.BooleanField(verbose_name=_("Google Plus"), default=False, blank=True)
    google_plusUrl = models.URLField(verbose_name=_("Google Plus Page"), max_length=500, blank=True)
    google_circledByCount = models.IntegerField(verbose_name=_("Google Circle byCount"), default=0, blank=True)
    google_language = models.CharField(verbose_name=_("Google Language"), max_length=2, blank=True)
    google_kind = models.CharField(verbose_name=_("Google Kind"), max_length=2, blank=True)
    google_verified = models.BooleanField(verbose_name=_("Google Verified"), default=False, blank=True)
	
    objects = SocialProfileManager()
    	 
    class Meta(object):
        verbose_name = _("Social Profile")
        verbose_name_plural = _("Social Profiles")
        ordering = ['username']
        proxy = False
        abstract = True

    def save(self, *args, **kwargs):
        if not self.username:
            self.username = self.get_email()
        super(AbstractSocialProfile, self).save(*args, **kwargs)

    def __str__(self):
        return self.get_username()

    @models.permalink
    def get_absolute_url(self):
        return 'sp_profile_other_view_page', [self.username]

    def get_username(self):
        """Return the username"""
        if self.is_staff:
            return self.username
        return self.email or '<anonymous>'

    def get_email(self):
        """Return the email"""
        return self.email

    def get_full_name(self):
        """
        Returns the first_name plus the last_name, with a space in between else email
        """
        full_name = '%s %s' % (self.first_name, self.last_name)
        if full_name:
			return full_name.strip()
        return self.get_email()

    def get_short_name(self):
        """
        Returns the short name for the user.
        """
        return self.first_name

    def email_user(self, subject, message, from_email=None, **kwargs):
        """Send an email to this User."""
        send_mail(subject, message, from_email, [self.email], **kwargs)

class SocialProfile(AbstractSocialProfile):
    """
    Concrete class of AbstractSocialProfile.
    Use this if you don't need to extend SocialProfile.
    """

    class Meta(AbstractSocialProfile.Meta):  # noqa: D101
        swappable = 'AUTH_USER_MODEL'

class Group(BaseGroup):
    class Meta:
        proxy = True

    # def validate_unique(self, exclude=self.id):
        # """
        # Since the email address is used as the primary identifier, we must ensure that it is
        # unique. However, this can not be done on the field declaration since is only applies to
        # active users. Inactive users can not login anyway, so we don't need a unique constraint
        # for them.
        # """
        # super(SocialProfile, self).validate_unique(exclude)
        # if self.email and get_user_model().objects.exclude(id=self.id).filter(is_active=True, email__exact=self.email).exists():
            # msg = _("A customer with the e-mail address ‘{email}’ already exists.")
            # raise ValidationError({'email': msg.format(email=self.email)})

		
		
		
# class UserDetails(models.Model):
    # type = models.OneToOneField('SocialProfile')
    # extra_info = models.CharField(max_length=600)
	
# def create_user_profile(sender, instance, created, **kwargs):
    # """Creates a UserProfile Object Whenever a User Object is Created"""
    # if created:
        # SocialProfile.objects.create(user=instance)


# post_save.connect(create_user_profile, sender=settings.AUTH_USER_MODEL)
