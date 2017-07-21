import web
from . import config

db = config.db


def validate_user(username, password):
    try:
        return db.select('users',
        where='username=$username and password=$password', vars=locals())[0]
    except Exception as e:
        print(("Model get all Error {}".format(e.args)))
        print(("Model get all Message {}".format(e.message)))
        return None


def get_all_users():
    try:
        return db.select('users')
    except Exception as e:
        print(("Model get all Error {}".format(e.args)))
        print(("Model get all Message {}".format(e.message)))
        return None


def get_users(username):
    try:
        return db.select('users', where='username=$username', vars=locals())[0]
    except Exception as e:
        print(("Model get Error {}".format(e.args)))
        print(("Model get Message {}".format(e.message)))
        return None


def delete_users(username):
    try:
        return db.delete('users', where='username=$username', vars=locals())
    except Exception as e:
        print(("Model delete Error {}".format(e.args)))
        print(("Model delete Message {}".format(e.message)))
        return None


def insert_users(username, password, privilege):
    try:
        db.insert('users',
        username=username,
        password=password,
        privilege=privilege)
    except Exception as e:
        print(("Model insert Error {}".format(e.args)))
        print(("Model insert Message {}".format(e.message)))
        return None


def edit_users(username, password, privilege):
    try:
        db.update('users', username=username,
password=password,
privilege=privilege,
                  where='username=$username',
                  vars=locals())
    except Exception as e:
        print(("Model update Error {}".format(e.args)))
        print(("Model updateMessage {}".format(e.message)))
        return None
