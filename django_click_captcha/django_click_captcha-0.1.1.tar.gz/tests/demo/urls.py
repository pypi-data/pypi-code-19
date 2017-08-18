
from django.conf.urls import url, include
from .views import index, form_valid
urlpatterns = [
    url(r'^$', index, name='index'),
    url(r'^next$', form_valid, name='next'),
    url(r'^vendor/', include('click_captcha.urls'))
]

