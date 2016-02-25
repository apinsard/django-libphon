# -*- coding: utf-8 -*-
# Copyright (c) 2016 Aladom SAS & Hosting Dvpt SAS
import re
from urllib.error import URLError, HTTPError
import urllib.request

from django.http import QueryDict
from django.utils.module_loading import import_string

from ..conf import SMS_API_KEY, SMS_BACKEND
from ..exceptions import (
    PhoneError, InvalidPhoneNumber, NotAMobilePhone, ServiceUnavailable,
)

__all__ = [
    'Backend', 'UndefinedBackend', 'Digitaleo',
    'get_backend',
]


char_count_double = '^\\|~[]{}€\x0c'
sms_max_length = 160
long_sms_max_length = 1024
long_sms_single_max_length = 153


class Backend(object):

    def __init__(self, message, phone, send_date=None):
        self.message = message
        self.phone = phone
        if send_date:
            self.send_date = send_date.replace(microsecond=0)
        else:
            self.send_date = None

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

    def send(self):
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
        try:
            response = urllib.request.urlopen(url)
        except (URLError, HttpError) as e:
            raise ServiceUnavailable(e)
        self.parse_response(response.read().decode('utf-8'))
        if self.get_status == 'ko':
            raise PhoneError(self.response)

    def parse_response(self, response):
        self.response = dict(self.response_expr.findall(response))

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


def get_backend():
    return import_string(SMS_BACKEND)
