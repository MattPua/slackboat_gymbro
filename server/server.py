from flask import Flask
app = Flask(__name__)




@app.route("/")
def hello_world():
    return "Hello world!"

@app.route("/hello")
def yo():
    return "Hello"

if __name__ == '__main__':
    app.debug = True
    app.run()
