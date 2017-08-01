from django.conf.urls import url

from qrcode2.views import qrcode_img_view

urlpatterns = [
    url(r'^(.*?)/', qrcode_img_view, name='qrcode'),
]
