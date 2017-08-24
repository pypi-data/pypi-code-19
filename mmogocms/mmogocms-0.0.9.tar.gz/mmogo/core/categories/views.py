from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from .models import Category


# Create your views here.
# def categories_list(request):
#     categories = Categories.objects.all()
#     return render(request, 'categories/index.html', {'nodes': categories})


def category(request, path, instance):
    print instance
    print path

    children = instance.get_children() if instance else Category.objects.root_nodes()
    return render(request, 'categories/index.html',
                  {'instance': instance, 'children': children})

#
# def category(request, path, instance):
#     print instance
#     print path
#
#     category = instance.get_children() if instance else Categories.objects.root_nodes()
#     return render(request, 'categories/category.html',
#                   {'instance': instance, 'category': category})
