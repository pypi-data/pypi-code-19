from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render
from django.views import View

from results.helpers import get_does_not_exist_model


class ResultView(View):
    template_name = 'results/result.html'
    class_ = 'info'
    title = None
    message = None
    form_errors = None

    def get(self, request):
        return render(request, self.template_name, {
            'class': self.class_,  # 'info' / 'success' / 'danger'
            'title': self.title or '出错了',
            'message': self.message or '未知错误',
            'errors': self.form_errors,
        })


def result_view(request, class_: str = 'info', title: str = None, message=None, form_errors=None):
    return render(request, 'results/result.html', {
        'class': class_,  # 'info' / 'success' / 'danger'
        'title': title or '出错了',
        'message': message or '未知错误',
        'errors': form_errors,
    })


def error_result(request, title=None, message=None, error=None, form=None):
    if error:
        if isinstance(error, ObjectDoesNotExist):
            if not title:
                model = get_does_not_exist_model(error)
                if model:
                    title = '找不到{}'.format(model._meta.verbose_name or model._meta.model_name)
                else:
                    title = '找不到对象'

    return result_view(request,
                       title=title or '出错了',
                       message=message,
                       class_="danger",
                       form_errors=form.errors if form else None)
