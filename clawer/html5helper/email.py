#!/bin/env python
# coding=utf-8
''' email utility.
use 'python -m smtpd -n -c DebuggingServer localhost:1025' to start smtpd
'''

import threading
import types
import traceback
import logging
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.template.loader import render_to_string
from django.template.context import Context
from django.utils.html import strip_tags




def email_user(subject, template, template_dict, to_user):
    is_ok = True
    try:
        send_html_mail(subject, template, template_dict, to_user.email)
    except:
        is_ok = False
        logging.error("email %s failed:\n %s", to_user.email, traceback.format_exc(20))
    if is_ok is False and to_user.get_profile().second_email:
        try:
            send_html_mail(subject, template, template_dict, to_user.get_profile().second_email)
            is_ok = True
        except:
            logging.error("email %s failed:\n %s", to_user.get_profile().second_email, traceback.format_exc(20))
    return is_ok
            

def send_html_mail(subject, template, template_dict, to, cc = [], use_thread = True):
    if use_thread:
        thread = threading.Thread(target = _send_html_mail_thread, name = "send_html_email_cli", 
                                  args = (subject, template, template_dict, to , cc))
        thread.setDaemon(True)
        #thread.start()
        thread.run()
    else:
        _send_html_mail_thread(subject, template, template_dict, to, cc)
    

def _send_html_mail_thread(subject, template, template_dict, to, cc):
    """ run in thread
    """
    
    context = Context(use_l10n = True, use_tz = True)
    template_dict.update({"settings": settings})
    content = render_to_string(template, template_dict, context)
    _do_send_html_mail(subject, content, to, cc)
    
            
def _do_send_html_mail(subject, content, to, cc):
    """ run in thread
    """
    try:
        if isinstance(to, types.ListType) is False:
            to = [to]
        if subject[0] != "[":
            subject = settings.EMAIL_SUBJECT_PREFIX + subject
            
        text_content = strip_tags(content)
        email = EmailMultiAlternatives(subject, text_content, settings.EMAIL_FROM, to, [], cc = cc)
        email.attach_alternative(content, "text/html")
        email.send()
    except:
        errlog = traceback.format_exc(20)
        logging.error("send html mail error:\n%s", errlog)