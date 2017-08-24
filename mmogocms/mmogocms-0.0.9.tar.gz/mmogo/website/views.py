from django.shortcuts import render


def index(request):
    context = {}
    return render(request, 'website/templates/index.html', context )

def about_us(request):
    context = {}
    return render(request, 'website/templates/about.html', context )


def contact_us(request):
    context = {}
    return render(request, 'website/templates/contacts.html', context )