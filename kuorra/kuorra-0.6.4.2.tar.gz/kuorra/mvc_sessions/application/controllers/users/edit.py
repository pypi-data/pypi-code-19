from . import config
import hashlib


class Edit:

    def GET(self, username):
        result = config.model.get_users(username)
        return config.render.edit(result)

    def POST(self, username):
        form = config.web.input()
        pwdhash = hashlib.md5(form.password).hexdigest()

        config.model.edit_users(
            form['username'],
            pwdhash,
            form['privilege']
        )
        raise config.web.seeother('/users')