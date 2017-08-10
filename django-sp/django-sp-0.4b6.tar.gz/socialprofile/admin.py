"""Django Admin Site configuration for socialprofiles"""

# pylint: disable=R0901,R0904

from django.contrib import admin
from django.contrib.auth.admin import GroupAdmin as BaseGroupAdmin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group as StockGroup
from django.utils.translation import ugettext_lazy as _
from socialprofile.models import Group, SocialProfile
from image_cropping.admin import ImageCroppingMixin

@admin.register(SocialProfile)
class CustomUserAdmin(ImageCroppingMixin, BaseUserAdmin):
    """Sets up the custom user admin display"""
    fieldsets = (
        (None, {'fields': ('email', 'username', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'phone_number')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser',
                                       'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined','date_of_birth')}),
        (_('Contacts Info'), {'fields': ('email','phone_number')}),
        (_('Common Info'), {'fields': ('country', 'gender', 'url', 'image_url')}),
        (_('Staff'), {'fields': ('sort', 'visible', 'title', 'role',
			'function_01','function_02','function_03','function_04','function_05',
			'function_06','function_07','function_08','function_09','function_10',)}),
        (_('Google'), {'fields': ('editByGoogle', 'google_isPlusUser', 'google_plusUrl', 
			'google_circledByCount', 'google_language', 'google_kind', 'google_verified')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'email', 'password1', 'password2'),
        }),
    )
    readonly_fields = ['email', 'last_login', 'date_joined', 
		'editByGoogle', 'google_isPlusUser', 'google_plusUrl', 'google_circledByCount', 'google_language', 'google_kind', 'google_verified' ]
    #form = UserChangeForm
    #add_form = UserCreationForm
    list_display = ('email', 'username', 'gender', 'first_name', 'last_name', 'is_active', 'manually_edited','visible','date_joined','last_login')
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('last_login','date_joined','email',)

from social_django.models import UserSocialAuth, Nonce, Association
from social_django.admin import UserSocialAuthOption, NonceOption, AssociationOption

class ProxyUserSocialAuth(UserSocialAuth):
    """Create UserSocialAuth proxy model for OAuth social_django"""
    class Meta:
        proxy = True   
        verbose_name = "OAuth: " + str(UserSocialAuth._meta.verbose_name)
        verbose_name_plural = "OAuth: " + str(UserSocialAuth._meta.verbose_name_plural)
		
class ProxyNonce(Nonce):
    """Create Nonce proxy model for OAuth social_django"""
    class Meta:
        proxy = True  
        verbose_name = "OAuth: " + str(Nonce._meta.verbose_name)
        verbose_name_plural = "OAuth: " + str(Nonce._meta.verbose_name_plural)		
		
class ProxyAssociation(Association):
    """Create Association proxy model for OAuth social_django"""
    class Meta:
        proxy = True
        verbose_name = "OAuth: " + str(Association._meta.verbose_name)
        verbose_name_plural = "OAuth: " + str(Association._meta.verbose_name_plural)
		
admin.site.unregister(UserSocialAuth)
admin.site.unregister(Nonce)
admin.site.unregister(Association)
admin.site.register(ProxyUserSocialAuth, UserSocialAuthOption)
admin.site.register(ProxyNonce, NonceOption)
admin.site.register(ProxyAssociation, AssociationOption)


from two_factor.models import PhoneDevice
from two_factor.admin import PhoneDeviceAdmin
from django_otp.plugins.otp_static.models import StaticDevice
from django_otp.plugins.otp_static.admin import StaticDeviceAdmin
from django_otp.plugins.otp_totp.models import TOTPDevice
from django_otp.plugins.otp_totp.admin import TOTPDeviceAdmin

class ProxyPhoneDevice(PhoneDevice):
    """Create PhoneDevice proxy model for OAuth two_factor"""
    class Meta:
        proxy = True   
        verbose_name = "Otp: " + str(PhoneDevice._meta.verbose_name)
        verbose_name_plural = "Otp: " + str(PhoneDevice._meta.verbose_name_plural)
		
class ProxyStaticDevice(StaticDevice):
    """Create StaticDevice proxy model for OAuth social_django"""
    class Meta:
        proxy = True  
        verbose_name = "Otp: " + str(StaticDevice._meta.verbose_name)
        verbose_name_plural = "Otp: " + str(StaticDevice._meta.verbose_name_plural)		
		
class ProxyTOTPDevice(TOTPDevice):
    """Create TOTPDevice proxy model for OAuth social_django"""
    class Meta:
        proxy = True
        verbose_name = "Otp: " + str(TOTPDevice._meta.verbose_name)
        verbose_name_plural = "Otp: " + str(TOTPDevice._meta.verbose_name_plural)
		
admin.site.unregister(PhoneDevice)
admin.site.unregister(StaticDevice)
admin.site.unregister(TOTPDevice)
admin.site.register(ProxyPhoneDevice, PhoneDeviceAdmin)
admin.site.register(ProxyStaticDevice, StaticDeviceAdmin)
admin.site.register(ProxyTOTPDevice, TOTPDeviceAdmin)


from user_sessions.admin import SessionAdmin
from user_sessions.models import Session

class ProxySession(Session):
    """Create Session proxy model for user_session"""
    class Meta:
        proxy = True
        verbose_name = "Monitor: " + str(Session._meta.verbose_name)
        verbose_name_plural = "Monitor: " + str(Session._meta.verbose_name_plural)
		
admin.site.unregister(Session)
admin.site.register(ProxySession, SessionAdmin)


from axes.admin import AccessAttemptAdmin, AccessLogAdmin
from axes.models import AccessAttempt, AccessLog

class ProxyAccessAttempt(AccessAttempt):
    """Create AccessAttempt proxy model for user_session"""
    class Meta:
        proxy = True
        verbose_name = "Monitor: " + str(AccessAttempt._meta.verbose_name)
        verbose_name_plural = "Monitor: " + str(AccessAttempt._meta.verbose_name_plural)

class ProxyAccessLog(AccessLog):
    """Create Axes proxy model for user_session"""
    class Meta:
        proxy = True
        verbose_name = "Monitor: " + str(AccessLog._meta.verbose_name)
        verbose_name_plural = "Monitor: " + str(AccessLog._meta.verbose_name_plural)
		
admin.site.unregister(AccessAttempt)
admin.site.unregister(AccessLog)
admin.site.register(ProxyAccessAttempt, AccessAttemptAdmin)
admin.site.register(ProxyAccessLog, AccessLogAdmin)


admin.site.unregister(StockGroup)
@admin.register(Group)
class GroupAdmin(BaseGroupAdmin):
    pass