# -*- coding: utf-8 -*-
# Copyright (c) 2016 Aladom SAS & Hosting Dvpt SAS
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

__all__ = [
    'SMS_BACKEND', 'SMS_API_KEY',
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
SMS_API_KEY = get_setting('SMS_API_KEY', None)
