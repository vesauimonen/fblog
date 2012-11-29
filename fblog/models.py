from sqlalchemy import Column, Integer, String
from fblog.database import Base


class Post(Base):
    __tablename__ = 'posts'
    id = Column(Integer, primary_key=True)
    title = Column(String)
    content = Column(String)

    def __init__(self, title, content):
        self.title = title
        self.content = content

    def __repr__(self):
        return "<Post ('%r', '%r')>" % (self.title, self.content)
