import os
from sqlite3 import dbapi2 as sqlite3
from flask import Flask, request, g, redirect, url_for, render_template, flash

import hashlib # hash passwords

app = Flask(__name__)

# Load default config and override config from an environment variable
app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'jibi.db'),
    SECRET_KEY='development key',
))


def connect_db():
    """Connects to the specific database."""
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv


def init_db():
    """Initializes the database."""
    db = get_db()
    with app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()


@app.cli.command('initdb')
def initdb_command():
    """Creates the database tables."""
    init_db()
    print('Initialized the database.')


def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db


# automatically run this command at the end of any request
@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()

@app.route('/')
def login():
    return render_template("login.html")

@app.route('/user_auth', methods=['GET'])
def user_auth():
    """ Authenticates user entries given in the login form. """
    username = request.args.get('username')
    password = request.args.get('password')

    # Hash the password to compare with hashed passwords in DB
    # hashed_password = hash_password(password)

    db = get_db()
    user = db.execute('SELECT * FROM users WHERE username = ? AND password = ?',
                        (username, password)).fetchone()
    db.close()

    if user:
        print("success!")
        # render_template("feed.html")
    else:
        print("fail.")

    return render_template("login.html")

@app.route('/register_user')
def register_user():
    return render_template("create_account.html")






#@app.route('/add_user')
#def add_user():
#    db = get_db()
#    username = request.form['username']
#    password = request.form['password']
#
#    # Hash the password
#    hashed_password = hash_password(password)
#
#    # Insert the new user into the database
#    db.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, hashed_password))
#    db.commit()
#
#    return render_template('login.html')