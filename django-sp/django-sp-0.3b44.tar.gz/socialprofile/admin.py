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
        (None, {'fields': ('email', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser',
                                       'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2'),
        }),
    )
    readonly_fields = ['last_login', 'date_joined', ]
    #form = UserChangeForm
    #add_form = UserCreationForm
    list_display = ('email', 'username', 'gender', 'first_name', 'last_name', 'is_staff', 'is_active', 'manually_edited','visible','date_joined','last_login')
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('last_login','date_joined','email',)

admin.site.unregister(StockGroup)
 
@admin.register(Group)
class GroupAdmin(BaseGroupAdmin):
    pass