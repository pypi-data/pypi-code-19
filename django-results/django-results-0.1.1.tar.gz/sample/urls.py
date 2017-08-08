from functools import partial

from django.conf.urls import url
from django.core.exceptions import ObjectDoesNotExist
from django.views.generic import TemplateView

from results import views as results_views
from results.views import error_result
from sample import views as sample_views

urlpatterns = [
    url(r'^$', TemplateView.as_view(template_name='sample/index.html')),
    url(r'^form-error/$', sample_views.form_error_view, name='form_error'),

    url(r'^error-result/$', partial(error_result, title='出错标题', message='出错消息'), name='error_result'),
    url(r'^error-result/object-does-not-exist/$',
        partial(error_result, error=ObjectDoesNotExist()),
        name='error_result_object_does_not_exist'),

    url(r'^result_view/success/$',
        results_views.result_view,
        {"title": "success的标题", "message": "success的消息", "class_": 'success'}, name='result_view_success'),
    url(r'^result_view/danger/$',
        results_views.result_view,
        {"title": "danger的标题", "message": "danger的消息", "class_": 'danger'}, name='result_view_danger'),
    url(r'^result_view/info/$',
        results_views.result_view,
        {"title": "info的标题", "message": "info的消息", "class_": 'info'}, name='result_view_info'),
]
