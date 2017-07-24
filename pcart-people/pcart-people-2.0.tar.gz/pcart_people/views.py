from django.shortcuts import render
from .models import Person


def people_view(request):
    people = Person.objects.filter(active=True)
    context = {
        'page_url': request.path,
        'people': people,
    }
    return render(request, 'people/people.html', context)
