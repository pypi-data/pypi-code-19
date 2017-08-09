from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render
from django.views import View

from results.helpers import get_does_not_exist_model


class ResultView(View):
    template_name = 'results/result.html'
    class_ = 'info'
    title = '出错了'
    message = '未知错误'
    form_errors = None

    def get(self, request, *args, **kwargs):
        return self.result_view(request)

    @classmethod
    def result_view(cls, request, class_: str = 'info', title: str = None, message=None, form_errors=None,
                    template_name=None):
        return render(request, template_name or cls.template_name, {
            'class': class_ or cls.class_,  # 'info' / 'success' / 'danger'
            'title': title or cls.title,
            'message': message or cls.message,
            'errors': form_errors or cls.form_errors,
        })

    @classmethod
    def error_result(cls, request, title=None, message=None, error=None, form=None, template_name=None):
        if error:
            if isinstance(error, ObjectDoesNotExist):
                if not title:
                    model = get_does_not_exist_model(error)
                    if model:
                        title = '找不到{}'.format(model._meta.verbose_name or model._meta.model_name)
                    else:
                        title = '找不到对象'

        return cls.result_view(request,
                               title=title,
                               message=message,
                               class_="danger",
                               form_errors=form.errors if form else None,
                               template_name=template_name)
