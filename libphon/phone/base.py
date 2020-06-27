# -*- coding: utf-8 -*-
# Copyright (c) 2016 Aladom SAS & Hosting Dvpt SAS
import re
import phonenumbers

from ..conf import PREFERRED_LOCAL_COUNTRIES
from ..sms.backends import get_backend as get_sms_backend

__all__ = [
    'Phone',
]


class Phone:

    @property
    def value(self):
        return self.get_cleaned_value()

    @value.setter
    def value(self, value):
        self._raw_value = value
        self._value = None
        if not value:
            return
        country_codes = [None]
        if PREFERRED_LOCAL_COUNTRIES:
            country_codes += PREFERRED_LOCAL_COUNTRIES
        value = re.sub(r'^00', '+', value)
        for code in country_codes:
            try:
                self._value = phonenumbers.parse(value, code)
            except phonenumbers.phonenumberutil.NumberParseException:
                continue
            if not phonenumbers.is_valid_number(self._value):
                self._value = None
            else:
                break
        if not self._value and value[0] != '+':
            value = '+' + value
            for code in country_codes:
                try:
                    self._value = phonenumbers.parse(value, code)
                except phonenumbers.phonenumberutil.NumberParseException:
                    continue
                if not phonenumbers.is_valid_number(self._value):
                    self._value = None
                else:
                    break
        if self._value and not phonenumbers.is_valid_number(self._value):
            self._value = None

    def __init__(self, value):
        self.value = value

    def __eq__(self, other):
        if isinstance(other, str):
            other = self.__class__(other)
        if not isinstance(other, self.__class__):
            return False
        return self.value == other.value

    def __str__(self):
        return self._raw_value or ''

    def __len__(self):
        return len(self._raw_value)

    def is_valid(self):
        return self._value is not None

    def is_mobile(self):
        if not self.is_valid():
            return False
        if self._value.country_code == 33:
            return str(self._value.national_number)[0] in ['6', '7']
        return None

    def get_country(self):
        if self.is_valid():
            return phonenumbers.region_code_for_country_code(
                self._value.country_code)
        else:
            return None

    def get_cleaned_value(self):
        if self.is_valid():
            return phonenumbers.format_number(
                self._value, phonenumbers.PhoneNumberFormat.E164)
        else:
            plus = ('+' if '+' in self._raw_value else '')
            return plus + phonenumbers.normalize_digits_only(self._raw_value)

    def format(self, separator=None, international=True):
        if self.is_valid():
            value = phonenumbers.format_number(self._value, (
                phonenumbers.PhoneNumberFormat.INTERNATIONAL if international
                else phonenumbers.PhoneNumberFormat.NATIONAL
            ))
        else:
            value = self.value
        if separator:
            value = value.replace(' ', separator)
        return value

    def local_format(self, separator=None):
        return self.format(separator, international=False)

    def send_sms(self, message, **kwargs):
        backend = kwargs.pop('backend', get_sms_backend())
        sms = backend(message, self, **kwargs)
        sms.send()

    def send_sms_async(self, message, **kwargs):
        """Send SMS asynchroneously. Requires Celery."""
        try:
            from ..tasks import send_sms
        except ImportError:
            raise ImportError(
                "This service requires Celery. You can install it with: "
                "pip install celery"
            )
        send_sms.delay(self.value, message, **kwargs)
