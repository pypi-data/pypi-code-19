from django.conf.urls import url
from django.core.exceptions import ObjectDoesNotExist
from django.views.generic import TemplateView

from results.views import ResultView
from sample import views as sample_views

urlpatterns = [
    url(r'^$', TemplateView.as_view(template_name='sample/index.html')),

    url('^result-view-class/$',
        ResultView.as_view(template_name='results/result.html',
                           title='sample出错标题',
                           message='sample出错信息',
                           type='info'),
        name='result_view_class'),

    url(r'^form-error/$', sample_views.form_error_view, name='form_error'),

    url(r'^error-result/$', ResultView.error_view, dict(title='出错标题', message='ResultView.error_view'),
        name='error_result'),
    url(r'^error-result/object-does-not-exist/$', ResultView.error_view, dict(error=ObjectDoesNotExist()),
        name='error_result_object_does_not_exist'),

    url(r'^result-view/success/$',
        ResultView.success_view,
        {"title": "success的标题", "message": "success的消息"}, name='result_view_success'),
    url(r'^result-view/danger/$',
        ResultView.error_view,
        {"title": "danger的标题", "message": "danger的消息"}, name='result_view_danger'),
    url(r'^result-view/info/$',
        ResultView.info_view,
        {"title": "info的标题", "message": "info的消息"}, name='result_view_info'),
]
