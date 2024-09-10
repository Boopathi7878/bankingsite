from flask import Flask, render_template, request, redirect, url_for, session
from pymongo import MongoClient
import bcrypt

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # For session management

# MongoDB Connection
client = MongoClient('mongodb://localhost:27017/')
db = client['banking_system']

@app.route('/')
def index():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    users_collection = db['users']
    username = request.form['username']
    password = request.form['password']

    user = users_collection.find_one({'username': username})
    
    if user and bcrypt.checkpw(password.encode('utf-8'), user['password']):
        session['username'] = username  # Create session for the user
        return redirect(url_for('dashboard'))
    else:
        return "Invalid username or password. Please try again."

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        users_collection = db['users']
        accounts_collection = db['accounts']
        balances_collection = db['balances']
        cards_collection = db['cards']

        # Get form data
        username = request.form['username']
        password = request.form['password']
        account_number = request.form['account_number']
        account_holder_name = request.form['account_holder_name']
        address = request.form['address']
        mobile_number = request.form['mobile_number']
        balance = request.form['balance']
        card_number = request.form['card_number']
        card_holder_name = request.form['card_holder_name']
        expiration_date = request.form['expiration_date']
        cvv = request.form['cvv']
        card_type = request.form['card_type']

        # Check if username already exists
        if users_collection.find_one({'username': username}):
            return "Username already exists!"

        # Hash the password
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        # Insert user details into MongoDB collections
        users_collection.insert_one({'username': username, 'password': hashed_password})
        accounts_collection.insert_one({
            'account_number': account_number,
            'account_holder_name': account_holder_name,
            'address': address,
            'mobile_number': mobile_number
        })
        balances_collection.insert_one({
            'account_number': account_number,
            'account_holder_name': account_holder_name,
            'balance': balance
        })
        cards_collection.insert_one({
            'card_number': card_number,
            'card_holder_name': card_holder_name,
            'expiration_date': expiration_date,
            'cvv': cvv,
            'card_type': card_type
        })

        return redirect(url_for('index'))

    return render_template('signup.html')

@app.route('/dashboard')
def dashboard():
    if 'username' in session:
        username = session['username']
        return render_template('dashboard.html', username=username)
    else:
        return redirect(url_for('index'))

@app.route('/logout')
def logout():
    session.pop('username', None)  # Remove session
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
