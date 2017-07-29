# coding: utf-8
from decouple import config, Csv

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False
ALLOWED_HOSTS = config('ALLOWED_HOSTS', cast=Csv(), default='djotali.com')
