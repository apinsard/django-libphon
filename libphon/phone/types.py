# -*- coding: utf-8 -*-
# Copyright (c) 2016 Aladom SAS & Hosting Dvpt SAS
import re

__all__ = [
    'PhoneType', 'FrenchPhone',
    'phone_types', 'get_phone_type',
]


def clean_number(value):
    return re.sub('[^0-9]', '', value)


class PhoneType(object):

    country_code = None
    phone_country_code = None
    expression = None
    mobile_expression = None
    default_separator = '-'

    @classmethod
    def is_valid(cls, value):
        value = clean_number(value)
        return bool(cls.expression.match(value))

    @classmethod
    def is_mobile(cls, value):
        value = clean_number(value)
        return bool(cls.mobile_expression.match(value))

    @classmethod
    def clean(cls, value):
        value = clean_number(value)
        number = cls.expression.match(value)
        if not number:
            return None
        return '+{code}{number}'.format(
            code=cls.phone_country_code,
            number=number.group('local'))

    @classmethod
    def format(cls, value, separator=None, international=True):
        return None


class FrPhone(PhoneType):

    country_code = 'FR'
    phone_country_code = '33'
    expression = re.compile('^(0|(00)?33)(?P<local>[1-9][0-9]{8})$')
    mobile_expression = re.compile('^(0|(00)?33)6')
    default_separator = ' '

    @classmethod
    def format(cls, value, separator=None, international=True):
        if separator is None:
            separator = cls.default_separator
        value = clean_number(value)
        number = cls.expression.match(value)
        if not number:
            return None
        number = number.group('local')
        head = number[0]
        tail = number[1:]
        number_parts = [head] + [tail[i:i+2] for i in range(len(tail)//2)]
        number = separator.join(number_parts)
        if international:
            return '+{code} {number}'.format(
                code=cls.phone_country_code, number=number)
        else:
            return '0{}'.format(number)


phone_types = [
    FrPhone,
]


def get_phone_type(value):
    for phone_type in phone_types:
        if phone_type.is_valid(value):
            return phone_type
    return None
