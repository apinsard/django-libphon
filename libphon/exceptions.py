# -*- coding: utf-8 -*-
# Copyright (c) 2016 Aladom SAS & Hosting Dvpt SAS

__all__ = [
    'PhoneError', 'InvalidPhoneNumber', 'NotAMobilePhone',
    'ServiceUnavailable',
]


class PhoneError(Exception):
    pass


class InvalidPhoneNumber(PhoneError, ValueError):
    pass


class NotAMobilePhone(PhoneError, ValueError):
    pass


class ServiceUnavailable(PhoneError):
    pass
