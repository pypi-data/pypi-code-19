import web
import config

db = config.db

def validate_user(username, password):
    try:
        return db.select('users',where='username=$username and password=$password', vars=locals())[0]
    except Exception as e:
        print "Model get all Error {}".format(e.args)
        print "Model get all Message {}".format(e.message)
        return None