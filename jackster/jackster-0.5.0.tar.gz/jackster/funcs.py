def html(html):
    def func(req, res, nxt):
        res.html(html)
    return func


def json(obj):
    def func(req, res, nxt):
        res.json(obj)
    return func


def text(text):
    def func(req, res, nxt):
        res.text(text)
    return func
