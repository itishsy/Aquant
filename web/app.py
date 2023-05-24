from flask import Flask,render_template

app = Flask(__name__)


@app.route('/69f2aeb7fa0e11edad01f46b8c05cf04')
def index():
    return render_template('index.html')


if __name__ == "__main__":
    app.run(port=5000, host='172.172.4.131', debug=True)