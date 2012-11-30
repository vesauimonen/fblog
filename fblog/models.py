from sqlalchemy import Table, Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from fblog.database import Base


associated_tags = Table('associated_tags', Base.metadata,
    Column('post_id', Integer, ForeignKey('posts.id')),
    Column('tag_id', Integer, ForeignKey('tags.id'))
)


class Post(Base):
    __tablename__ = 'posts'
    id = Column(Integer, primary_key=True)
    title = Column(String)
    content = Column(String)
    tags = relationship('Tag', secondary=associated_tags)

    def __init__(self, title, content, tags):
        self.title = title
        self.content = content
        self.tags = tags

    def __repr__(self):
        return "<Post ('%r', '%r')>" % (self.title, self.content)


class Tag(Base):
    __tablename__ = 'tags'
    id = Column(Integer, primary_key=True)
    name = Column(String(30))

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return '<Tag %r>' % (self.name)
