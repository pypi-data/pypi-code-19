# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import json
from StringIO import StringIO
from collections import OrderedDict

from django.conf import settings
from django.http import JsonResponse
from rest_framework import views
from rest_framework.permissions import BasePermission
from rest_framework.response import Response
from django.core.management import call_command
from rest_framework.reverse import reverse
from django.apps import apps

DRF_API_DUMP_EXCLUDES = getattr(settings, 'DRF_API_DUMP_EXCLUDES', [])
DRF_API_DUMP_AVAILABLES = getattr(settings, 'DRF_API_DUMP_AVAILABLES', [])
DRF_API_VIEW_TITLE = str(getattr(settings, 'DRF_API_VIEW_TITLE', 'DrfDumpApi'))


class IsSuperUser(BasePermission):
    """
    Allows access only to superusers.
    """

    def has_permission(self, request, view):
        return request.user.is_superuser


class DrfDumpApiView(views.APIView):
    """
    Generates and serves fixturized data from apps and/or models.
    """
    _request = None
    permission_classes = (IsSuperUser,)

    def split_app_model(self, app_model):
        app = None
        model = None
        if '.' in app_model:
            app = app_model.split('.')[0]
            model = app_model.split('.')[1]
        else:
            app = app_model

        try:
            app = apps.get_app_config(app)
        except:
            app = None

        return app, model

    @property
    def all_apps_and_models_dict(self):
        output = OrderedDict()
        for app in apps.get_app_configs():
            output[app.label] = []
            for model in app.get_models():
                output[app.label].append(model._meta.model_name)
        return output

    @property
    def available_to_dump(self):
        app_dict = self.all_apps_and_models_dict
        if len(DRF_API_DUMP_AVAILABLES) > 0:
            # Remove from app dict
            available_dict = OrderedDict()
            for available in DRF_API_DUMP_AVAILABLES:
                app, model = self.split_app_model(available)
                if not app:
                    continue
                app = app.label
                available_dict[app] = []
                if model:
                    available_dict[app].append(model)

            for app in available_dict:
                if len(available_dict[app]) == 0:
                    available_dict[app] = self.all_apps_and_models_dict[app]
        else:
            available_dict = self.all_apps_and_models_dict

        if len(DRF_API_DUMP_EXCLUDES) > 0:
            # make restrictions
            for unavailable in DRF_API_DUMP_EXCLUDES:
                app, model = self.split_app_model(unavailable)
                app = app.label
                if model:
                    if model in available_dict[app]:
                        available_dict[app].remove(model)
                else:
                    del available_dict[app]

        return available_dict

    @property
    def available_list(self):
        availables = []
        for app in self.available_to_dump:
            if len(self.available_to_dump[app]) > 0:
                for model in self.available_to_dump[app]:
                    availables.append(str('%s.%s' % (app, model)))
            else:
                availables.append(str('%s' % app))
        return availables

    @property
    def exclude_list(self):
        exclude_list = []
        for app in self.all_apps_and_models_dict:
            if app not in self.available_to_dump:
                exclude_list.append(str(app))
                continue
            for model in self.all_apps_and_models_dict[app]:
                if model not in self.available_to_dump[app]:
                    exclude_list.append(str('%s.%s' % (app, model)))

        return exclude_list

    def root_content(self, request):
        permissions = self.available_to_dump
        output = OrderedDict(__ALL__=reverse('drf-api-dump:dump-app-view', request=request, kwargs={"pk": '__ALL__'}))

        for app in permissions:
            if not app in output:
                output[app] = OrderedDict(
                    __ALL__=reverse('drf-api-dump:dump-app-view', request=request, kwargs={"pk": app}))
            if app == '__ALL__':
                continue

            for model in permissions[app]:
                if model != '__ALL__':
                    output[app][model] = reverse('drf-api-dump:dump-app-view', request=request,
                                                 kwargs={"pk": "%s.%s" % (app, model)})

        return output

    def get_view_name(self):
        return DRF_API_VIEW_TITLE

    def get(self, request, pk=None):
        if not pk:
            return Response(self.root_content(request))
        else:
            if pk == '__ALL__':
                return self.dump_view(all=True)
            return self.dump_view(pk)

    def dump_view(self, app=None, all=False):
        if not app and not all:
            return JsonResponse({"error": "An app is needed"})
        else:
            dump_arg = app

        if app in self.exclude_list:
            return JsonResponse({"details":"404 Not found"}, status=404)

        exception = None
        output = StringIO()

        if all:
            try:
                call_command('dumpdata', use_base_manager=True, exclude=self.exclude_list, stdout=output)
            except Exception as e:
                exception = e
        else:
            try:
                call_command('dumpdata', dump_arg, exclude=self.exclude_list, stdout=output)
            except Exception as e:
                exception = e

        if exception:
            return JsonResponse({'error': str(e)})
        return Response(json.loads(output.getvalue()))
