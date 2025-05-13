from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, BooleanField, SubmitField
from flask_wtf.file import FileField
from wtforms.validators import DataRequired


class PostForm(FlaskForm):
    title = StringField('Заголовок', validators=[DataRequired()])
    content = TextAreaField("Содержание")
    image = FileField('Изображение')
    is_private = BooleanField("Приватный пост")
    submit = SubmitField('Применить')
