import datetime
import sqlalchemy
from sqlalchemy import Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from .db_session import SqlAlchemyBase


class Comments(SqlAlchemyBase):
    __tablename__ = 'comments'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    text = sqlalchemy.Column(sqlalchemy.Text, nullable=False)
    created_date = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now)
    user_id = sqlalchemy.Column(sqlalchemy.Integer, ForeignKey('users.id'))
    post_id = sqlalchemy.Column(sqlalchemy.Integer, ForeignKey('post.id'))

    user = relationship('data.users.User', back_populates='comments')
    post = relationship('data.post.Post', back_populates='comments')
