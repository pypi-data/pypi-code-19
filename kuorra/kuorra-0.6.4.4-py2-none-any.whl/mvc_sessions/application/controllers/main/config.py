import web
import application.models.model_users

render = web.template.render('application/views/main/', base='master')
model = application.models.model_users
