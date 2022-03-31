import os

from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
@app.route('/home')
def home_page():
    return render_template('home.html')



if __name__ == '__main__':
    os.environ['FLASK_APP'] = 'market.py'
    os.environ['FLASK_DEBUG'] = '1'
    os.system('flask run')
