from django.core.exceptions import ObjectDoesNotExist
from django.forms.utils import ErrorDict
from django.shortcuts import render
from django.views import View

from results.helpers import get_does_not_exist_model


class ResultView(View):
    template_name = 'results/result.html'
    type = 'info'
    title = ''
    message = ''
    error = None

    def get(self, request):
        return self.result_view(request, self.type, self.title, self.message, self.error,
                                template_name=self.template_name)

    @classmethod
    def render_error(cls, request, error):
        title = ''
        message = ''

        if isinstance(error, ObjectDoesNotExist):
            model = get_does_not_exist_model(error)
            if model:
                title = '找不到{}'.format(model._meta.verbose_name or model._meta.model_name)
            else:
                title = '找不到对象'
        elif isinstance(error, ErrorDict):
            title = '数据验证失败'
            message = str(error)

        return title, message

    @classmethod
    def result_view(cls, request, type='info', title='', message='', error=None, template_name=None, **kwargs):
        if error:
            error_title, error_message = cls.render_error(request, error)
            if error_title:
                title = title or error_title
            if error_message:
                message = message + error_message

        return render(request, template_name or cls.template_name, {
            'type': type or cls.type,  # 'info' / 'success' / 'danger'
            'title': title or cls.title,
            'message': message or cls.message,
            **kwargs,
        })

    @classmethod
    def error_view(cls, request, title='', message='', error=None, template_name=None, **kwargs):
        return cls.result_view(request, 'error', title, message, error, template_name, **kwargs)

    @classmethod
    def success_view(cls, request, title='', message='', error=None, template_name=None, **kwargs):
        return cls.result_view(request, 'success', title, message, error, template_name, **kwargs)

    @classmethod
    def info_view(cls, request, title='', message='', error=None, template_name=None, **kwargs):
        return cls.result_view(request, 'info', title, message, error, template_name, **kwargs)
