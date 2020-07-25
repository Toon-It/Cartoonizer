from flask import Flask, request, render_template

app = Flask(__name__)

@app.route("/")
def welcome():
    return render_template('basic.html')


@app.route('/login/', methods=['POST'])
def login():
    user = request.form['nm']
    opstring = 'Hey ' + user + ', Welcome to The Tinkerhub LFH Program'
    return opstring 

if __name__ == "__main__":
    app.run()