from flask import Flask
from flask import render_template, url_for

application = Flask(__name__)

username = ''
password = ''


# method to render login page
@application.route('/login', methods=['GET', 'POST'])
def login():
    return render_template('login.html')


# method to render main page
@application.route('/')
def main():
    username = ''
    password = ''
    return render_template('index.html')


# method to render login page
@application.route('/login_page', methods=['GET', 'POST'])
def login_page():
    return render_template('login.html')


# method to render signup page
@application.route('/signup_page', methods=['GET', 'POST'])
def signup_page():
    return render_template('signup.html')


# method to render account page
@application.route('/account_page', methods=['GET', 'POST'])
def account_page():
    return render_template('account.html')


if __name__ == '__main__':
    application.run(debug=True)


      # Uploading data
    # step 0, Create s3 private bucket
    #
    # step 1, copy data to s3 private bucket
    #
    # step 2, parse data, skip re-download since we know we're not changing private bucket data
    # outside of this program
    #
    # step 3, populate table from input file