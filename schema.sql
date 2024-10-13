DROP TABLE IF EXISTS users;
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    email TEXT NOT NULL
);

CREATE TABLE posts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,                      -- Foreign key linking to the user who posted the review
    title TEXT NOT NULL,                  -- Comic book title
    review TEXT NOT NULL,                 -- Review content
    stars INTEGER CHECK(stars BETWEEN 1 AND 5), -- Rating (1 to 5 stars)
    image_filename TEXT,                  -- Name of the uploaded image file
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, -- Timestamp for when the post was created
    FOREIGN KEY (user_id) REFERENCES users(id)  -- User ID links to the users table
);
