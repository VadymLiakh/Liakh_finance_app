from flask_mail import Message
from flask import url_for, current_app
from app import mail

def send_reset_email(user):
    token = user.get_reset_token()
    
    sender = current_app.config.get('MAIL_DEFAULT_SENDER')
    if not sender:
        raise RuntimeError("MAIL_DEFAULT_SENDER не заданий у конфігурації")

    msg = Message(
        subject='Відновлення пароля',
        sender=sender,
        recipients=[user.email]
    )

    msg.body = f'''Привіт, {user.username}!

Щоб скинути пароль, перейдіть за цим посиланням:
{url_for('auth.reset_token', token=token, _external=True)}

Якщо ви не запитували скидання пароля, просто проігноруйте цей лист.
'''

    mail.send(msg)
