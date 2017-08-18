from django.shortcuts import render
from click_captcha.image_unicode import ImageChar
from .forms import CaptchaForm
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse

ImageChar.choice_index = lambda cls, number: [0, 1]


def index(request):
    if request.method == "POST":
        form = CaptchaForm(data=request.POST)
        if form.is_valid():
            return HttpResponseRedirect(reverse('next'))
    else:
        form = CaptchaForm()
    return render(request, template_name='index.html', context={'form': form})


def form_valid(request):
    return HttpResponse('<h1 class="selenium-test">form valid</h1>')
