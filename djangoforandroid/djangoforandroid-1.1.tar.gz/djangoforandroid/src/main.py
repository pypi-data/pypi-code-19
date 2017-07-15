#Generated with django-for-android

""" Start Django in multithreaded mode

It allows for debugging Django while serving multiple requests at once in
multi-threaded mode.

"""

import sys
import os

if not '--nodebug' in sys.argv:

    log_path = "{{APP_LOGS}}"

    if not os.path.exists(log_path):
        os.mkdir(log_path)
        #os.makedirs(log_path, exist_ok=True)

    print("Logs in {}".format(log_path))
    sys.stdout = open(os.path.join(log_path, "stdout.log"), "w")
    sys.stderr = open(os.path.join(log_path, "stderr.log"), "w")

print("Starting Django Server")
from wsgiref import simple_server
from django.core.wsgi import get_wsgi_application

sys.path.append(os.path.join(os.path.dirname(__file__), "{{NAME}}"))

#os.environ['LD_LIBRARY_PATH'] = ":".join(filter(None, [os.path.abspath(os.environ.get('LD_LIBRARY_PATH', '')),
                                                       #os.path.abspath('.'),
                                                       #os.path.abspath('../lib'),
                                                       #'/data/data/com.yeisoncardona.piton/lib/',
                                                       #os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'lib')),
                                                       #]))

#sys.path.append(os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'lib')))
#sys.path.append(os.path.abspath('../lib'))
#sys.path.append("/data/data/com.yeisoncardona.piton/lib/")

#----------------------------------------------------------------------
def django_wsgi_application():
    """"""
    print("Creating WSGI application...")
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "{{NAME}}.settings")
    application = get_wsgi_application()
    return application


#----------------------------------------------------------------------
def main():
    """"""
    if {{APP_MULTITHREAD}}:
        import socketserver
        class ThreadedWSGIServer(socketserver.ThreadingMixIn, simple_server.WSGIServer):
            pass
        httpd = simple_server.make_server('{{IP}}' , {{PORT}}, django_wsgi_application(), server_class=ThreadedWSGIServer)
    else:
        httpd = simple_server.make_server('{{IP}}' , {{PORT}}, django_wsgi_application())

    httpd.serve_forever()
    print("Django for Android serving on {}:{}".format(*httpd.server_address))


main()
