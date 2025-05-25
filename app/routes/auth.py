from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from app.forms import LoginForm, RegistrationForm
from app.models import User, db

from app import mail
from flask_mail import Message
from app.forms import ResetPasswordForm
from app.forms import RequestResetForm
from app.models import Role


auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.password_hash, form.password.data):
            login_user(user)
            if user.role.name == 'admin':
                return redirect(url_for('admin.admin_dashboard'))
            else:
                return redirect(url_for('dashboard.index'))
        else:
            flash('Невірний email або пароль.', 'danger')
    return render_template('login.html', form=form)
    

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))

    form = RegistrationForm()
    if form.validate_on_submit():
        # Перевірка унікальності
        if User.query.filter_by(username=form.username.data).first():
            flash('Це ім’я вже зайняте.', 'danger')
            return render_template('register.html', form=form)
        if User.query.filter_by(email=form.email.data).first():
            flash('Цей email вже використовується.', 'danger')
            return render_template('register.html', form=form)

        # 🔹 Отримуємо роль "user" з таблиці roles
        default_role = Role.query.filter_by(name='user').first()
        if not default_role:
            flash("Не знайдено роль 'user'. Створіть її в базі даних.", 'danger')
            return render_template('register.html', form=form)

        # Створення нового користувача
        hashed_password = generate_password_hash(form.password.data)
        new_user = User(
            username=form.username.data,
            email=form.email.data,
            password_hash=hashed_password,
            role_id=default_role.id  # 🔹 Замість role='user'
        )
        db.session.add(new_user)
        db.session.commit()

        flash('Успішна реєстрація! Тепер увійдіть.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('register.html', form=form)


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Ви вийшли з акаунту.', 'info')
    return redirect(url_for('auth.login'))

@auth_bp.route('/reset_password', methods=['GET', 'POST'])
def reset_request():
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_reset_email(user)
            flash('Інструкція надіслана на вашу пошту.', 'info')
        else:
            flash('Користувача з такою поштою не знайдено.', 'danger')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_request.html', form=form)

from app.utils.email import send_reset_email

@auth_bp.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_token(token):
    user = User.verify_reset_token(token)
    if not user:
        flash('Невірний або прострочений токен', 'warning')
        return redirect(url_for('auth.reset_request'))

    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data)
        user.password_hash = hashed_password
        db.session.commit()
        flash('Ваш пароль оновлено. Тепер ви можете увійти.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/reset_token.html', form=form)

