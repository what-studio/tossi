# -*- coding: utf-8 -*-
"""
   tossi.coda
   ~~~~~~~~~~

   Coda is final consonant in a Korean syllable.  That is important because
   required when determining a particle allomorph in Korean.

   This module implements :func:`guess_coda` and related functions to guess a
   coda from any words as correct as possible.

   :copyright: (c) 2016 by What! Studio
   :license: BSD, see LICENSE for more details.

"""
from bisect import bisect_right
from decimal import Decimal
import re
import unicodedata

from .hangul import split_phonemes


__all__ = ['filter_only_significant', 'guess_coda',
           'guess_coda_from_significant_word', 'pick_coda_from_decimal',
           'pick_coda_from_letter']


#: Matches to a decimal at the end of a word.
DECIMAL_PATTERN = re.compile(r'[0-9]+(\.[0-9]+)?$')


def guess_coda(word):
    """Guesses the coda of the given word as correct as possible.  If it fails
    to guess the coda, returns ``None``.
    """
    word = filter_only_significant(word)
    return guess_coda_from_significant_word(word)


def guess_coda_from_significant_word(word):
    if not word:
        return None
    decimal_m = DECIMAL_PATTERN.search(word)
    if decimal_m:
        return pick_coda_from_decimal(decimal_m.group(0))
    return pick_coda_from_letter(word[-1])


# Patterns which match to significant or insignificant letters at the end of
# words.
INSIGNIFICANT_PARENTHESIS_PATTERN = re.compile(r'\(.*?\)$')
SIGNIFICANT_UNICODE_CATEGORY_PATTERN = re.compile(r'^([LN].|S[cmo])$')


def filter_only_significant(word):
    """Gets a word which removes insignificant letters at the end of the given
    word::

    >>> pick_significant(u'넥슨(코리아)')
    넥슨
    >>> pick_significant(u'메이플스토리...')
    메이플스토리

    """
    if not word:
        return word
    # Unwrap a complete parenthesis.
    if word.startswith(u'(') and word.endswith(u')'):
        return filter_only_significant(word[1:-1])
    x = len(word)
    while x > 0:
        x -= 1
        l = word[x]
        # Skip a complete parenthesis.
        if l == u')':
            m = INSIGNIFICANT_PARENTHESIS_PATTERN.search(word[:x + 1])
            if m is not None:
                x = m.start()
            continue
        # Skip unreadable characters such as punctuations.
        unicode_category = unicodedata.category(l)
        if not SIGNIFICANT_UNICODE_CATEGORY_PATTERN.match(unicode_category):
            continue
        break
    return word[:x + 1]


def pick_coda_from_letter(letter):
    """Picks only a coda from a Hangul letter.  It returns ``None`` if the
    given letter is not Hangul.
    """
    try:
        __, __, coda = \
            split_phonemes(letter, onset=False, nucleus=False, coda=True)
    except ValueError:
        return None
    else:
        return coda


# Data for picking coda from a decimal.
DIGITS = u'영일이삼사오육칠팔구'
EXPS = {1: u'십', 2: u'백', 3: u'천', 4: u'만',
        8: u'억', 12: u'조', 16: u'경', 20: u'해',
        24: u'자', 28: u'양', 32: u'구', 36: u'간',
        40: u'정', 44: u'재', 48: u'극', 52: u'항하사',
        56: u'아승기', 60: u'나유타', 64: u'불가사의', 68: u'무량대수',
        72: u'겁', 76: u'업'}
DIGIT_CODAS = [pick_coda_from_letter(x[-1]) for x in DIGITS]
EXP_CODAS = {exp: pick_coda_from_letter(x[-1]) for exp, x in EXPS.items()}
EXP_INDICES = list(sorted(EXPS.keys()))


# Mark the first unreadable exponent.
_unreadable_exp = max(EXP_INDICES) + 4
EXP_CODAS[_unreadable_exp] = None
EXP_INDICES.append(_unreadable_exp)
del _unreadable_exp


def pick_coda_from_decimal(decimal):
    """Picks only a coda from a decimal."""
    decimal = Decimal(decimal)
    __, digits, exp = decimal.as_tuple()
    if exp < 0:
        return DIGIT_CODAS[digits[-1]]
    __, digits, exp = decimal.normalize().as_tuple()
    index = bisect_right(EXP_INDICES, exp) - 1
    if index < 0:
        return DIGIT_CODAS[digits[-1]]
    else:
        return EXP_CODAS[EXP_INDICES[index]]
