
from flask_mail import Mail, Message
from flask import current_app

mail = Mail() 
email_recipient = "jasmita@ambiplatforms.com"  # Set your recipient's email

def send_email(recipient, subject, body):
    with current_app.app_context():
        msg = Message(subject, sender=current_app.config['MAIL_USERNAME'], recipients=[recipient])
        msg.body = body
        mail.send(msg)
        print("Email sent successfully.")