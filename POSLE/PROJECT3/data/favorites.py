import sqlalchemy
from sqlalchemy import orm
from sqlalchemy.orm import relationship

from .db_session import SqlAlchemyBase


class Favorite(SqlAlchemyBase):
    __tablename__ = 'favorites'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    user_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"))
    post_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("post.id"))

    user = orm.relationship('User')
    post = relationship("Post")
