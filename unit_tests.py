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
        self.test_add_user_success()
        rv = self.app.post('/user_auth', data=dict(
            username='johndoe',
            password='password123'  # Pass plain text password, hash it in the function
        ), follow_redirects=True)

        assert b'You look good today' in rv.data  # Assuming the feed page greets the user with "Welcome"
        assert b'John' in rv.data  # Assuming the feed page greets the user with "Welcome"



    def test_user_auth_fail_mismatch_password(self):
        """Test failed user authentication with wrong password."""
        rv = self.app.post('/user_auth', data=dict(
            username='johndoe',
            password='invalid_password'
        ))
        assert b'Credentials do not match.' in rv.data

    def test_user_auth_fail_mismatch_username(self):
        """Test failed user authentication with wrong username."""
        rv = self.app.post('/user_auth', data=dict(
            username='invalid_username',
            password='password123'
        ))
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

    # POST TESTS
    def test_add_post_page_loads(self):
        """Test that the add post page loads successfully."""
        self.test_add_user_success()  # Make sure a user is registered for the test
        self.app.post('/user_auth', data=dict(
            username='johndoe',
            password='password123'
        ), follow_redirects=True)  # Log in the user

        rv = self.app.get('/add_post', follow_redirects=True)  # Make a GET request to load the add post page

        # Check if the response contains the expected elements
        assert b'Add Your Review' in rv.data  # Assuming the title of the page is 'Add a New Post'
        assert b'Comic Book Title' in rv.data  # Check for the title input field
        assert b'Review' in rv.data  # Check for the review textarea
        assert b'Rating (out of 5 stars)' in rv.data  # Check for the stars input field
        assert b'Upload Comic Book Cover' in rv.data  # Check for the image upload field
        assert b'Submit Review' in rv.data  # Check for submit button

    # UNIT TESTS FOR LATER
    def test_add_post_and_submit_review(self):
        """Test the process of adding a post (comic book review) and submitting it successfully."""

        # Step 1: Access the add post page
        self.test_add_post_page_loads()
        rv = self.app.get('/add_post', follow_redirects=True)

        # Step 2: Submit the post via the submit_review route
        rv = self.app.post('/submit_review', data=dict(
            title='Spider-Man',
            review='Amazing comic!',
            stars='5'
        ), follow_redirects=True)

        # Check that the success message is flashed and the user is redirected to the feed
        assert b'Your new review has been posted.' in rv.data
        assert b'Add a Post' in rv.data  # Assuming the feed page contains the word 'Feed'

    # def test_feed_page_displays_post(self):
    #     """Test that the feed page displays the added post."""
    #     self.test_add_post_success()  # Add a post
    #     rv = self.app.get('/feed', follow_redirects=True)
    #     assert b'Spider-Man' in rv.data  # Check if post title appears in feed
    #     assert b'Amazing comic!' in rv.data  # Check if review appears in feed
    #
    # def test_feed_page_displays_username(self):
    #     """Test that the feed page displays the user's name after login."""
    #     self.test_add_user_success()  # Register user first
    #     self.app.post('/user_auth', data=dict(
    #         username='johndoe',
    #         password='password123'
    #     ), follow_redirects=True)  # Log in user
    #
    #     rv = self.app.get('/feed', follow_redirects=True)
    #     assert b'You look good today, John' in rv.data  # Assuming feed greets user by first name

if __name__ == '__main__':
    unittest.main()