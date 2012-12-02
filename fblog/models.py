import datetime
from math import ceil
from sqlalchemy import Table, Column, Integer, String, Boolean, DateTime, \
    ForeignKey, desc
from sqlalchemy.orm import relationship
from flask.ext.login import UserMixin, AnonymousUser
from fblog.database import Base
from werkzeug.security import generate_password_hash, \
     check_password_hash


associated_tags = Table('associated_tags', Base.metadata,
    Column('post_id', Integer, ForeignKey('posts.id')),
    Column('tag_id', Integer, ForeignKey('tags.id'))
)


class Post(Base):
    __tablename__ = 'posts'
    id = Column(Integer, primary_key=True)
    title = Column(String)
    content = Column(String)
    published = Column(DateTime, default=datetime.datetime.now)
    tags = relationship('Tag', secondary=associated_tags)

    def __init__(self, title, content, tags):
        self.title = title
        self.content = content
        self.tags = tags

    def __repr__(self):
        return "<Post %r>" % (self.title)


class Tag(Base):
    __tablename__ = 'tags'
    id = Column(Integer, primary_key=True)
    name = Column(String(30))

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return '<Tag %r>' % (self.name)


class User(Base, UserMixin):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String(30))
    password = Column(String)
    active = Column(Boolean)

    def __init__(self, username, password, active=True):
        self.username = username
        self.set_password(password)
        self.active = active

    def is_active(self):
        return self.active

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)


class Anonymous(AnonymousUser):
    name = u"Anonymous"


class Pagination(object):

    def __init__(self, page, per_page, total_count):
        self.page = page
        self.per_page = per_page
        self.total_count = total_count

    @property
    def pages(self):
        return int(ceil(self.total_count / float(self.per_page)))

    @property
    def has_prev(self):
        return self.page > 1

    @property
    def has_next(self):
        return self.page < self.pages

    def iter_pages(self, left_edge=2, left_current=2,
                   right_current=5, right_edge=2):
        last = 0
        for num in xrange(1, self.pages + 1):
            if num <= left_edge or \
               (num > self.page - left_current - 1 and \
                num < self.page + right_current) or \
               num > self.pages - right_edge:
                if last + 1 != num:
                    yield None
                yield num
                last = num


def get_posts_for_page(page, per_page, total_count):
    posts = Post.query.order_by(desc(Post.published))
    if total_count <= per_page * (page - 1):
        return []
    posts_for_page = []
    for i in range((page - 1) * per_page, page * per_page):
        if (total_count == i):
            break
        posts_for_page.append(posts[i])
    return posts_for_page


def count_all_posts():
    return len(Post.query.all())
