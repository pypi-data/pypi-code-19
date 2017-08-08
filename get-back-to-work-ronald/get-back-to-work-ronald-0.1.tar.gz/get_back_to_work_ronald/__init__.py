from flask import Flask, render_template


app = Flask('get_back_to_work_ronald')


@app.route('/')
def gotcha():
    return render_template('index.html')


app.run(host='127.0.0.1', port=80)
