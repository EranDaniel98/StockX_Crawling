from flask import Flask, request, render_template

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('prediction.html')

@app.route('/', methods={'POST'})
def getvalue():
    url = request.form['url_input']
    
    print(url)
    return render_template("pass.html")

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5001, debug=True)
    
