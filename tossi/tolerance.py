# -*- coding: utf-8 -*-
"""
   tossi.tolerance
   ~~~~~~~~~~~~~~~

   Utilities for tolerant particle forms.

   :copyright: (c) 2016 by What! Studio
   :license: BSD, see LICENSE for more details.

"""
from six import integer_types


__all__ = ['generate_tolerances', 'get_tolerance',
           'get_tolerance_from_iterator', 'parse_tolerance_style']


# Tolerance styles:
FORM1_AND_OPTIONAL_FORM2 = 0  # 은(는)
OPTIONAL_FORM1_AND_FORM2 = 1  # (은)는
FORM2_AND_OPTIONAL_FORM1 = 2  # 는(은)
OPTIONAL_FORM2_AND_FORM1 = 3  # (는)은


def generate_tolerances(form1, form2):
    """Generates all reasonable tolerant particle forms::

    >>> set(generate_tolerances(u'이', u'가'))
    set([u'이(가)', u'(이)가', u'가(이)', u'(가)이'])
    >>> set(generate_tolerances(u'이면', u'면'))
    set([u'(이)면'])

    """
    if form1 == form2:
        # Tolerance not required.
        return
    if not (form1 and form2):
        # Null allomorph exists.
        yield u'(%s)' % (form1 or form2)
        return
    len1, len2 = len(form1), len(form2)
    if len1 != len2:
        longer, shorter = (form1, form2) if len1 > len2 else (form2, form1)
        if longer.endswith(shorter):
            # Longer form ends with shorter form.
            yield u'(%s)%s' % (longer[:-len(shorter)], shorter)
            return
    # Find common suffix between two forms.
    for x, (let1, let2) in enumerate(zip(reversed(form1), reversed(form2))):
        if let1 != let2:
            break
    if x:
        # They share the common suffix.
        x1, x2 = len(form1) - x, len(form2) - x
        common_suffix = form1[x1:]
        form1, form2 = form1[:x1], form2[:x2]
    else:
        # No similarity with each other.
        common_suffix = ''
    for form1, form2 in [(form1, form2), (form2, form1)]:
        yield u'%s(%s)%s' % (form1, form2, common_suffix)
        yield u'(%s)%s%s' % (form1, form2, common_suffix)


def parse_tolerance_style(style, registry=None):
    """Resolves a tolerance style of the given tolerant particle form::

    >>> parse_tolerance_style(u'은(는)')
    0
    >>> parse_tolerance_style(u'(은)는')
    1
    >>> parse_tolerance_style(OPTIONAL_FORM2_AND_FORM1)
    3

    """
    if isinstance(style, integer_types):
        return style
    if registry is None:
        from . import registry
    particle = registry.get(style)
    if len(particle.tolerances) != 4:
        raise ValueError('Set tolerance style by general allomorphic particle')
    return particle.tolerances.index(style)


def get_tolerance(tolerances, style):
    try:
        return tolerances[style]
    except IndexError:
        return tolerances[0]


def get_tolerance_from_iterator(tolerances, style):
    for x, form in enumerate(tolerances):
        if style == x:
            return form
    return form
