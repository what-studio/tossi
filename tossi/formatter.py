# -*- coding: utf-8 -*-
"""
   tossi.formatter
   ~~~~~~~~~~~~~~~

   String formatter for Tossi.

   :copyright: (c) 2016-2017 by What! Studio
   :license: BSD, see LICENSE for more details.

"""
import re
from string import Formatter as StringFormatter


class Formatter(StringFormatter):
    """String formatter supports tossi format spec.

    >>> f = Formatter(tossi.registry)
    >>> t = u'{0:으로} {0:을}'
    >>> assert f.format(t, u'나오') == u'나오로 나오를'
    >>> assert f.format(t, u'키홀') == u'키홀로 키홀을'
    >>> assert f.format(t, u'모리안') == u'모리안으로 모리안을'
    """
    hangul_pattern = re.compile(u'[가-힣]+')

    def __init__(self, registry):
        self.registry = registry

    def format_field(self, value, format_spec):
        if re.match(self.hangul_pattern, format_spec):
            return self.registry.postfix(value, format_spec)
        else:
            return super(Formatter, self).format_field(value, format_spec)
