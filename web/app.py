from flask import Flask,render_template

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


if __name__ == "__main__":
    pass
    #app.run(port=5000, host='172.172.4.131', debug=True)