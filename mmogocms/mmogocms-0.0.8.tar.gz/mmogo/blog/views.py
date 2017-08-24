from django.shortcuts import render


def index(request):
    context = {}
    return render(request, 'blog/templates/index.html', context )

def post(request, slug):
    context = {}
    return render(request, 'blog/templates/post.html', context )
