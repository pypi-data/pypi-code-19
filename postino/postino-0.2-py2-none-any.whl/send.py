import smtplib


def send_message(
        message,
        recipients,
        fromaddr,
        host,
        port=25,
        mode=None,
        login=None,
        password=None):

    if mode == 'ssl':
        smtp = smtplib.SMTP_SSL(host, port)
    elif mode == 'tls':
        smtp = smtplib.SMTP(host, port)
        smtp.starttls()
    else:
        smtp = smtplib.SMTP(host, port)

    try:
        if login and password:
            smtp.login(login, password)
        smtp.sendmail(fromaddr, recipients, message.as_string())
    finally:
        smtp.quit()
