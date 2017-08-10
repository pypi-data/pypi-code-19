import json
import http.server

class Handler(http.server.BaseHTTPRequestHandler):

    def bodyData(self):
        if not 'content-length' in self.headers:
            return {}
        return json.loads(self.rfile.read(int(self.headers['content-length'])))

    def needs(self, data, *args):
        for i in args:
            if not i in data:
                raise Exception('Could not find \'' + i + '\' in ' + str(data))
        return data

    def has(self, data, *args):
        for i in args:
            if not i in data:
                return False
        return True

    def __handle_exception_wrap(self):
        try:
            self.req(self.bodyData())
        except Exception as e:
            self.err(e)
            raise

    def err(self, msg):
        return self.json({'error': True, 'msg': str(msg)}, status=500)

    def json(self, data, status=200):
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))

    def do_POST(self):
        self.__handle_exception_wrap()

    def do_GET(self):
        self.__handle_exception_wrap()

    def req(self, body):
        self.json({'Nothing': 'to see here yet'})

def run(handler, addr=('0.0.0.0', 8000)):
    httpd = http.server.HTTPServer(addr, handler)
    httpd.serve_forever()

def main():
    run(Handler)

if __name__ == '__main__':
    main()
