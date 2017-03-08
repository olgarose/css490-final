from __future__ import print_function
import time
import boto3, os, requests, shutil
from boto3.dynamodb.conditions import Key, Attr
from flask import Flask
from flask import render_template, redirect, url_for, request, jsonify, Markup, flash
import twilio.twiml
import uuid

application = Flask(__name__)

username = ''
password = ''

access_key = 'AKIAJSVUOAS23R7X3XZA'
secret_key = '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'
dynamodb = boto3.resource('dynamodb', region_name='us-west-2')
table = dynamodb.Table('490final-userinfostore')
callers = {
    "+14158675309": "Curious George",
    "+14158675310": "Boots",
    "+14158675311": "Virgil",
}
contacts_table = dynamodb.Table('css490-final-contacts-list')


# this function will add contact to the contacts_database
@application.route("/add_contact", methods=['POST', 'GET'])
def add_contact():
    # getting names to query from webrequest
    firstname = request.form['first_name']
    lastname = request.form['last_name']
    phone = request.form['phone']

    if len(firstname) or len(phone) == 0:

        return redirect("/account_page")

    user_id = str(uuid.uuid4())


    if len(lastname) == 0:
        new_item = {'contact_id': user_id, 'first_name': firstname, 'phone_number': phone}
    else:
        new_item = {'contact_id': user_id, 'first_name': firstname, 'last_name': lastname, 'phone_number': phone}

    contacts_table.put_item(Item=new_item)

    return redirect("/account_page")


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


# method to render main page
@application.route('/')
def main():
    username = ''
    password = ''
    createTable()
    return render_template('index.html')


# method to render login page
@application.route('/account_page', methods=['GET', 'POST'])
def account_page():
    return render_template('account.html')


# method to render login page
@application.route('/login_page', methods=['GET', 'POST'])
def login_page():
    return render_template('login.html')


@application.route('/login', methods=['GET', 'POST'])
def login():
    createTable()
    email_input = request.form.get("email")
    password_input = request.form.get("password")

    # print("email: ", email_input, "\npassword: ", password_input)
    return render_template('login.html')


# method to render login page
@application.route('/signup_page', methods=['GET', 'POST'])
def signup_page():
    return render_template('signup.html')

# method to render sign up page
@application.route('/signup', methods=['GET', 'POST'])
def signup():
    createTable()
    email_input = request.form.get("email")
    password_input = request.form.get("password")
    password_verify_input = request.form.get("password_verify")
    first_name_input = request.form.get("first_name")
    last_name_input = request.form.get("last_name")

    if password_input != password_verify_input:
        password_error = Markup("<p> Passwords provided do not match, please try again.</p>")
        flash(password_error)
        return render_template('signup.html')

    response = table.query(KeyConditionExpression=Key('email').eq(email_input))
    items = response['Items']
    if len(items) > 0:
        dup_email_error = Markup("<p> The email is already in use with our services, please log in<p>")
        flash(dup_email_error)
        return render_template('signup.html')

    dict = {'email': email_input, 'password': password_input,
            'first_name': first_name_input, 'last_name': last_name_input}
    table.put_item(Item=dict)

    return render_template('login.html')


# # method to render register page
# @application.route('/register', methods=['GET', 'POST'])
# def register():
#     createTable()
#     email_input = request.form.get("email")
#     password_input = request.form.get("password")
#     password_verify_input = request.form.get("password_verify")
#     first_name_input = request.form.get("first_name")
#     last_name_input = request.form.get("last_name")
#
#     if password_input != password_verify_input:
#         password_error = Markup("<p> Passwords provided do not match, please try again.</p>")
#         flash(password_error)
#         return render_template('signup.html')
#
#     response = table.query(KeyConditionExpression=Key('email').eq(email_input))
#     items = response['Items']
#     if len(items) > 0:
#         dup_email_error = Markup("<p> The email is already in use with our services, please log in<p>")
#         flash(dup_email_error)
#         return render_template('signup.html')
#
#     dict={'email': email_input, 'password': password_input,
#         'first_name': first_name_input, 'last_name': last_name_input}
#     table.put_item(Item=dict)
#
#     return render_template('login.html')


# method to render signup page
@application.route('/send_message', methods=['GET', 'POST'])
def send_message():
    """Respond and greet the caller by name."""

    from_number = request.values.get('From', None)
    if from_number in callers:
        message = callers[from_number] + ", thanks for the message!"
    else:
        message = "Monkey, thanks for the message!"

    resp = twilio.twiml.Response()
    print (resp.message(message))

    return render_template('account.html')


if __name__ == '__main__':
    application.secret_key = 'cUAaWI0ALM09wzhWmwV/4rJlBK8Ce2N1fzlJI/o+'
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
