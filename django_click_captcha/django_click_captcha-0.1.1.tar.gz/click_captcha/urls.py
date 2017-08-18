from django.conf.urls import url

from click_captcha import views

urlpatterns = [
    url(r'click_captcha/(?P<uuid>\w+)/$', views.CaptchaView.as_view(), name='click_captcha'),
]
