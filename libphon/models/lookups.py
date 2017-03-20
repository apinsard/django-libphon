# -*- coding: utf-8 -*-
import re

from django.db.models.lookups import Regex

__all__ = [
    'PhoneMatchLookup',
]


class PhoneMatchLookup(Regex):

    def get_db_prep_lookup(self, value, connection):
        value = re.sub(r'[^0-9]', '', value)
        m = re.match(r'(33|0+)([1-9][0-9]{4,})', value)
        if m and and m.group(2):
            value = r'^(\+?(33|590)|0+)[^0-9]*{}[^0-9]*'.format(
                r'[^0-9]*'.join(m.group(2)))
        else:
            value = r'^__NOMATCH__$'
        return super().get_db_prep_lookup(value, connection)
