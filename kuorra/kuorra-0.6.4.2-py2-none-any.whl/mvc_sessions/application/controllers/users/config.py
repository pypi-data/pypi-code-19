import web
import application.models.model_users

render = web.template.render('application/views/users/', base='master')
model = application.models.model_users