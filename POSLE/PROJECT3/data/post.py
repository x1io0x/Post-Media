import datetime
import sqlalchemy
from sqlalchemy import orm
from sqlalchemy.orm import relationship

from .db_session import SqlAlchemyBase


class Post(SqlAlchemyBase):
    __tablename__ = 'post'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    title = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    content = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    image = sqlalchemy.Column(sqlalchemy.String(200), nullable=True)
    created_date = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now)
    is_private = sqlalchemy.Column(sqlalchemy.Boolean, default=True)

    user_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('users.id'))
    user = orm.relationship('User')
    categories = orm.relationship('Category', secondary='association', backref='post')

    likes = relationship("Like", back_populates="post")
    like_count = sqlalchemy.Column(sqlalchemy.Integer, default=0)

    comments = relationship('data.comments.Comments', back_populates='post', order_by='data.comments.Comments.created_date.desc()')

    def __repr__(self):
        return f'<Post {self.title}>'
