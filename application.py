from __future__ import print_function
import boto3, flask_login, requests
from boto3.dynamodb.conditions import Key, Attr
from flask import Flask, render_template, url_for, request, Markup, flash, redirect, session, abort
import uuid
from tabledef import *
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user
from twilio.rest import TwilioRestClient

application = Flask(__name__)
application.secret_key = 'cUAaWI0ALM09wzhWmwV/4rJlBK8Ce2N1sdfsdgsdsdgaJKJL3rq3d3wdod3qfzlJI/o+'


username = 'example@example.com'
password = ''

access_key = 'removed for security purposes'
secret_key = 'removed for security purposes'
dynamodb = boto3.resource('dynamodb', aws_access_key_id=access_key, aws_secret_access_key=secret_key, region_name='us-west-2')
table = dynamodb.Table('490final-userinfostore')
login_manager = flask_login.LoginManager()
login_manager.init_app(application)
login_manager.login_view = "login"

# TWILIO INFO
ACCOUNT_SID = "removed for security purposes"
AUTH_TOKEN = "removed for security purposes"
client = TwilioRestClient(ACCOUNT_SID, AUTH_TOKEN)
twilio_phone = '2065390317'

contacts_table = dynamodb.Table('css490-final-contacts-list')


@application.route('/account_page', methods=['GET', 'POST'])
def account_page():
    if not session.get('logged_in'):
        return render_template('login.html')
    contacts = contacts_table.scan()['Items']
    contacts_to_display = {}

    for contact in contacts:
        if username == contact['user']:
            name = contact['first_name'] + ' ' + contact['last_name']
            contacts_to_display[name] = contact['phone_number']

    return render_template('account.html', contacts=contacts_to_display)


@application.route('/send_message', methods=['GET', 'POST'])
def send_message():
    contacts = request.form.getlist('select_contacts')
    for contact in contacts:
        phone_number = contact.split('|')[-1].strip()
        try:
            client.messages.create(
                to=phone_number,
                from_=twilio_phone,
                body=request.form["message"],
                # media_url="https://c1.staticflickr.com/3/2899/14341091933_1e92e62d12_b.jpg",
            )
        except:
            print('NOT VALID NUMBER ' + phone_number)
    return redirect('account_page')


@application.route('/edit_contacts', methods=['GET', 'POST'])
def edit_contacts_page():
    if not session.get('logged_in'):
        return render_template('login.html')
    contacts = contacts_table.scan()['Items']
    contacts_to_display = {}

    for contact in contacts:
        if username == contact['user']:
            name = contact['first_name'] + ' ' + contact['last_name']
            contacts_to_display[name] = contact['phone_number']

    return render_template('edit_contacts.html', contacts=contacts_to_display)


@application.route('/edit_contact', methods=['GET', 'POST'])
def edit_contact():
    contacts_to_delete = request.form.getlist('select_contacts')
    all_contacts = contacts_table.scan()['Items']
    phones = []
    names = []

    for contact in contacts_to_delete:
        split_contact = contact.split('|')
        names += [str(split_contact[0].strip())]
        phones += [str(split_contact[-1].strip())]
        
    for c in all_contacts:
        for n, p in zip(names, phones):
            if n == c['first_name'] + ' ' + c['last_name'] or n == c['first_name'] and p == c['phone_number']:
                global username
                key = {
                            'user': username,
                            'contact_id': c['contact_id']
                        }
                contacts_table.delete_item(Key=key)
    return redirect('edit_contacts')


@application.route('/back_to_messages', methods=['POST'])
def back_to_messages():
    return redirect('account_page')


# this function will add contact to the contacts_database
@application.route("/add_contact", methods=['POST', 'GET'])
def add_contact():
    # getting names to query from webrequest
    first_name = request.form['first_name'].strip()
    last_name = request.form['last_name'].strip()
    phone = request.form['phone'].strip()

    # if first name or phone number are empty - NEED TO DISPLAY ERROR MESSAGE
    if len(first_name) == 0 or len(phone) == 0:
        result_message = Markup("<h4 style=\"color: white;\">PLEASE ENTER VALUES IN ALL REQUIRED FIELDS</h4>")
        flash(result_message)
        return redirect("/edit_contacts")
    else:
        user_id = str(uuid.uuid4())
        if not last_name:
            last_name = ' '
        global username
        contact = {'user': username, 'contact_id': user_id, 'first_name': first_name, 'last_name': last_name,
                   'phone_number': phone}

    contacts_table.put_item(Item=contact)

    return redirect("/edit_contacts")


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


# method to render main page
@application.route('/')
def main():
    if not session.get('logged_in'):
        return render_template('login.html')
    else:
        return render_template('index.html')


# method to render login page
@application.route('/login_page', methods=['GET', 'POST'])
def login_page():
    if request.method == 'POST':
        engine = create_engine('sqlite:///tutorial.db', echo=True)
        # create session
        Session = sessionmaker(bind=engine)
        s = Session()

        email_input = request.form.get("email")
        password_input = request.form.get("password")

        query = s.query(User).filter(User.username.in_([email_input]), User.password.in_([password_input])).first()

        s.close()
        # print("\n\nquery: ", query, "\n\n")
        if query:
            session['logged_in'] = True
            login_success = 'Login Successful!'
            print(login_success)
            global username
            username = email_input
            return account_page()
        else:
            wrong_cred_err = Markup("<p> Invalid credentials<p>")
            flash(wrong_cred_err)
            return render_template('login.html')
        return redirect("/account_page")
    return render_template('login.html')


@application.route('/logout', methods=['GET', 'POST'])
def logout():
    session['logged_in'] = False
    return redirect('/')


# method to render signup page
@application.route('/signup_page', methods=['GET', 'POST'])
def signup_page():
    if request.method == 'POST':
        engine = create_engine('sqlite:///tutorial.db', echo=True)
        # create session
        Session = sessionmaker(bind=engine)
        s = Session()

        # pull in data from form
        email_input = request.form.get("email")
        password_input = request.form.get("password")
        password_verify_input = request.form.get("password_verify")
        first_name_input = request.form.get("first_name")
        last_name_input = request.form.get("last_name")

        if password_input != password_verify_input:
            print("Mismatched passwords")
            password_error = Markup("<p> Passwords provided do not match, please try again.</p>")
            flash(password_error)
            return render_template('signup.html')

        try:
            query = s.query(User).filter(User.username.in_([email_input]))
            result = query.first()
            if result:
                print("Duplicate email")
                dup_email_error = Markup("<p> The email is already in use with our services, please log in<p>")
                flash(dup_email_error)
                return render_template('signup.html')
        except:
            print("Query Error")
            return render_template('signup.html')

        user = User(email_input, password_input, email_input, first_name_input, last_name_input)

        s.add(user)
        s.commit()
        s.close()

        return render_template('login.html')
    return render_template('signup.html')


if __name__ == '__main__':
    # session['logged_in'] = False
    application.run(debug=True)
