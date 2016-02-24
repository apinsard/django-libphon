# -*- coding: utf-8 -*-
# Copyright (c) 2016 Aladom SAS & Hosting Dvpt SAS
from .types import get_phone_type

__all__ = [
    'Phone',
]


class Phone(object):

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self._type = get_phone_type(value)
        self._value = value

    def __init__(self, value):
        self.value = value

    def is_valid(self):
        return self._type is not None

    def is_mobile(self):
        return self.is_valid() and self._type.is_mobile(self.value)

    def get_country(self):
        if self.is_valid():
            return self._type.country_code
        else:
            return None
