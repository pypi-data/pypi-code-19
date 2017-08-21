import configfactory


def version(request):
    return {
        'version': configfactory.__version__
    }
