from flask import Blueprint, render_template
from flask_login import login_required, current_user
from app.models import db, Transaction, Category
from sqlalchemy import func
from collections import defaultdict


dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/')
@login_required
def index():
    user_id = current_user.id

    # Роздільне підсумовування доходів та витрат
    income = db.session.query(func.sum(Transaction.amount)) \
        .filter_by(user_id=user_id, type='income').scalar() or 0

    expense = db.session.query(func.sum(Transaction.amount)) \
        .filter_by(user_id=user_id, type='expense').scalar() or 0

    balance = income - expense

    # Останні транзакції
    last_transactions = Transaction.query \
        .filter_by(user_id=user_id) \
        .order_by(Transaction.date.desc()) \
        .limit(5).all()

    # Сума витрат по категоріях
    expenses_by_category = db.session.query(
        Category.name, func.sum(Transaction.amount)
    ).join(Transaction).filter(
        Transaction.user_id == user_id,
        Transaction.type == 'expense'
    ).group_by(Category.name).all()

    # Підготовка динаміки балансу (лінійний графік)
    raw_data = db.session.query(
        Transaction.date,
        Transaction.type,
        func.sum(Transaction.amount)
    ).filter(Transaction.user_id == user_id) \
    .group_by(Transaction.date, Transaction.type) \
    .order_by(Transaction.date).all()

    daily_totals = defaultdict(lambda: {'income': 0, 'expense': 0})
    for t_date, t_type, amount in raw_data:
        daily_totals[t_date][t_type] += float(amount)

    trend_labels = []
    trend_values = []
    running_balance = 0

    for t_date in sorted(daily_totals):
        day_data = daily_totals[t_date]
        running_balance += day_data['income']
        running_balance -= day_data['expense']
        trend_labels.append(t_date.strftime('%d.%m'))
        trend_values.append(round(running_balance, 2))

    return render_template(
        'dashboard.html',
        user=current_user,
        balance=balance,
        last_transactions=last_transactions,
        chart_labels=[name for name, _ in expenses_by_category],
        chart_values=[float(total) for _, total in expenses_by_category],
        trend_labels=trend_labels,
        trend_values=trend_values
    )

@dashboard_bp.route('/balance-trend')
@login_required
def balance_trend():
    transactions = Transaction.query.filter_by(user_id=current_user.id).order_by(Transaction.date).all()

    daily_data = {}
    balance = 0
    for t in transactions:
        date = t.date.strftime('%Y-%m-%d')
        if date not in daily_data:
            daily_data[date] = 0
        balance += t.amount if t.type == 'income' else -t.amount
        daily_data[date] = balance

    labels = list(daily_data.keys())
    values = list(daily_data.values())

    return render_template('dashboard/balance_trend.html', labels=labels, values=values)

