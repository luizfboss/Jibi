import os
from sqlite3 import dbapi2 as sqlite3
from flask import Flask, session, request, g, redirect, url_for, render_template, flash
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

# LOGIN START
@app.route('/')
def login():
    return render_template("login.html")

@app.route('/user_auth', methods=["POST"])
def user_auth():
    """ Authenticates user entries given in the login form. """
    username = request.form.get('username')
    password = request.form.get('password')

    # Hash the password to compare with hashed passwords in DB
    hashed_password = hash_password(password)

    db = get_db()
    user = db.execute('SELECT * FROM users WHERE username = ? AND password = ?',
                      (username, hashed_password)).fetchone()

    if user:
        session['username'] = user[1].capitalize()
        session['first_name'] = user['first_name'].capitalize()
        return redirect(url_for('feed'))
    else:
        flash('Credentials do not match.')
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

        # See if username is unique. If not, warn user.
        try:
            db.execute('INSERT INTO users (username, password, first_name, last_name, email) VALUES (?, ?, ?, ?, ?)',
                       (username, hashed_password, first_name, last_name, email))
            db.commit()
            flash('Your new account has been created.')
            return redirect('/')

        except sqlite3.IntegrityError:
            flash("Username already exists. Please try another one.")
            return redirect('/register_user')

    else:
        flash('Passwords must match.')
        return redirect('register_user')
# LOGIN END

# ADD POST START
@app.route('/feed', methods=['GET'])
def feed():
    """ Render the feed page. """
    name = session.get('username')
    if not name:
        flash('You are not logged in.')
        return redirect(url_for('login'))

    first_name = session.get('first_name', "Guest")
    return render_template("feed.html", name=first_name)

@app.route('/add_post')
def add_post():
    return render_template('add_post.html')

@app.route('/submit_review', methods=["POST"])
def submit_review():
    flash('Your new review has been posted.')
    return redirect(url_for('feed'))

# TODO:
# - possibly: try to add the post to the database (create tables for each part of the post).
