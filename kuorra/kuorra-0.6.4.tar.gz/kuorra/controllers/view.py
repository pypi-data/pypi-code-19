import config

class View:

    def GET(self, primary_key):
        primary_key = int(primary_key)
        result = config.model.get_table_name(primary_key)
        return config.render.view(result)
