

import os
import logging

import datetime as dt

import flask
from flask import Flask, render_template, redirect, url_for, request
from flask_socketio import SocketIO, join_room, leave_room, send, disconnect


logging.getLogger().setLevel(logging.DEBUG)

app = Flask(__name__, template_folder='templates')
app.config['DEBUG'] = True
app.config['SECRET'] = 'secret!'


# Set this variable to "threading", "eventlet" or "gevent" to test the
# different async modes, or leave it set to None for the application to choose
# the best option based on installed packages.
async_mode = None

socketio = SocketIO(app, json=flask.json, async_mode=async_mode)

clients = []
passwords = {}


def fmt(d):
    return d.strftime('%d%b %H:%M:%S')


@socketio.on('join', namespace='/chat')
def on_join(data):
    global clients

    print(data)
    name = data.get('name', None)
    room = data.get('room', None)
    password = data.get('password', None)

    if (not name) or (not room) or (not password):
        msg = 'Wrong join: ' + str(data)
        print(msg)
        return {'msg': msg}

    new_client = {'name': name,
                  'room': room,
                  'password': password,
                  'datetime': fmt(dt.datetime.now()),
                  'sid': request.sid}

    data = {'datetime': fmt(dt.datetime.now()),
            'sid': request.sid}

    warning_msg = None
    if name in [c['name'] for c in clients if c['room'] == room]:
        warning_msg = "Pseudo already used. It'll work but confusing. Change it !"
        data['warning_msg'] = warning_msg

    if room not in passwords:
        passwords[room] = password

    if password != passwords[room]:
        warning_msg = 'Wrong password. Messages will appear garbled if at all !'
        data['warning_msg'] = warning_msg

    join_room(room)
    clients.append(new_client)

    print('new client =', str(new_client))
    print('connected clients =', str(clients))
    print('passwords =', str(passwords))

    data2 = {'name': 'Server',
             'text': '{} has joined the room'.format(name)}
    socketio.emit('msg', data2, room=room, namespace='/chat')

    data3 = {'clients': [c for c in clients
                         if c['room'] == new_client['room']]}
    socketio.emit('status', data3, room=room, namespace='/chat')

    return data


@socketio.on('kill', namespace='/chat')
def on_kill(data):
    global clients

    print(data)
    sid = data.get('sid', None)

    if not sid:
        msg = 'Wrong kill: ' + str(data)
        print(msg)
        return {'msg': msg}

    out_client = {'sid': sid}
    out_client = [c for c in clients if c['sid'] == out_client['sid']][0]
    room = out_client['room']
    clients = [c for c in clients if c['sid'] != out_client['sid']]

    print('client killed =', str(out_client))
    print('connected clients =', str(clients))
    print('passwords =', str(passwords))

    data = {'clients': [c for c in clients if c['room'] == room]}
    socketio.emit('status', data, room=room, namespace='/chat')

    leave_room(room, sid=sid)
    disconnect()


@socketio.on('leave', namespace='/chat')
def on_leave(data):
    global clients

    print(data)
    sid = data.get('sid', None)

    if not sid:
        msg = 'Wrong leave: ' + str(data)
        print(msg)
        return {'msg': msg}

    out_client = {'sid': sid}
    out_client = [c for c in clients if c['sid'] == out_client['sid']][0]
    room = out_client['room']
    name = out_client['name']
    clients = [c for c in clients if c['sid'] != out_client['sid']]

    set_rooms = set([c['room'] for c in clients])
    if room not in set_rooms:
        passwords.pop(room)

    print('client leaving =', str(out_client))
    print('connected clients =', str(clients))
    print('passwords =', str(passwords))

    data = {'clients': [c for c in clients if c['room'] == room]}
    socketio.emit('status', data, room=room, namespace='/chat')

    data = {'name': 'Server',
            'text': '{} has left the room'.format(name)}
    socketio.emit('msg', data, room=room, namespace='/chat')

    leave_room(room)
    disconnect()


@socketio.on('clients', namespace='/chat')
def on_clients(data):

    client = {'sid': request.sid}
    client = [c for c in clients if c['sid'] == client['sid']][0]
    room = client['room']

    print('request for clients')
    print('connected clients =', str(clients))
    print('passwords =', str(passwords))

    data = {'clients': [c for c in clients if c['room'] == room]}
    socketio.emit('status', data, room=room, namespace='/chat')

    return data


@socketio.on('msg', namespace='/chat')
def on_msg(data):
    print(data)
    name = data.get('name', None)
    room = data.get('room', None)
    text = data.get('text', None)
    sid = data.get('sid', None)

    if (not name) or (not room) or (not text) or (not sid):
        msg = 'Wrong msg:' + str(data)
        print(msg)
        return {'msg': msg}

    data = {'room': room,
            'name': name,
            'sid': sid,
            'text': text,
            }
    socketio.emit('msg', data, room=room,
                  namespace='/chat', include_self=False)
    msg = 'msg "{}" from {} broadcasted to room {}'.format(text, name, room)
    return {'msg': msg}


# default route
@app.route('/info', methods=['GET'])
def info():
    """single page app"""
    return render_template('info.html', async_mode=socketio.async_mode)


# fallback
@app.route('/')
def root():
    """redirect"""
    return redirect(url_for('info'))


@app.route('/<path:dummy>')
def fallback(dummy):
    """redirect"""
    return redirect(url_for('info'))


port = int(os.environ.get('port', 5000))

logging.info(app.config)
logging.info('Starting ezchat hub')
socketio.run(app, debug=True, port=port)
