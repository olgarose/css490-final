from __future__ import print_function
import boto3
from boto3.dynamodb.conditions import Key, Attr
from flask import Flask
from flask import render_template, redirect, url_for, request, jsonify, Markup, flash
import uuid

from twilio.rest import TwilioRestClient
import twilio.twiml

application = Flask(__name__)

username = ''
password = ''

access_key = 'AKIAJSVUOAS23R7X3XZA'
secret_key = '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'
dynamodb = boto3.resource('dynamodb', region_name='us-west-2')
table = dynamodb.Table('490final-userinfostore')

# TWILIO INFO
ACCOUNT_SID = "AC1a3f636ceb05e4559409a12976a0f9d6"
AUTH_TOKEN = "22fa61aef0c4e56ffc8e333dd8f1bf33"
client = TwilioRestClient(ACCOUNT_SID, AUTH_TOKEN)
twilio_phone = '2065390317'

contacts_table = dynamodb.Table('css490-final-contacts-list')


@application.route('/account_page', methods=['GET', 'POST'])
def account_page():
    contacts = contacts_table.scan()['Items']
    contacts_to_display = {}

    for contact in contacts:
        name = contact['first_name'] + ' ' + contact['last_name']
        contacts_to_display[name] = contact['phone_number']

    return render_template('account.html', contacts=contacts_to_display)


# KEEPING OLD CODE FOR NOW, MIGHT NEED FOR REFERENCE
# # method to render account page
# @application.route('/account_page', methods=['GET', 'POST'])
# def account_page():
#     response = contacts_table.scan()
#     response = response['Items']
#     contacts_to_display = {}
#     x = 0
#     for i in response:
#         contacts_to_display[x] = {'first': i['first_name'], 'number': i['phone_number']}
#         x += 1
#     return render_template('account.html', contacts=contacts_to_display)


@application.route('/send_message', methods=['GET', 'POST'])
def send_message():
    contacts = request.form.getlist('select_contacts')
    for contact in contacts:
        phone_number = contact.split()[-1]
        try:
            client.messages.create(
                to=phone_number,
                from_=twilio_phone,
                body=request.form["message"],
                # media_url="https://c1.staticflickr.com/3/2899/14341091933_1e92e62d12_b.jpg",
            )
        except:
            print('NOT VALID NUMBER' + contact.split()[-1])
    return redirect('account_page')


@application.route('/edit_contacts', methods=['GET', 'POST'])
def edit_contacts_page():
    contacts = contacts_table.scan()['Items']
    contacts_to_display = {}

    for contact in contacts:
        name = contact['first_name'] + ' ' + contact['last_name']
        contacts_to_display[name] = contact['phone_number']

    return render_template('edit_contacts.html', contacts=contacts_to_display)


@application.route('/edit_contact', methods=['GET', 'POST'])
def edit_contact():
    print('First name ' + request.form['first_name'])
    return redirect('edit_contacts')


# this function will add contact to the contacts_database
@application.route("/add_contact", methods=['POST', 'GET'])
def add_contact():
    # getting names to query from webrequest
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    phone = request.form['phone']

    # if first name or phone number are empty - NEED TO DISPLAY ERROR MESSAGE
    if len(first_name) == 0 or len(phone) == 0:
        result_message = Markup("<h4 style=\"color: #e21f46;\">PLEASE ENTER VALUES IN ALL REQUIRED FIELDS</h4>")
        flash(result_message)
        return redirect("/account_page")
    else:
        user_id = str(uuid.uuid4())
        if not last_name:
            last_name = ' '
        contact = {'contact_id': user_id, 'first_name': first_name, 'last_name': last_name, 'phone_number': phone}

    contacts_table.put_item(Item=contact)

    return redirect("/account_page")


def create_table():
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


def response_message():
    """Respond to incoming calls with a simple text message."""

    resp = twilio.twiml.Response()
    resp.message("Hello, Mobile Monkey")
    return str(resp)


# method to render main page
@application.route('/', methods=['GET', 'POST'])
def main():
    create_table()
    response_message()
    return render_template('index.html')


# method to render login page
@application.route('/login_page', methods=['GET', 'POST'])
def login_page():
    return render_template('login.html')


@application.route('/login', methods=['GET', 'POST'])
def login():
    create_table()
    email_input = request.form.get("email")
    password_input = request.form.get("password")

    # print("email: ", email_input, "\npassword: ", password_input)
    # return render_template('login.html')
    return redirect("/account_page")


# method to render login page
@application.route('/signup_page', methods=['GET', 'POST'])
def signup_page():
    return render_template('signup.html')


# method to render sign up page
@application.route('/signup', methods=['GET', 'POST'])
def signup():
    create_table()
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


if __name__ == '__main__':
    application.secret_key = 'cUAaWI0ALM09wzhWmwV/4rJlBK8Ce2N1fzlJI/o+'
    application.run(debug=True)
