from django.conf.global_settings import DEFAULT_FROM_EMAIL
from django.contrib.auth.models import User
from django.core.mail import send_mail

__author__ = 'Thorin Tabor'


def email_user(user, subject, message, sent_by=DEFAULT_FROM_EMAIL):
    if isinstance(user, User):
        to_email = user.email
    else:
        to_email = user
    send_mail(subject, message, sent_by, [to_email])