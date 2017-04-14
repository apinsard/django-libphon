# -*- coding: utf-8 -*-
# Copyright (c) 2016 Aladom SAS & Hosting Dvpt SAS
from .types import get_phone_type, clean_number

from ..sms.backends import get_backend as get_sms_backend

__all__ = [
    'Phone',
]


class Phone(object):

    @property
    def value(self):
        return self.get_cleaned_value()

    @value.setter
    def value(self, value):
        self._type = get_phone_type(value)
        self._value = value

    def __init__(self, value):
        self.value = value
        
    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            other = self.__class__(other)
        return self.value == other.value

    def __str__(self):
        return self._value or ''

    def __len__(self):
        return len(self._value)

    def is_valid(self):
        return self._type is not None

    def is_mobile(self):
        return self.is_valid() and self._type.is_mobile(self._value)

    def get_country(self):
        if self.is_valid():
            return self._type.country_code
        else:
            return None

    def get_cleaned_value(self):
        if self.is_valid():
            return self._type.clean(self._value)
        else:
            return clean_number(self._value)

    def format(self, separator=None, international=True):
        if self.is_valid():
            return self._type.format(self._value, separator, international)
        else:
            return self.value

    def local_format(self, separator=None):
        return self.format(separator, international=False)

    def send_sms(self, message, **kwargs):
        backend = kwargs.pop('backend', get_sms_backend())
        sms = backend(message, self, **kwargs)
        sms.send()

    def send_sms_async(self, message, **kwargs):
        """Send SMS asynchroneously. Requires django channels."""
        try:
            from channels import Channel
        except ImportError:
            raise ImportError(
                "This service requires Django Channels. You can install it "
                "with: pip install channels"
            )
        Channel('libphon.send_sms').send(dict(
            phone=self.value, message=message, **kwargs
        ))
