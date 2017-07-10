from email.header import Header
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formataddr
from smtplib import SMTP


class EmailClientError(Exception):
    pass

def to_ls(addr):
    if isinstance(addr, str):
        addr = [addr]
    elif isinstance(addr, list):
        addr = ','.join(addr)
    return addr

class EmailClient(object):

    def __init__(self, host=None, port=None,
                 username=None, password=None):
        self.host = host
        self.port = port
        self.username = username
        self.password = password

    def send_mail(self, _from=None, receivers=None, data=None, cc=None,
                  bcc=None, subject=None, text=None, html=None):

        msg = MIMEMultipart('alternative')

        if not receivers or not _from:
            raise EmailClientError(
                'Mail can not be sent without _to or _from')

        cc = to_ls(cc)
        bcc = to_ls(bcc)

        if subject: msg['Subject'] = Header(subject, 'utf-8')
        if cc: msg['CC'] = cc
        if bcc: msg['BCC'] = bcc
        if text: msg.attach(MIMEText(text, 'plain', 'utf-8'))
        if html: msg.attach(MIMEText(html, 'html', 'utf-8'))

        msg['From'] = formataddr((str(_from[0]), _from[1]))
        msg['To'] = to_ls(receivers)

        client = SMTP(host=self.host, port=self.port)
        if self.username and self.password:
            client.login(self.username, self.password)
        client.sendmail(
            msg=msg.as_string(),
            to_addrs=receivers,
            from_addr=_from
        )

        client.quit()

if __name__ == '__main__':
    es = EmailClient(
        host="localhost",
        port="1025"
    )

    es.send_mail(
        _from=('ardaorhan', 'test@test.com'),
        receivers=['test@test.com'],
        text='Hello world'
    )







