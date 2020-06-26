# -*- coding: utf-8 -*-
# Copyright (c) 2016 Aladom SAS & Hosting Dvpt SAS
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

__all__ = [
    'SMS_BACKEND', 'SMS_API_KEY', 'SMS_DEFAULT_FROM', 'DEV_PHONES',
    'PREFERRED_LOCAL_COUNTRIES',
]


def get_setting(key, *args):
    """Retrieve a mailing specific setting from django settings.
    Accept a default value as second argument.
    Raise ImproperlyConfigured if the requested setting is not set and no
    default value is provided.
    """
    try:
        value = settings.LIBPHON[key]
    except (AttributeError, KeyError):
        if len(args) > 0:
            value = args[0]
        else:
            message = "Please define LIBPHON['{}'] in your settings.py"
            raise ImproperlyConfigured(message.format(key))
    return value


SMS_BACKEND = get_setting('SMS_BACKEND',
                          'libphon.sms.backends.UndefinedBackend')
"""SMS backend to use to send SMS."""

SMS_API_KEY = get_setting('SMS_API_KEY', None)
"""The API key to access the SMS API."""

SMS_DEFAULT_FROM = get_setting('SMS_DEFAULT_FROM', "Django Libphon")
"""The default From header displayed to SMS recipients."""

DEV_PHONES = get_setting('DEV_PHONES', None)
"""Prevents from sending SMS to other phone numbers than those specified here
while in DEBUG mode.
"""

PREFERRED_LOCAL_COUNTRIES = get_setting('PREFERRED_LOCAL_COUNTRIES', None)
"""List of countries in preferred order to check for local phone number
if country code is not provided.
"""
