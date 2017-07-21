import web
import application.models.model_users

render = web.template.render('application/views/main/', base='master')
model = application.models.model_users

form = web.form.Form(
        web.form.Textbox(
            'username',
            web.form.notnull,
            size=30,
            description="Username:",
            class_="form-control"
            ),
        web.form.Password(
            'password',
            web.form.notnull,
            size=30,
            description="Password:",
            class_="form-control"
            ),
        web.form.Button(
            'Login',
            class_="form-control"
            )
    )