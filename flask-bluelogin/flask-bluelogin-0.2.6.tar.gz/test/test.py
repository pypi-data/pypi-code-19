from flask import Flask, request, current_app
from flask_bluelogin import BlueLogin
from flask_bluelogin.models.user import User
from flask_bluelogin.models.users import Users
from flask_bluelogin.util import check_login
import logging

app = Flask(__name__)
app.secret_key = 'super secret string'
app.register_blueprint(BlueLogin(url_prefix="/api", ui_testing=True))
User(id="fred", password="fred").save()
Users().add_user(User(id='admin', password='passadmin', groups=['admin',]))
Users().add_user(User(id='test', password='passtest'))

@app.route("/")
def hello():
    return "Hello World!"

@app.route("/check")
@check_login()
def check():
    return "You are authentified"

@app.route("/admin")
@check_login("admin")
def admin():
    return "you are admin"


if __name__ == "__main__":
    app.run(port=8080)
