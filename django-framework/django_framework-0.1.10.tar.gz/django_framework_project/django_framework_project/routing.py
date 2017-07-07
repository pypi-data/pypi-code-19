import importlib
from channels import route

from django.conf import settings

from django_framework.django_framework.django_helpers.channel_helpers.consumers import ws_connect, ws_message, ws_disconnect

channel_routing = [
    # determines what to do when a websocket initially connects
    route("websocket.connect", ws_connect),
    # determine what to do when we receive a message.  All websockets will be sending messages
    route("websocket.receive", ws_message),
    
    # when a websocket closes.
    route("websocket.disconnect", ws_disconnect),
]

# all apps have their own routing on http_request.json
for app_name in settings.SERVER_APPS: # dynamically get the routes! we will enforce that the routes must exist for ALL apps

    try:
        
        module = importlib.import_module(app_name + '.routes', package=None)
    
        for channel_name,method_callback, filters in module.routes:
            channel_routing.append(route(channel_name, method_callback, **filters))
    
    except Exception as e:
        print('Routing probably does not exist!',app_name, e)