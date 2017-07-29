# coding: utf-8
from djotali.celery import app as celery_app


@celery_app.task(bind=True, max_retries=2, default_retry_delay=5)
def send_mail(self, from_email, contacts, username):
    print("Sending email")
    # mail('Hello', 'Contact %s is created.' % username, from_email, contacts)
