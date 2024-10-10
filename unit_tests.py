import os
import app
import unittest
import tempfile

class FlaskrTestCase(unittest.TestCase):
    def setUp(self):
        self.db_fd, app.app.config['DATABASE'] = tempfile.mkstemp()
        app.app.testing = True
        self.app = app.app.test_client()
        with app.app.app_context():
            app.init_db()

    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(app.app.config['DATABASE'])

    def test_login_page_loads(self):
        """Test that the login page loads successfully with correct title."""
        rv = self.app.get('/')
        assert b'Jibi - The Comic Book Review Platform' in rv.data
        assert b'Login' in rv.data

    def test_register_user_page_loads(self):
        """Test that the registration page loads successfully with form fields."""
        rv = self.app.get('/register_user')
        assert b'Create Account' in rv.data
        assert b'First name' in rv.data
        assert b'Last name' in rv.data
        assert b'Email' in rv.data
        assert b'Username' in rv.data
        assert b'Password' in rv.data
        assert b'Confirm Password' in rv.data

    def test_user_auth_success(self):
        """Test successful user authentication."""
        # Add user to database first
        self.test_add_user_success()

        # Simulate a GET request with valid username and password in the query string
        # Use query_string for GET requests and data for POST requests.
        rv = self.app.get('/user_auth', query_string=dict(
            username='johndoe',
            password='password123'  # Pass plain text password, hash it in the function
        ))

        # Check if the response contains the expected data
        assert b'You look good today,' in rv.data

    def test_user_auth_fail_mismatch_password(self):
        """Test failed user authentication with wrong password."""
        # Simulate a GET request with invalid credentials
        rv = self.app.get('/user_auth', query_string=dict(
            username='johndoe',
            password='invalid_password'))

        # Check if the login page is rendered and flash message is displayed
        assert b'Credentials do not match.' in rv.data

    def test_user_auth_fail_mismatch_username(self):
        """Test failed user authentication with wrong username."""
        # Simulate a GET request with invalid credentials
        rv = self.app.get('/user_auth', query_string=dict(
            username='invalid_username',
            password='password123'))

        # Check if the login page is rendered and flash message is displayed
        assert b'Credentials do not match.' in rv.data

    def test_add_user_success(self):
        """Test successful user registration."""
        rv = self.app.post('/add_user', data=dict(
            first_name='John',
            last_name='Doe',
            email='john.doe@example.com',
            username='johndoe',
            password='password123',
            confirm_password='password123'
        ), follow_redirects=True)
        assert b'Your new account has been created.' in rv.data

    def test_add_user_password_mismatch(self):
        """Test user registration fails if passwords don't match."""
        self.test_add_user_success() # adds a user with a given username

        # add another user with the same username as the one in the function above
        rv = self.app.post('/add_user', data=dict(
            first_name='John',
            last_name='Doe',
            email='john.doe@example.com',
            username='johndoe',
            password='password123',
            confirm_password='wrongpassword'
        ), follow_redirects=True)
        assert b'Passwords must match.' in rv.data

    def test_add_user_duplicate_username(self):
        """Test user registration fails if username already exists."""
        # Flash message: Username already exists. Please try another one.
        """Test user registration fails if username already exists."""
        self.test_add_user_success()
        rv = self.app.post('/add_user', data=dict(
            first_name='John',
            last_name='Doe',
            email='john.doe@example.com',
            username='johndoe',
            password='password123',
            confirm_password='password123'
        ), follow_redirects=True)
        assert b'Username already exists. Please try another one.' in rv.data

if __name__ == '__main__':
    unittest.main()