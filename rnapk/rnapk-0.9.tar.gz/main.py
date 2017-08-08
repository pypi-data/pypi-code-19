import os
import smtplib
import yaml
import sys
import click
import subprocess
from email import encoders
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


@click.group()
def cli():
    ''' A simple utility to send a production APK build for your React Native apps to your team via email. '''
    pass


@click.command()
@click.option('--config', default=os.getcwd() + '/rnapk.yml', help='Path for the rnapk.yml config file.')
@click.option('-sb', is_flag=True, help='Skip build, only send the email')
def deploy(config, skip_build):
    ''' Create and send the apk. '''
    opts = config_parser(config)
    try:
        if not skip_build:
            build_apk()
        send_emails(opts, os.getcwd() + '/app/build/outputs/apk/app-release.apk')
    except Exception as e:
        print('An error occurred: %s' % e)
        sys.exit()


def config_parser(path):
    ''' Creates a dict from the config file options '''
    try:
        print('Making config')
        with open(path, 'r') as f:
            config = yaml.load(f)
            return config
    except Exception as e:
        print('Error occurred %s' % e)


cli.add_command(deploy)


def build_apk():
    android_folder = os.getcwd() + '/android'
    if not os.path.exists(android_folder):
        print('Working with cwd: %s' % os.getcwd())
        raise Exception('Android folder not found. Please make sure you are in the root of your React Native project.')

    print('Done with path check')
    try:
        print('cding android')
        os.chdir(os.getcwd() + '/android')
        print('current working dir is: %s' % os.getcwd())
        subprocess.call(['sh', 'gradlew', 'assembleRelease'], cwd=os.getcwd())
        print('Done')
    except Exception as e:
        print('Error %s' % e)
        raise Exception('Please make sure you are in the root of a valid React Native project.')


def send_emails(options, apk_file):
    send_email_with_attachment(options['emails'], options['credentials'], apk_file)


def send_email_with_attachment(recipients, credentials, attachment):
    gmail_user = credentials['username']
    gmail_pwd = credentials['password']

    FROM = credentials['name']
    TO = recipients

    msg = MIMEMultipart()
    msg['To'] = ', '.join(recipients)
    msg['From'] = FROM
    msg['Subject'] = credentials['subject']

    text = MIMEText(credentials['text'], 'plain')

    msg.attach(text)

    with open(attachment, 'rb') as f:
        maintype = 'application'
        subtype='vnd.android.package-archive'
        apk = MIMEBase(maintype, subtype)
        apk.set_payload(f.read())
    encoders.encode_base64(apk)

    filename = credentials['filename'] + '.apk'

    apk.add_header('Content-Disposition', 'attachment', filename=filename)
    msg.attach(apk)

    try:
        server_ssl = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server_ssl.ehlo() # optional, called by login()
        server_ssl.login(gmail_user, gmail_pwd)
        server_ssl.sendmail(FROM, TO, msg.as_string())
        server_ssl.close()
        print('Done')
    except Exception as e:
        print('Error sending mail: %s' % e)
