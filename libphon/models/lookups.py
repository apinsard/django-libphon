# -*- coding: utf-8 -*-
import re

from django.db.models.lookups import Regex

__all__ = [
    'PhoneMatchLookup',
]


class PhoneMatchLookup(Regex):

    lookup_name = 'matches'

    def get_db_prep_lookup(self, value, connection):
        print(value)
        value = re.sub(r'[^0-9]', '', value)
        print(value)
        m = re.match(r'(33|0+)([1-9][0-9]*)?', value)
        value = r'^(\+?(33|972)|0+)[^0-9]*{}[^0-9]*'.format(
            r'[^0-9]*'.join(m.group(2)))
        print(value)
        return super().get_db_prep_lookup(value, connection)
