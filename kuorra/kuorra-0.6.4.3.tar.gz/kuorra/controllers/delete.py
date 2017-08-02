import config

class Delete:

    def GET(self, primary_key):
        result = config.model.get_table_name(int(primary_key))
        return config.render.delete(result)

    def POST(self, primary_key):
        form = config.web.input()
        config.model.delete_table_name(form['primary_key'])
        raise config.web.seeother('/table_name')
