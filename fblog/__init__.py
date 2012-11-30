from flask import Flask, request, render_template, redirect, url_for, flash
from flask.ext.login import (LoginManager, current_user, login_required,
                            login_user, logout_user, UserMixin, AnonymousUser,
                            confirm_login, fresh_login_required)
from fblog.database import db_session
from fblog.models import Post, User, Anonymous

# configuration
DATABASE = '/tmp/flaskr.db'
DEBUG = True
SECRET_KEY = 'development key'
USERNAME = 'admin'
PASSWORD = 'default'
USERS = {
    1: User(USERNAME, 1, PASSWORD)
}
USER_NAMES = dict((u.name, u) for u in USERS.itervalues())

app = Flask(__name__)

app.config.from_object(__name__)

login_manager = LoginManager()

login_manager.anonymous_user = Anonymous
login_manager.login_view = 'login'
login_manager.login_message = u'Please log in to access this page.'
login_manager.refresh_view = 'reauth'


@login_manager.user_loader
def load_user(id):
    return USERS.get(int(id))


login_manager.init_app(app)


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


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME']:
            flash('Invalid username.')
        elif request.form['password'] != app.config['PASSWORD']:
            flash('Invalid password.')
        else:
            username = request.form['username']
            if login_user(USER_NAMES[username]):
                flash('You are logged in!')
                return redirect(request.args.get('next') or url_for('display_posts'))
            else:
                flash("Sorry, you couldn't be logged in.")
    return render_template('login.html', error=error)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out.')
    return redirect(url_for('display_posts'))
