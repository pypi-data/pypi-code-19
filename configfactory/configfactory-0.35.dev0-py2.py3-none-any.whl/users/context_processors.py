def auth(request):
    return {
        'current_user':  request.user
    }
