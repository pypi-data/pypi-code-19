from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import redirect
from django.views.generic import FormView
from django_comments.views.comments import post_comment
from molo.commenting.admin_import_export import MoloCommentsResource
from molo.commenting.forms import AdminMoloCommentReplyForm
from molo.commenting.models import MoloComment
from wagtail.contrib.modeladmin.views import IndexView
from django.utils.translation import ugettext as _


class MoloCommentsAdminView(IndexView):
    def post(self, request, *args, **kwargs):
        drf__submit_date__gte = request.GET.get('drf__submit_date__gte')
        drf__submit_date__lte = request.GET.get('drf__submit_date__lte')
        is_removed__exact = request.GET.get('is_removed__exact')

        filter_list = {
            'submit_date__range': (drf__submit_date__gte,
                                   drf__submit_date__lte) if
            drf__submit_date__gte and drf__submit_date__lte else None,
            'is_removed': is_removed__exact
        }

        arguments = {}

        for key, value in filter_list.items():
            if value:
                arguments[key] = value

        dataset = MoloCommentsResource().export(
            MoloComment.objects.filter(**arguments)
        )

        response = HttpResponse(dataset.csv, content_type="text/csv")
        response['Content-Disposition'] = \
            'attachment;filename=comments.csv'
        return response

    def get_template_names(self):
        return 'admin/molo_comments_admin.html'


class MoloCommentsAdminReplyView(FormView):
    form_class = AdminMoloCommentReplyForm
    template_name = 'admin/molo_comments_admin_reply.html'

    def get_form_kwargs(self):
        kwargs = super(MoloCommentsAdminReplyView, self).get_form_kwargs()
        kwargs['parent'] = self.kwargs['parent']
        return kwargs

    def form_valid(self, form):
        self.request.POST = self.request.POST.copy()
        self.request.POST['name'] = ''
        self.request.POST['url'] = ''
        self.request.POST['email'] = ''
        self.request.POST['parent'] = self.kwargs['parent']
        post_comment(self.request)
        messages.success(self.request, _('Reply successfully created.'))

        return redirect('/admin/modeladmin/commenting/molocomment/')
