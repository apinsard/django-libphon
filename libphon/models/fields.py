# -*- coding: utf-8 -*-
# Copyright (c) 2016 Aladom SAS & Hosting Dvpt SAS
from django.db.models import CharField
from django.utils.translation import ugettext_lazy as _

from . import Phone


class PhoneField(CharField):
    description = _("Phone number")

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('max_length', 20)
        super().__init__(*args, **kwargs)

    def from_db_value(self, value, expression, connection, context):
        if value is None:
            return value
        return Phone(value)

    def to_python(self, value):
        if isinstance(value, Phone) or value is None:
            return value
        return Phone(value)

    def get_prep_value(self, value):
        return str(value)
