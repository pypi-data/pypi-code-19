# -*- coding: utf-8 -*-
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.http import Http404
from django.shortcuts import render
from django.utils import timezone

from background_task.models import Task
from threebot_repeat.tasks import repeat_workflow


@login_required
def list(request, template_name='threebot_repeat/list.html'):
    repetitive_tasks = Task.objects.filter(Q(repeat_until__gte=timezone.now()) | Q(repeat_until=None)).exclude(repeat=Task.NEVER)
    kwvars = {
        'repetitive_tasks': repetitive_tasks,
    }
    return render(request, template_name, kwvars)


@login_required
def replay_and_repeat(request, log_id):
    available_choices = [
        3600,
        3600 * 24,
        3600 * 24 * 7,
        3600 * 24 * 7 * 2,
        3600 * 24 * 7 * 4,
    ]
    repeat_choice = request.GET.get('choice', '')
    try:
        repeat_choice = int(repeat_choice)
        assert repeat_choice in available_choices
    except (ValueError, AssertionError):
        raise Http404("'{}' is not a valid choice for repeat".format(repeat_choice))

    repeat_workflow(log_id, repeat=repeat_choice)
    return HttpResponseRedirect(reverse('threebot_repeat_list'))


@login_required
def stop_repetition(request, bg_task_id):
    try:
        Task.objects.get(id=bg_task_id).delete()
    except Task.DoesNotExist:
        pass
    return HttpResponseRedirect(reverse('threebot_repeat_list'))
