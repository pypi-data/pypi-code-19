from django.contrib import admin
from django.contrib.admin.sites import AdminSite
from .forms import *
from django.contrib.auth.models import User, Group

# Register your models here.
class MyAdminWithReCaptcha(AdminSite):
    login_form = MyAdminLoginForm

my_admin = MyAdminWithReCaptcha()
my_admin.register(User)
my_admin.register(Group)
