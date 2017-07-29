import tornado.ioloop
import tornado.web


class MainHandler(tornado.web.RequestHandler):  
    def get(self):  
        self.write("Hello, world")  
  
application = tornado.web.Application([  
    (r"/",MainHandler),  
])  
  
if __name__=="__main__":  
	print("start bind to port:6666")
	application.listen(6666)
	tornado.ioloop.IOLoop.instance().start()  
