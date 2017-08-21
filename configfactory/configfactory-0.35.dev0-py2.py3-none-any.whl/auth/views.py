from django.shortcuts import redirect, render
from django.urls import reverse

from configfactory import auth
from configfactory.auth.forms import LoginForm


def login(request):

    if request.user.is_authenticated:
        return redirect(to=reverse('index'))

    if request.method == 'POST':
        form = LoginForm(data=request.POST)
        if form.is_valid():
            auth.login(request, form.user)
            return redirect(to=reverse('index'))
    else:
        form = LoginForm()

    return render(request, 'login.html', {
        'form': form
    })


def logout(request):
    auth.logout(request)
    return redirect(reverse('login'))
