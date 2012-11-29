from flask import Flask, render_template
from fblog.database import db_session
from fblog.models import Post

app = Flask(__name__)


@app.teardown_request
def shutdown_session(exception=None):
    db_session.remove()


@app.route('/')
def display_posts():
    posts = Post.query.all()
    for post in posts:
        if len(post.content) > 250:
            post.content = post.content[:250] + '...'
    return render_template('posts.html', posts=posts)
