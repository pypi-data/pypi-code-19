from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from material.frontend.views import ListModelView, ModelViewSet, DetailModelView
from npolling import models as polling_models


# Create your views here.
class ComparisonReportListView(ListModelView):
    model = polling_models.ComparisonReport
    list_display = ('trip',)
    template_name = 'npolling/index.html'

    # def get_queryset(self):
    #     today = timezone.now().date()
    #     department = get_object_or_404(polling_models.ComparisonReport, pk=self.kwargs['report_pk'])
    #     queryset = super(ComparisonReportListView, self).get_queryset()
    #
    #
    #     # return queryset.filter(
    #     #     deptemp__department=department,
    #     #     deptemp__from_date__lte=today,
    #     #     deptemp__to_date__gt=today
    #     # )
    #     return queryset.all()
    #
    # def get_context_data(self, **kwargs):
    #     report = get_object_or_404(polling_models.ComparisonReport, pk=self.kwargs['report_pk'])
    #     return super(ComparisonReportListView, self).get_context_data(
    #         report=report, **kwargs)


class ComparisonReportDetailsView(DetailModelView):
    model = polling_models.ComparisonReport


class ComparisonReportViewSet(ModelViewSet):
    model = polling_models.ComparisonReport
    # list_display = ('trip',)
    detail_view_class = ComparisonReportDetailsView
    list_view_class = ComparisonReportListView



