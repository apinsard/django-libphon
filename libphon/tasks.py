# -*- coding: utf-8 -*-
from celery import shared_task

from .sms.backends import get_backend


@shared_task
def send_sms(phone, message, send_date=None):
    SMS = get_backend()
    sms = SMS(message, phone, send_date=send_date)
    sms.send()
    return sms
