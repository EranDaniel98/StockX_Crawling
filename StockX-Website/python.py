from flask import Flask, request, render_template

app = Flask(__name__)

@app.route('./')
def index():
    return render_template('prediction.html')

@app.route('/get-text', methods=['GET', 'POST'])
def foo():
    url_ = request.form['input_url']
    return 'Hello %s have fun learning python <br/> <a href="/">Back Home</a>' % url_

if __name__ == '__main__':
    app.run(host = '0.0.0.0', port = 3000)
    
    
