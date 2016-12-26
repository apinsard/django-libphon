# -*- coding: utf-8 -*-
# Copyright (c) 2016 Aladom SAS & Hosting Dvpt SAS
import re

__all__ = [
    'PhoneType', 'FrPhone', 'GpPhone', 'GfPhone', 'MqPhone', 'RePhone',
    'YtPhone',
    'clean_number', 'get_phone_type',
]


def clean_number(value):
    return re.sub('[^0-9]', '', value)


class PhoneType(object):

    country_code = None
    country_calling_code = None
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
            code=cls.country_calling_code,
            number=number.group('local'))

    @classmethod
    def format(cls, value, separator=None, international=True):
        return None


class FrPhone(PhoneType):

    country_code = 'FR'
    country_calling_code = '33'
    expression = re.compile('^(0|(00)?33)(?P<local>[1-9][0-9]{8})$')
    mobile_expression = re.compile('^(0|(00)?33)[67]')
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
        number_parts = [head] + [tail[i:i+2] for i in range(len(tail)) if i%2 == 0]
        number = separator.join(number_parts)
        if international:
            return '+{code} {number}'.format(
                code=cls.country_calling_code, number=number)
        else:
            return '0{}'.format(number)


class GpPhone(FrPhone):

    country_code = 'GP'
    country_calling_code = '590'
    expression = re.compile('^(0|(00)?590)(?P<local>[56]90[0-9]{6})$')
    mobile_expression = re.compile('^(0|(00)?590)6')

    @classmethod
    def format(cls, value, separator=None, international=True):
        if separator is None:
            separator = cls.default_separator
        value = clean_number(value)
        number = cls.expression.match(value)
        if not number:
            return None
        number = number.group('local')
        head = number[0:3]
        tail = number[3:]
        number_parts = [head] + [tail[i:i+2] for i in range(len(tail)) if i%2 == 0]
        number = separator.join(number_parts)
        if international:
            return '+{code} {number}'.format(
                code=cls.country_calling_code, number=number)
        else:
            return '0 {}'.format(number)


class GfPhone(GpPhone):

    country_code = 'GF'
    country_calling_code = '594'
    expression = re.compile('^(0|(00)?594)(?P<local>[56]94[0-9]{6})$')
    mobile_expression = re.compile('^(0|(00)?594)6')


class MqPhone(GpPhone):

    country_code = 'MQ'
    country_calling_code = '596'
    expression = re.compile('^(0|(00)?594)(?P<local>[56]96[0-9]{6})$')
    mobile_expression = re.compile('^(0|(00)?596)6')


class RePhone(GpPhone):

    country_code = 'RE'
    country_calling_code = '262'
    expression = re.compile('^(0|(00)?262)(?P<local>(26|69)[23][0-9]{6})$')
    mobile_expression = re.compile('^(0|(00)?262)6')


class YtPhone(RePhone):

    country_code = 'YT'
    expression = re.compile('^(0|(00)?262)(?P<local>(26|63)9[0-9]{6})$')


phone_types = [
    YtPhone,
    RePhone,
    MqPhone,
    GfPhone,
    GpPhone,
    FrPhone,
]


def get_phone_type(value):
    for phone_type in phone_types:
        if phone_type.is_valid(value):
            return phone_type
    return None
