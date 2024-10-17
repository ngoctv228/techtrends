import sqlite3
import logging
import sys
from flask import Flask, jsonify, json, render_template, request, url_for, redirect, flash
from werkzeug.exceptions import abort

logging.basicConfig(stream = sys.stderr ,level=logging.DEBUG, format = (
                                                    '%(levelname)s:\t'
                                                    '%(name)s:'
                                                    '%(asctime)s, '
                                                    '%(message)s'
                                                ))

# Function to get a database connection.
# This function connects to database with the name `database.db`
def get_db_connection():
    connection = sqlite3.connect('database.db')
    connection.row_factory = sqlite3.Row
    return connection

def log_connection(connection, action_name): 
     connection.execute('UPDATE connections\
                        SET count = count + 1,\
                        last_connection = CURRENT_TIMESTAMP\
                        WHERE action_name = ?', (action_name,))
     connection.commit()
     return connection


# Function to get a post using its ID
def get_post(post_id):
    connection = get_db_connection()
    post = connection.execute('SELECT * FROM posts WHERE id = ?',
                        (post_id,)).fetchone()
    
    # log connection
    log_connection(connection, "POST_GET_BY_ID")

    connection.close()
    return post

# Define the Flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your secret key'

# Define the main route of the web application 
@app.route('/')
def index():
    connection = get_db_connection()
    posts = connection.execute('SELECT * FROM posts').fetchall()

    # log connection
    log_connection(connection, "POST_GET_ALL")

    connection.close()
    return render_template('index.html', posts=posts)

# Define how each individual article is rendered 
# If the post ID is not found a 404 page is shown
@app.route('/<int:post_id>')
def post(post_id):
    post = get_post(post_id)
    if post is None:
      logging.info('Article with ID "%d" not found!', post_id)
      return render_template('404.html'), 404
    else:
      logging.info('Article "%s" retrieved!', post["title"])
      return render_template('post.html', post=post)

# Define the About Us page
@app.route('/about')
def about():
    logging.info('About Us page is retrieved')
    return render_template('about.html')

# Define the post creation functionality 
@app.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            flash('Title is required!')
        else:
            connection = get_db_connection()
            connection.execute('INSERT INTO posts (title, content) VALUES (?, ?)',
                         (title, content))
            # log connection
            log_connection(connection, "POST_CREATE")

            connection.commit()
            logging.info('Article "%s" is created', title)
            connection.close()

            return redirect(url_for('index'))

    return render_template('create.html')

# Define the health check functionality
@app.route('/healthz', methods = ['GET'])
def healthz():
    data = { 
            "result" : "OK - healthy"
        } 
    return jsonify(data)

# Define the metrics functionality
@app.route('/metrics', methods = ['GET'])
def metrics():
    connection = get_db_connection()
    postCount = connection.execute('SELECT COUNT(*) FROM posts').fetchone()
    connectionCount = connection.execute('SELECT SUM(count) FROM connections').fetchone()
    connection.close()
    data = { 
            "db_connection_count" : connectionCount[0],
            "post_count": postCount[0]
        } 
    return jsonify(data)

# start the application on port 3111
if __name__ == "__main__":
   app.run(host='0.0.0.0', port='3111')
