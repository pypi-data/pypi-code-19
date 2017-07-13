from django.shortcuts import reverse
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe

class RootMenu:
    def __init__(self, request):
        self.items = []
        self.request = request

    def add(self, item):
        self.items.append(item)

    @mark_safe
    def __str__(self):
        for item in self.items:
            item.set_current(self.request)

        rows = []
        for item in self.items:
            res = item.render(self.request)
            if res:
                rows.append(res)
        return ''.join(rows)

class Menu:
    def __init__(self, label, items, icon='cubes'):
        self.label = label
        self.items = items
        self.icon = icon

    def is_current(self, request):
        return any(item.is_current(request) for item in self.items)

    def set_current(self, request):
        for item in self.items:
            item.set_current(request)

    def render(self, request):
        rows = []
        for item in self.items:
            rows.append(item.render(request))

        if not any(rows):
            return ''

        active = self.is_current(request)
        items = ''.join(rows)
        return render_to_string('ms_utils/menu/menu.html', dict(menu=self, items=items, active=active))

class MenuItem:
    def __init__(self, label, url, perms=None, icon='cube'):
        self.label = label
        self.url = url
        self.perms = perms
        self.icon = icon

    def is_current(self, request):
        return request.session.get('lasturl') == self.url

    def set_current(self, request):
        if request.path == reverse(self.url):
            request.session['lasturl'] = self.url

    def render(self, request):
        if self.perms:
            if isinstance(self.perms, (list, tuple)):
                if not any(map(request.user.has_perm, self.perms)): return ''
            else:
                if not request.user.has_perm(self.perms): return ''

        active = self.is_current(request)

        return render_to_string('ms_utils/menu/menuitem.html', dict(item=self, active=active))
