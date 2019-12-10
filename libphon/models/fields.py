# -*- coding: utf-8 -*-
# Copyright (c) 2016 Aladom SAS & Hosting Dvpt SAS
from django.db.models import CharField
from django.utils.translation import ugettext_lazy as _

from ..phone import Phone
from .lookups import PhoneMatchLookup

__all__ = [
    'PhoneField',
]


class PhoneField(CharField):
    description = _("Phone number")

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('max_length', 20)
        super().__init__(*args, **kwargs)

    def from_db_value(self, value, expression, connection):
        if not value:
            return None
        return Phone(value)

    def to_python(self, value):
        if isinstance(value, Phone):
            return value
        if not value:
            return None
        return Phone(value)

    def get_prep_value(self, value):
        if value is None:
            return ""
        return str(value)

    def contribute_to_class(self, cls, name, *args, **kwargs):
        super().contribute_to_class(cls, name, *args, **kwargs)

        def get_FOO_display(s, *bar, **baz):
            field = getattr(s, self.name)
            return field.format(*bar, **baz) if field else '-'
        get_FOO_display.__name__ = 'get_{}_display'.format(self.name)
        get_FOO_display.short_description = self.verbose_name
        get_FOO_display.admin_order_field = self.name

        setattr(cls, get_FOO_display.__name__, get_FOO_display)

    def get_lookup(self, lookup_name):
        if lookup_name == 'matches':
            return PhoneMatchLookup
        return super().get_lookup(lookup_name)
