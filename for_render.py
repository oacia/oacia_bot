# render必须得起一个http服务,否则就会断开连接....
from flask import Flask

app = Flask(__name__)


@app.route('/')
def home():
    return "hello world"


@app.route('/webhook')
def webhook():
    return 'ok'


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=10000)
