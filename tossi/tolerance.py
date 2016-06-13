# -*- coding: utf-8 -*-
"""
   tossi.tolerance
   ~~~~~~~~~~~~~~~

   Utilities for tolerant particle morphs.

   :copyright: (c) 2016 by What! Studio
   :license: BSD, see LICENSE for more details.

"""
from six import integer_types


__all__ = ['generate_tolerances', 'get_tolerance',
           'get_tolerance_from_iterator', 'parse_tolerance_style']


# Tolerance styles:
MORPH1_AND_OPTIONAL_MORPH2 = 0  # 은(는)
OPTIONAL_MORPH1_AND_MORPH2 = 1  # (은)는
MORPH2_AND_OPTIONAL_MORPH1 = 2  # 는(은)
OPTIONAL_MORPH2_AND_MORPH1 = 3  # (는)은


def generate_tolerances(morph1, morph2):
    """Generates all reasonable tolerant particle morphs::

    >>> set(generate_tolerances(u'이', u'가'))
    set([u'이(가)', u'(이)가', u'가(이)', u'(가)이'])
    >>> set(generate_tolerances(u'이면', u'면'))
    set([u'(이)면'])

    """
    if morph1 == morph2:
        # Tolerance not required.
        return
    if not (morph1 and morph2):
        # Null allomorph exists.
        yield u'(%s)' % (morph1 or morph2)
        return
    len1, len2 = len(morph1), len(morph2)
    if len1 != len2:
        longer, shorter = (morph1, morph2) if len1 > len2 else (morph2, morph1)
        if longer.endswith(shorter):
            # Longer morph ends with shorter morph.
            yield u'(%s)%s' % (longer[:-len(shorter)], shorter)
            return
    # Find common suffix between two morphs.
    for x, (let1, let2) in enumerate(zip(reversed(morph1), reversed(morph2))):
        if let1 != let2:
            break
    if x:
        # They share the common suffix.
        x1, x2 = len(morph1) - x, len(morph2) - x
        common_suffix = morph1[x1:]
        morph1, morph2 = morph1[:x1], morph2[:x2]
    else:
        # No similarity with each other.
        common_suffix = ''
    for morph1, morph2 in [(morph1, morph2), (morph2, morph1)]:
        yield u'%s(%s)%s' % (morph1, morph2, common_suffix)
        yield u'(%s)%s%s' % (morph1, morph2, common_suffix)


def parse_tolerance_style(style, registry=None):
    """Resolves a tolerance style of the given tolerant particle morph::

    >>> parse_tolerance_style(u'은(는)')
    0
    >>> parse_tolerance_style(u'(은)는')
    1
    >>> parse_tolerance_style(OPTIONAL_MORPH2_AND_MORPH1)
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
    for x, morph in enumerate(tolerances):
        if style == x:
            return morph
    return morph
