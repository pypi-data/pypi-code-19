import config

class Edit:
    
    def GET(self, primary_key):
        result = config.model.get_table_name(int(primary_key))
        return config.render.edit(result)

    def POST(self, primary_key):
        form = config.web.input()

        config.model.edit_table_name(
            fields
            
        )
        raise config.web.seeother('/table_name')