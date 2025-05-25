from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.models import db, User, Role

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.before_request
@login_required
def check_admin():
    if not current_user.is_admin():
        flash("Доступ заборонено.", "danger")
        return redirect(url_for('dashboard.index'))

@admin_bp.route('/delete_user/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        flash("Не можна видалити свій обліковий запис.", "warning")
        return redirect(url_for('admin.user_list'))
    db.session.delete(user)
    db.session.commit()
    flash("Користувача видалено.", "success")
    return redirect(url_for('admin.admin_dashboard'))

@admin_bp.route('/toggle_role/<int:user_id>', methods=['POST'])
def toggle_role(user_id):
    user = User.query.get_or_404(user_id)

    if user.role.name == 'admin':
        user.role = Role.query.filter_by(name='user').first()
    else:
        user.role = Role.query.filter_by(name='admin').first()

    db.session.commit()
    flash("Роль змінено.", "info")
    return redirect(url_for('admin.admin_dashboard'))

@admin_bp.route('/admin')
@login_required
def admin_dashboard():
    if not current_user.is_admin():
        flash('У вас немає доступу до адмін-панелі.', 'danger')
        return redirect(url_for('dashboard.index'))

    users = User.query.all()
    return render_template('admin/dashboard.html', users=users)






