import web
import application.models.model_table_name

render = web.template.render('application/views/table_name/', base='master')
model = application.models.model_table_name