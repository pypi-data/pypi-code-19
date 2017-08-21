from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import Http404, HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.views.static import serve

from configfactory import __version__, backup, logs
from configfactory.users.decorators import superuser_required
from configfactory.utils import current_timestamp


@login_required()
def index(request):
    return render(request, 'index.html')


@login_required()
def backup_dump(request):

    if request.method == 'POST':

        name = backup.dump()

        messages.success(
            request,
            'Settings successfully dumped as `{}`.'.format(name)
        )
        return redirect(to=reverse('load_backup'))

    return render(request, 'backup/dump.html', {

    })


@superuser_required()
def backup_load(request, filename=None):

    if filename:

        if request.method == 'POST':
            backup.load(filename)
            messages.success(
                request, 'Backup `{}` successfully loaded.'.format(filename))
            return redirect(to=reverse('load_backup'))

        return render(request, 'backup/load_confirmation.html', {
            'filename': filename
        })

    backups = backup.get_all()

    return render(request, 'backup/load.html', {
        'backups': backups
    })


@superuser_required()
def backup_delete(request, filename):

    if not backup.exists(filename):
        raise Http404

    if request.method == 'POST':
        backup.delete(filename)
        messages.success(
            request,
            'Backup `{}` successfully deleted.'.format(filename))
        return redirect(to=reverse('load_backup'))

    return render(request, 'backup/delete.html', {
        'filename': filename
    })


@superuser_required()
def backup_serve(request, filename):

    if not backup.exists(filename):
        raise Http404

    return serve(
        request=request,
        path=filename,
        document_root=backup.BACKUP_DIR
    )


@superuser_required()
def logs_index(request):

    return render(request, 'logs/index.html', {
        'log_files': logs.get_all()
    })


@superuser_required()
def logs_serve(request, filename):

    if not logs.exists(filename):
        raise Http404

    return serve(
        request=request,
        path=filename,
        document_root=logs.LOGGING_DIR
    )


def ping(request):
    return HttpResponse('OK')


def alive(request):
    return JsonResponse(data={
        'component': 'configfactory',
        'version': __version__,
        'host': request.META['HTTP_HOST'],
        'time': current_timestamp(),
        'alive': True,
    })
