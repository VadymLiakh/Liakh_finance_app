from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.models import Category, Transaction, db
from app.forms import CategoryForm
from sqlalchemy import func



categories_bp = Blueprint('categories', __name__, url_prefix='/categories')

@categories_bp.route('/add', methods=['POST'])
@login_required
def add():
    name = request.form.get('name')
    if name:
        existing = Category.query.filter_by(name=name, user_id=current_user.id).first()
        if existing:
            flash('Така категорія вже існує.', 'danger')
        else:
            new_cat = Category(name=name, user_id=current_user.id)
            db.session.add(new_cat)
            db.session.commit()
            flash('Категорія додана!', 'success')
    return redirect(url_for('categories.index'))

@categories_bp.route('/delete/<int:cat_id>')
@login_required
def delete(cat_id):
    category = Category.query.get_or_404(cat_id)
    if category.user_id != current_user.id:
        flash('Це не ваша категорія.', 'danger')
    else:
        db.session.delete(category)
        db.session.commit()
        flash('Категорію видалено.', 'success')
    return redirect(url_for('categories.index'))

@categories_bp.route('/', methods=['GET', 'POST'])
@login_required
def index():
    form = CategoryForm()
    categories = (
        db.session.query(
            Category,
            func.count(Transaction.id).label('transaction_count'),
            func.sum(Transaction.amount).label('total_amount')
        )
        .outerjoin(Transaction)
        .filter(Category.user_id == current_user.id)
        .group_by(Category.id)
        .all()
    )

    if form.validate_on_submit():
        new_category = Category(name=form.name.data, user_id=current_user.id)
        db.session.add(new_category)
        db.session.commit()
        flash('Категорію додано!', 'success')
        return redirect(url_for('categories.index'))

    return render_template('categories/index.html', form=form, categories=[
        {
            'id': c.Category.id,
            'name': c.Category.name,
            'transaction_count': c.transaction_count,
            'total_amount': c.total_amount
        } for c in categories
    ])


@categories_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    category = Category.query.get_or_404(id)
    if category.user_id != current_user.id:
        flash('Це не ваша категорія.', 'danger')
        return redirect(url_for('categories.index'))

    form = CategoryForm(obj=category)

    if form.validate_on_submit():
        category.name = form.name.data
        db.session.commit()
        flash('Категорію оновлено!', 'success')
        return redirect(url_for('categories.index'))

    return render_template('categories/edit.html', form=form, category=category)
