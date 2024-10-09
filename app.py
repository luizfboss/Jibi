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

    if user:
        print("success!")
        # render_template("feed.html")
    else:
        print("fail.")

    return render_template("login.html")

@app.route('/register_user')
def register_user():
    return render_template("create_account.html")

def hash_password(password):
    """
        Helper function for add_user().
        Hashing function to hash passwords (to be stored securely in DB).
    """
    return hashlib.sha256(password.encode()).hexdigest()

@app.route('/add_user', methods=["POST"])
def add_user():
    db = get_db()
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    email = request.form['email']
    username = request.form['username']
    password = request.form['password']
    confirm_password = request.form['confirm_password']


    if password == confirm_password:
        # Hash the password
        hashed_password = hash_password(password)

        # See if username is unique
        try:
            db.execute('INSERT INTO users (username, password, first_name, last_name, email) VALUES (?, ?, ?, ?, ?)',
                       (username, hashed_password, first_name, last_name, email))
            db.commit()
            flash('New entry was successfully posted.','success')
            return redirect('/')

        except sqlite3.IntegrityError:
            flash("Username already exists. Please try another one.", 'error')
            return redirect('/register_user')

    else:
        flash('Passwords must match.')
        return redirect('register_user')
