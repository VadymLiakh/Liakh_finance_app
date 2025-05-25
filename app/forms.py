from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length
from wtforms import DecimalField, SelectField, TextAreaField, DateField
from wtforms.validators import DataRequired, Email

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    submit = SubmitField('Увійти')

class RegistrationForm(FlaskForm):
    username = StringField('Ім’я користувача', validators=[DataRequired(), Length(min=3, max=50)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Пароль', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Підтвердити пароль', validators=[
        DataRequired(), EqualTo('password', message='Паролі не збігаються')])
    submit = SubmitField('Зареєструватися')

class TransactionForm(FlaskForm):
    amount = DecimalField('Сума', places=2, validators=[DataRequired()])
    type = SelectField('Тип', choices=[('income', 'Дохід'), ('expense', 'Витрата')])
    category = SelectField('Категорія', coerce=int, validators=[DataRequired()])
    date = DateField('Дата', validators=[DataRequired()])
    description = TextAreaField('Опис')
    submit = SubmitField('Зберегти')

class CategoryForm(FlaskForm):
    name = StringField('Назва категорії', validators=[DataRequired()])
    submit = SubmitField('Додати')

class UpdateProfileForm(FlaskForm):
    username = StringField('Ім’я користувача', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Оновити профіль', name='update_profile')

class ChangePasswordForm(FlaskForm):
    current_password = PasswordField('Поточний пароль', validators=[DataRequired()])
    new_password = PasswordField('Новий пароль', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Підтвердьте новий пароль', validators=[
        DataRequired(), EqualTo('new_password')
    ])
    submit = SubmitField('Змінити пароль', name='change_password')

class ConfirmPasswordForm(FlaskForm):
    password = PasswordField('Підтвердіть пароль', validators=[DataRequired()])
    submit = SubmitField('Видалити акаунт')

class RequestResetForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Надіслати інструкцію')

class ResetPasswordForm(FlaskForm):
    password = PasswordField('Новий пароль', validators=[DataRequired()])
    confirm_password = PasswordField('Підтвердіть пароль', validators=[
        DataRequired(), EqualTo('password', message='Паролі мають збігатися.')
    ])
    submit = SubmitField('Змінити пароль')
