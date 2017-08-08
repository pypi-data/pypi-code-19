import tornado.testing
import tornado.web
import tornado_transmute
import json

@tornado_transmute.describe(paths="/foo/{multiplier}")
@tornado_transmute.annotate({"multiplier": int, "return": int})
def get(self, multiplier):
    return 2 * multiplier


@tornado_transmute.describe(paths="/add")
@tornado_transmute.annotate({"left": int, "right": int, "return": int})
def add(self, left, right):
    return left + right


@tornado_transmute.describe(paths="/add", methods="POST")
@tornado_transmute.annotate({"left": int, "right": int, "return": int})
def subtract(self, left, right):
    return left - right


@tornado_transmute.describe(paths="/exception", methods="GET")
def exception(self):
    return raise_exception()


def raise_exception():
    raise Exception("OFOOONTHE")


app = route_set = tornado_transmute.RouteSet()
route_set.add(get)
route_set.add(add)
route_set.add(subtract)
route_set.add(exception)
app = tornado.web.Application(route_set.generate_url_specs())
tornado_transmute.add_swagger(app, "/swagger.json", "/swagger")

if __name__ == "__main__":
    app.listen(8888)
    tornado.ioloop.IOLoop.current().start()
