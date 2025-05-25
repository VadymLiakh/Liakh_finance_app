from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from app.models import db, Transaction, Category
from app.forms import TransactionForm
from flask import request, render_template

transactions_bp = Blueprint('transactions', __name__, url_prefix='/transactions')

@transactions_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_transaction():
    form = TransactionForm()

    categories = Category.query.filter_by(user_id=current_user.id).all()
    form.category.choices = [(c.id, c.name) for c in categories]

    if form.validate_on_submit():
        transaction = Transaction(
            amount=form.amount.data,
            type=form.type.data,
            category_id=form.category.data,
            date=form.date.data,
            description=form.description.data,
            user_id=current_user.id
        )

        if form.type.data == 'income':
            transaction.category_id = None

        db.session.add(transaction)
        db.session.commit()
        flash('Транзакція додана!', 'success')
        return redirect(url_for('transactions.list_transactions'))

    return render_template('transactions/add.html', form=form)

@transactions_bp.route('/list')
@login_required
def list_transactions():
    user_id = current_user.id
    transactions = Transaction.query.filter_by(user_id=user_id)

    # Фільтри
    t_type = request.args.get('type')
    category = request.args.get('category')
    date_from = request.args.get('date_from')
    date_to = request.args.get('date_to')
    min_amount = request.args.get('min_amount')
    max_amount = request.args.get('max_amount')

    if t_type:
        transactions = transactions.filter(Transaction.type == t_type)
    if category:
        transactions = transactions.filter(Transaction.category_id == int(category))
    if date_from:
        transactions = transactions.filter(Transaction.date >= date_from)
    if date_to:
        transactions = transactions.filter(Transaction.date <= date_to)
    if min_amount:
        transactions = transactions.filter(Transaction.amount >= float(min_amount))
    if max_amount:
        transactions = transactions.filter(Transaction.amount <= float(max_amount))

    transactions = transactions.order_by(Transaction.date.desc()).all()
    categories = Category.query.filter_by(user_id=user_id).all()

    return render_template('transactions/list.html', transactions=transactions, categories=categories)

@transactions_bp.route('/edit/<int:transaction_id>', methods=['GET', 'POST'])
@login_required
def edit_transaction(transaction_id):
    transaction = Transaction.query.get_or_404(transaction_id)

    if transaction.user_id != current_user.id:
        flash("Ви не можете редагувати цю транзакцію", "danger")
        return redirect(url_for('transactions.list_transactions'))

    form = TransactionForm(obj=transaction)

    categories = Category.query.filter_by(user_id=current_user.id).all()
    form.category.choices = [(c.id, c.name) for c in categories]

    if form.validate_on_submit():
        transaction.amount = form.amount.data
        transaction.type = form.type.data
        transaction.date = form.date.data
        transaction.description = form.description.data

        # 👇 Якщо дохід — не встановлюємо категорію
        if form.type.data == 'income':
            transaction.category_id = None
        else:
            transaction.category_id = form.category.data

        db.session.commit()
        flash("Транзакцію оновлено", "success")
        return redirect(url_for('transactions.list_transactions'))

    return render_template('transactions/edit.html', form=form, transaction=transaction)

@transactions_bp.route('/delete/<int:transaction_id>', methods=['POST'])
@login_required
def delete_transaction(transaction_id):
    transaction = Transaction.query.get_or_404(transaction_id)
    if transaction.user_id != current_user.id:
        flash("Ви не маєте доступу до цієї транзакції.", 'danger')
    else:
        db.session.delete(transaction)
        db.session.commit()
        flash("Транзакцію видалено.", "success")
    return redirect(url_for('transactions.list_transactions'))
