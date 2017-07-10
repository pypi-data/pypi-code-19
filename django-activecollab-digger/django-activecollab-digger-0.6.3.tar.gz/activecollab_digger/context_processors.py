from django.conf import settings as s


def activecollab_digger(request):
    return {
        'AC_BASE_URL': s.AC_BASE_URL,
        'LOGIN_URL': s.LOGIN_URL,
        'PROJECT_NAME': s.PROJECT_NAME,
        'PROJECT_TITLE': s.PROJECT_TITLE
    }
