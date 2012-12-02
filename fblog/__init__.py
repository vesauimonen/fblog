import re
import configuration
from flask import Flask, request, render_template, redirect, url_for, flash, \
    abort
from flask.ext.login import LoginManager, login_required, login_user, \
    logout_user
from fblog.database import db_session
from fblog.models import Post, User, Anonymous, Pagination, \
    get_posts_for_page, count_all_posts
from jinja2 import evalcontextfilter, Markup, escape


app = Flask(__name__)

app.config.from_object(configuration)

login_manager = LoginManager()
login_manager.anonymous_user = Anonymous
login_manager.login_view = 'login'
login_manager.login_message = app.config['LOGIN_MESSAGE']


@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

login_manager.init_app(app)


@app.teardown_request
def shutdown_session(exception=None):
    db_session.remove()


@app.route('/', defaults={'page': 1})
@app.route('/page/<int:page>')
def display_posts(page):
    count = count_all_posts()
    print count
    posts = get_posts_for_page(page, app.config['PER_PAGE'], count)
    if not posts and page != 1:
        abort(404)
    pagination = Pagination(page, app.config['PER_PAGE'], count)
    return render_template('posts.html',
        pagination=pagination,
        posts=posts
        )


@app.route('/post/<int:id>')
def display_post(id):
    post = Post.query.get(id)
    if post is None:
        abort(404)
    return render_template('post.html', post=post)


@app.route('/add', defaults={'id': None}, methods=['GET', 'POST'])
@app.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def add_post(id):
    edit = True if id != None else False
    if edit and Post.query.get(id) == None:
        abort(404)
    if edit:
        post = Post.query.get(id)
    else:
        post = None
    if request.method == 'POST':
        if not edit:
            post = Post(request.form['title'], request.form['content'], [])
        if not (request.form['title'] and request.form['content']):
            flash('Both title and content need to be specified.')
            return render_template('add_post.html', post=post, edit=edit)
        else:
            if edit:
                post.title = request.form['title']
                post.content = request.form['content']
                db_session.commit()
                flash('Post edited.')
            else:
                db_session.add(post)
                db_session.commit()
                flash('New post submitted.')
            return redirect(url_for('display_posts'))
    return render_template('add_post.html', post=post, edit=edit)


@app.route('/delete/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_post(id):
    post = Post.query.get(id)
    if request.method == 'GET':
        return render_template('delete_post.html', post=post)
    if request.form['confirm'] == 'yes':
        db_session.delete(post)
        db_session.commit()
        flash('Post deleted.')
        return redirect(url_for('display_posts'))
    return redirect(url_for('display_posts'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter(
            User.username == request.form['username']).first()
        if user is None:
            flash('Invalid username.')
        elif not user.check_password(request.form['password']):
            flash('Invalid password.')
        else:
            if login_user(user):
                flash('You are logged in!')
                # Todo: req args next not working
                return redirect(request.args.get('next') or url_for('display_posts'))
            else:
                flash("Sorry, you couldn't be logged in.")
    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out.')
    return redirect(url_for('display_posts'))


def url_for_other_page(page):
    args = request.view_args.copy()
    args['page'] = page
    return url_for(request.endpoint, **args)
app.jinja_env.globals['url_for_other_page'] = url_for_other_page


_paragraph_re = re.compile(r'(?:\r\n|\r|\n){2,}')


@app.template_filter()
@evalcontextfilter
def nl2br(eval_ctx, value):
    result = u'\n\n'.join(u'<p>%s</p>' % p.replace('\n', '<br>\n')
        for p in _paragraph_re.split(escape(value)))
    if eval_ctx.autoescape:
        result = Markup(result)
    return result
