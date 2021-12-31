''' Sets up the Flask app. The routes for the app are within views.py'''

from flask import Flask

app = Flask(__name__)

app.config['DEBUG'] = True

from views import *

if __name__ == '__main__':
    app.debug = True
    app.run()
