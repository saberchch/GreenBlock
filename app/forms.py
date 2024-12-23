from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField
from wtforms.validators import DataRequired, Length

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    secret_phrase = PasswordField('Secret Phrase', validators=[DataRequired(), Length(min=6, max=100)])
    profession = SelectField('Profession', choices=[
        ('civil_engineer', 'Civil Engineer'),
        ('mechanical_engineer', 'Mechanical Engineer'),
        ('electronics_engineer', 'Electronics Engineer')
    ], validators=[DataRequired()])
    submit = SubmitField('Register')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    secret_phrase = PasswordField('Secret Phrase', validators=[DataRequired()])
    submit = SubmitField('Login') 