from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from guardian.shortcuts import get_objects_for_user

from configfactory.configurations import config
from configfactory.configurations.forms import (
    ComponentForm,
    ComponentSchemaForm,
    ComponentSettingsForm,
)
from configfactory.environments.helpers import get_environment_alias
from configfactory.environments.models import Environment
from configfactory.exceptions import ComponentDeleteError
from configfactory.models import Component
from configfactory.services import delete_component
from configfactory.users.decorators import superuser_required
from configfactory.utils import cleanse_dict, inject_dict_params


@superuser_required()
def component_create(request):

    if request.method == 'POST':

        form = ComponentForm(data=request.POST)

        if form.is_valid():
            form.save()
            return redirect(to=reverse('index'))
    else:
        form = ComponentForm()

    return render(request, 'components/create.html', {
        'form': form
    })


@superuser_required()
def component_edit(request, alias):

    component = get_object_or_404(Component, alias=alias)

    if request.method == 'POST':

        form = ComponentForm(data=request.POST, instance=component)

        if form.is_valid():
            form.save()
            messages.success(request, "Component successfully updated.")
            return redirect(to=reverse('view_component',
                                       kwargs={'alias': component.alias}))
    else:
        form = ComponentForm(instance=component)

    return render(request, 'components/edit.html', {
        'form': form,
        'component': component
    })


@superuser_required()
def component_edit_schema(request, alias):

    component = get_object_or_404(Component, alias=alias)
    schema = component.schema

    if request.method == 'POST':

        form = ComponentSchemaForm(data=request.POST, initial={
            'schema': schema
        })

        if form.is_valid():
            data = form.cleaned_data
            component.schema = data['schema']
            component.save()
            messages.success(request, "Component schema successfully updated.")
        else:
            messages.error(
                request,
                form.errors.as_text(),
                extra_tags=' alert-danger'
            )
    else:
        form = ComponentSchemaForm(initial={
            'schema': schema
        })

    return render(request, 'components/edit_schema.html', {
        'form': form,
        'component': component
    })


@superuser_required()
def component_delete(request, alias):

    component = get_object_or_404(Component, alias=alias)

    if request.method == 'POST':
        try:
            delete_component(component)
        except ComponentDeleteError as e:
            messages.error(request, str(e), extra_tags=' alert-danger')
            return redirect(to=reverse('delete_component', kwargs={
                'alias': component.alias
            }))

        messages.success(request, "Component successfully deleted.")
        return redirect(to=reverse('index'))

    return render(request, 'components/delete.html', {
        'component': component
    })


@login_required()
def component_view(request, alias, environment=None):

    user = request.user
    component = get_object_or_404(Component, alias=alias)
    environments = get_objects_for_user(
        user=user,
        perms=('view_environment', 'change_environment'),
        any_perm=True,
        klass=Environment
    )
    alias = get_environment_alias(environment)
    environment = get_object_or_404(environments, alias=alias)

    try:
        edit_mode = int(request.GET.get('edit_mode', False))
    except TypeError:
        raise Http404

    settings_dict = config.get_settings(
        component=component,
        environment=environment,
        flatten=not edit_mode
    )

    if not edit_mode:
        settings_dict = cleanse_dict(
            inject_dict_params(
                data=settings_dict,
                params=config.get_all_settings(environment, flatten=True),
                raise_exception=False
            )
        )

    if request.method == 'POST':

        form = ComponentSettingsForm(
            component=component,
            environment=environment,
            data=request.POST,
            initial={
                'settings': settings_dict
            }
        )

        if form.is_valid():
            data = form.cleaned_data
            component = config.update_settings(
                component=component,
                environment=environment,
                settings=data['settings']
            )
            messages.success(
                request,
                "Component %(component)s settings successfully updated." % {
                    'component': component.name
                }
            )
        else:
            messages.error(
                request,
                form.errors.as_text(),
                extra_tags=' alert-danger'
            )

    else:
        form = ComponentSettingsForm(
            component=component,
            environment=environment,
            initial={
                'settings': settings_dict
            }
        )

    return render(request, 'components/view.html', {
        'component': component,
        'environments': environments,
        'current_environment': environment,
        'form': form,
        'edit_mode': edit_mode,
    })
