from flask import Flask
from settings import *

app = Flask(__name__)


@app.route("/slack_gymlife")
def new_exercise():
    print request


if __name__ == '__main__':
    app.debug = DEBUG
    app.run(host='0.0.0.0')

