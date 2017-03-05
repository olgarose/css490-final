from flask import Flask
from flask import render_template, url_for

application = Flask(__name__)


# method to render main page
@application.route('/')
def main():
    return render_template('index.html')


# method to render login page
@application.route('/login', methods=['GET', 'POST'])
def login():
    return render_template('login.html')


if __name__ == '__main__':
    application.run(debug=True)
