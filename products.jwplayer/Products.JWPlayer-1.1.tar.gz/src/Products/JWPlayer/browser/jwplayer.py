from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.JWPlayer import _

class TinyMCESettings(BrowserView):

    template = ViewPageTemplateFile("templates/jwp-tinymce-settings.pt");

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        return self.template();