from configfactory.models import Component


def components(request):
    return {
        'components': Component.objects.all(),
    }
