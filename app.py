from flask import Flask 

app = Flask(__name__) 

@app.route('/')
def index():
    return "Hello Flask"

@app.route('/sayMyName/<name>/')
def response(name):
    return "Hello " + name

@app.route('/sayHello/')
def hello():
    return "Hello " * 10

if __name__ == '__main__': 
	app.run()