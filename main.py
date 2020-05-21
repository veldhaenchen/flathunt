# Simple Flask Webserver to control / configure flathunter

from flask import Flask
from flask import render_template

app = Flask(__name__)

@app.route("/index")
@app.route('/')
def index():
    return render_template("index.html", title="Home")

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)
