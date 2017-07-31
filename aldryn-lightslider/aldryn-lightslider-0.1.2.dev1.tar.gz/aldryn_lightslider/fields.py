from django.forms import fields, widgets


class Classes(fields.CharField):
    widget = widgets.Textarea
