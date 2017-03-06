from __future__ import print_function
import time
import requests_cache
import boto3, os, requests, shutil
from boto3.dynamodb.conditions import Key, Attr
from flask import Flask
from flask import render_template, url_for, request, jsonify, Markup, flash

application = Flask(__name__)

<<<<<<< HEAD
username = ''
password = ''


# method to render login page
@application.route('/login', methods=['GET', 'POST'])
def login():
    return render_template('login.html')
=======
access_key = 'AKIAJSVUOAS23R7X3XZA'
secret_key = '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'
dynamodb = boto3.resource('dynamodb', region_name='us-west-2')
table = dynamodb.Table('490final-userinfostore')

def createTable():
    try:
        table = dynamodb.create_table(
            TableName='490final-userinfostore',
            KeySchema=[
                {
                    'AttributeName': 'email',
                    'KeyType': 'HASH'
                },
                {
                    'AttributeName': 'last_name',
                    'KeyType': 'RANGE'
                }
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'email',
                    'AttributeType': 'S'
                },
                {
                    'AttributeName': 'last_name',
                    'AttributeType': 'S'
                },
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 5,
                'WriteCapacityUnits': 5
            }
        )
        return
    except:
        print('Table already made')
        return
>>>>>>> refs/heads/Shane


# method to render main page
@application.route('/')
def main():
<<<<<<< HEAD
    username = ''
    password = ''
=======
    createTable()
>>>>>>> refs/heads/Shane
    return render_template('index.html')


# method to render login page
<<<<<<< HEAD
@application.route('/login_page', methods=['GET', 'POST'])
def login_page():
=======
@application.route('/login', methods=['GET', 'POST'])
def login():
    createTable()
    email_input = request.form.get("email")
    password_input = request.form.get("password")

    #print("email: ", email_input, "\npassword: ", password_input)
    return render_template('login.html')

# method to render sign up page
@application.route('/signup', methods=['GET', 'POST'])
def signup():
    createTable()
    return render_template('signup.html')

# method to render register page
@application.route('/register', methods=['GET', 'POST'])
def register():
    createTable()
    email_input = request.form.get("email")
    password_input = request.form.get("password")
    password_verify_input = request.form.get("password_verify")
    first_name_input = request.form.get("first_name")
    last_name_input = request.form.get("last_name")

    if(password_input != password_verify_input):
        password_error = Markup("<p> Passwords provided do not match, please try again.</p>")
        flash(password_error)
        return render_template('signup.html')

    response = table.query(KeyConditionExpression=Key('email').eq(email_input))
    items = response['Items']
    if len(items) > 0:
        dup_email_error = Markup("<p> The email is already in use with our services, please log in<p>")
        flash(dup_email_error)
        return render_template('signup.html')

    dict={'email': email_input, 'password': password_input,
        'first_name': first_name_input, 'last_name': last_name_input}
    table.put_item(Item=dict)

>>>>>>> refs/heads/Shane
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
    application.secret_key='cUAaWI0ALM09wzhWmwV/4rJlBK8Ce2N1fzlJI/o+'
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