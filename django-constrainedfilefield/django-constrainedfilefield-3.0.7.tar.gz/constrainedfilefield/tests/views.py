from django.shortcuts import render

from constrainedfilefield.tests import forms


def nomodel_form(request):
    """

    Parameters
    ----------
    request: HTTP request

    Returns
    --------
    HttpResponse
        with a context dictionary
    """
    context = {}
    if request.method == 'POST':
        form = forms.TestNoModelForm(request.POST, )
        if form.is_valid():
            pass
        else:
            pass
    else:
        context['form'] = forms.TestNoModelForm()
    return render(request, 'tests/form.html', context)
