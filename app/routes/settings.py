from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from app.models import db, User
from app.forms import UpdateProfileForm, ChangePasswordForm, ConfirmPasswordForm

settings_bp = Blueprint('settings', __name__, url_prefix='/settings')

@settings_bp.route('/', methods=['GET', 'POST'])
@login_required
def index():
    profile_form = UpdateProfileForm(obj=current_user)
    password_form = ChangePasswordForm()

    if profile_form.validate_on_submit() and 'update_profile' in request.form:
        current_user.username = profile_form.username.data
        current_user.email = profile_form.email.data
        db.session.commit()
        flash('Профіль оновлено.', 'success')
        return redirect(url_for('settings.index'))

    if password_form.validate_on_submit() and 'change_password' in request.form:
        if not check_password_hash(current_user.password_hash, password_form.current_password.data):
            flash('Неправильний поточний пароль.', 'danger')
        else:
            current_user.password_hash = generate_password_hash(password_form.new_password.data)
            db.session.commit()
            flash('Пароль оновлено.', 'success')
            return redirect(url_for('settings.index'))

    return render_template('settings/index.html', profile_form=profile_form, password_form=password_form)

@settings_bp.route('/delete', methods=['GET', 'POST'])
@login_required
def delete_account():
    form = ConfirmPasswordForm()
    if form.validate_on_submit():
        if check_password_hash(current_user.password_hash, form.password.data):
            user = User.query.get(current_user.id)
            logout_user()
            db.session.delete(user)
            db.session.commit()
            flash('Акаунт видалено.', 'success')
            return redirect(url_for('auth.login'))
        else:
            flash('Невірний пароль.', 'danger')
    return render_template('settings/delete_account.html', form=form)

@settings_bp.route('/toggle-theme', methods=['POST'])
@login_required
def toggle_theme():
    current_user.theme = 'dark' if current_user.theme == 'light' else 'light'
    db.session.commit()
    flash('Тема змінена!', 'info')
    return redirect(request.referrer or url_for('dashboard.index'))

