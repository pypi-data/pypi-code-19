# -*- coding: utf-8 -*-
__author__ = 'Евгений Сергеевич'
from django.conf import settings
from django.core.mail import EmailMessage

import telepot
from cpsk.settings import ALLOWED_HOSTS
# CPSK_order_BOT
TOKEN = '307648697:AAEct6YLREZU74nOoV4B4FqDNARyo0JV9HU'
bot = telepot.Bot(TOKEN)

class UtmHandler:
    def __init__(self, request, telegram_id, email_list):
        self.request = request
        self.telegram_id = telegram_id
        self.email_list = email_list
        if self.request.method != 'GET': #error!
            raise ValueError("We accept just GET REQUESTS!")



    def _validator(self):
        # Провеми, что бы не было повторынх переходов -->
        #  ловим только переходы с поисковиков и пр.

        #special events
        if self.request.GET.get('event') == 'test':
            return True

        print 'ALLOWED_HOSTS', ALLOWED_HOSTS
        print "self.request.META.get('HTTP_REFERER')", self.request.META.get('HTTP_REFERER')

        if not self.telegram_id:
            return False

        if not self.request.GET.get('utm_term'):
            return False

        if self.request.META.get('HTTP_REFERER'):
            for item in ALLOWED_HOSTS:
                # прямой вход не забудем
                if item in self.request.META.get('HTTP_REFERER'):
                    break
                pass
            return False

        return True


    def _msg_handler(self):
        dict_to_work = dict(self.request.GET.iterlists())
        msg = u''
        msg += u'Переход по utm-метке %s \n\n' % self.request.META.get('PATH_INFO')
        for k, v in dict_to_work.items():
            if k == 'csrfmiddlewaretoken':
                continue
            msg += u'<b>%s</b>: %s; \n' % (k, ','.join(v))
        # msg += u'<b>HTTP_REFERER</b>: %s' % self.request.META.get('HTTP_REFERER')
        return msg

    def _send_email(self, msg):
        subject = u'Переход по utm-метке %s' % self.request.META.get('PATH_INFO')
        message = EmailMessage(subject,
                               msg, # или может быть просто message
                                to=self.email_list)
        # message.content_subtype = "html"
        message.send()

    def send(self):
        if self._validator():
            msg = self._msg_handler()
            if self.email_list:
                self._send_email(msg)
            if self.telegram_id:
                bot.sendMessage(self.telegram_id, msg,
                                disable_web_page_preview=True,
                                parse_mode='html')


def utmcollector(telegram_id=None, email_list=None, *utmcollector_args, **utmcollector_kwargs):
    telegram_id = telegram_id if telegram_id else None
    email_list = email_list if email_list else None

    def collect(view_func):
        def wrapper(*original_args, **original_kwargs):
            request = original_args[0]

            UtmHandler(request, telegram_id, email_list).send()

            return view_func(*original_args, **original_kwargs)
        return wrapper
    return collect