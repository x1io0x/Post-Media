from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField
from wtforms.validators import Length, DataRequired


class EditProfile(FlaskForm):
    name = StringField('Имя', validators=[DataRequired()])
    surname = StringField('Фамилия', validators=[DataRequired()])
    username = StringField('Юзернейм', validators=[DataRequired(), Length(max=30)])
    age = IntegerField('Возраст', validators=[DataRequired()])
    submit = SubmitField('Сохранить данные')