# -*- coding: utf-8 -*-
# Copyright (c) 2016 Aladom SAS & Hosting Dvpt SAS
import logging
import re

from django.conf import settings
from django.http import QueryDict
from django.utils.module_loading import import_string

import requests

from ..conf import SMS_API_KEY, SMS_BACKEND, SMS_DEFAULT_FROM, DEV_PHONES
from ..exceptions import (
    PhoneError, InvalidPhoneNumber, NotAMobilePhone, ServiceUnavailable,
)

__all__ = [
    'Backend',
    'Digitaleo',
    'Mailjet',
    'UndefinedBackend',
    'get_backend',
]


char_count_double = '^\\|~[]{}€\x0c'
sms_max_length = 160
long_sms_max_length = 1024
long_sms_single_max_length = 153

logger = logging.getLogger('libphon.sms')


class Backend:

    def __init__(self, message, phone, send_date=None, from_header=None):
        self.message = message
        if send_date:
            self.send_date = send_date.replace(microsecond=0)
        else:
            self.send_date = None
        if settings.DEBUG and DEV_PHONES and phone not in DEV_PHONES:
            phone = DEV_PHONES[0]
        if isinstance(phone, str):
            from ..phone import Phone  # import here to avoid circular imports
            phone = Phone(phone)
        self.phone = phone
        self.from_header = from_header or SMS_DEFAULT_FROM

    def get_length(self):
        return len(self.message) + sum(self.message.count(c)
                                       for c in char_count_double)

    def get_nb_sms(self):
        length = self.get_length
        if length <= sms_max_length:
            return 1
        else:
            return length // long_sms_single_max_length


class UndefinedBackend(Backend):

    def __init__(self, *args, **kwargs):
        raise NotImplementedError("You must configure an SMS backend "
                                  "in order to send SMS messages.")


class Digitaleo(Backend):

    send_url = 'https://www.ecosms.fr/ecosms.php'
    response_expr = re.compile('^([a-z_]+)=(.*)$', re.M)

    def __init__(self, message, phone, send_date=None, from_header=None):
        if from_header:
            logger.warning("from_header not supported by Digitaleo backend.")
        return super().__init__(message, phone, send_date, None)

    def send(self):
        """Send the SMS through Digitaleo API.
        May raise `InvalidPhoneNumber` if the phone number is not valid.
        May raise `NotAMobilePhone` if the phone number is not detected as
        mobile phone.
        May raise `ServiceUnavailable` if an error occurs when attempting to
        reach Digitaleo API.
        May raise `PhoneError` if something else failed with Digitaleo.
        """
        if not self.phone.is_valid():
            raise InvalidPhoneNumber(self.phone)
        if not self.phone.is_mobile():
            raise NotAMobilePhone(self.phone)
        querydict = QueryDict(mutable=True)
        querydict['sms'] = self.message
        querydict['mobile'] = self.phone.value
        querydict['code'] = SMS_API_KEY
        querydict['charset'] = 'UTF-8'
        if self.send_date:
            querydict['date'] = self.send_date.isoformat()
        url = '{}?{}'.format(self.send_url, querydict.urlencode())
        response = requests.get(url)
        if response.status_code >= 500:
            raise ServiceUnavailable(response.text)
        self.parse_response(response)
        if self.get_status() == 'ko':
            raise PhoneError(self.response)

    def parse_response(self, response):
        self.response = dict(self.response_expr.findall(response.text))

    def get_status(self):
        if 'statut' in self.response:
            return self.response['statut'].split(' ', 1)[0]
        else:
            return 'ko'

    def get_status_message(self):
        if 'statut' in self.response:
            return self.response['statut'].split(' ', 1)[1]
        else:
            return ''

    def get_sms_id(self):
        return self.response.get('sms_id', None)


class Mailjet(Backend):

    send_url = 'https://api.mailjet.com/v4/sms-send'

    def __init__(self, message, phone, send_date=None, from_header=None):
        if send_date:
            logger.warning("send_date not supported by Mailjet backend.")
        return super().__init__(message, phone, None, from_header)

    def send(self):
        """Send the SMS through Mailjet API.
        May raise `InvalidPhoneNumber` if the phone number is not valid.
        May raise `NotAMobilePhone` if the phone number is not detected as
        mobile phone.
        May raise `ServiceUnavailable` if an error occurs when attempting to
        reach Mailjet API.
        May raise `PhoneError` if something else failed with Mailjet.
        """
        if not self.phone.is_valid():
            raise InvalidPhoneNumber(self.phone)
        if not self.phone.is_mobile():
            raise NotAMobilePhone(self.phone)
        request_payload = {
            'From': self.from_header,
            'To': self.phone.format(separator='', international=True),
            'Text': self.message,
        }
        request_headers = {'Authorization': 'Bearer {}'.format(SMS_API_KEY)}
        response = requests.post(
            self.send_url, json=request_payload, headers=request_headers)
        if response.status_code >= 500:
            raise ServiceUnavailable(response.text)
        self.parse_response(response)
        if self.get_status() != 2:
            raise PhoneError(self.response)

    def parse_response(self, response):
        self.response = response.json()

    def get_status(self):
        try:
            return self.response['Status']['Code']
        except KeyError:
            return -1

    def get_status_message(self):
        try:
            return self.response['Status']['Description']
        except KeyError:
            return ''

    def get_sms_id(self):
        return self.response.get('MessageId', None)


def get_backend():
    return import_string(SMS_BACKEND)
