from flask import Flask
app = Flask(__name__)

if __name__ == '__main__':
  app.run(debug=True, host='0.0.0.0')


@app.route("/")
def hello():
  return "Hello World!"

