# -*- coding: utf-8 -*-
"""
   tossi.hangul
   ~~~~~~~~~~~~

   Manipulates Hangul letters.

   :copyright: (c) 2016 by What! Studio
   :license: BSD, see LICENSE for more details.

"""
from six import unichr


__all__ = ['combine_words', 'is_consonant', 'is_hangul', 'join_phonemes',
           'split_phonemes']


# Korean phonemes as known as 자소 including
# onset(초성), nucleus(중성), and coda(종성).
ONSETS = list(u'ㄱㄲㄴㄷㄸㄹㅁㅂㅃㅅㅆㅇㅈㅉㅊㅋㅌㅍㅎ')
NUCLEUSES = list(u'ㅏㅐㅑㅒㅓㅔㅕㅖㅗㅘㅙㅚㅛㅜㅝㅞㅟㅠㅡㅢㅣ')
CODAS = [u'']
CODAS.extend(u'ㄱㄲㄳㄴㄵㄶㄷㄹㄺㄻㄼㄽㄾㄿㅀㅁㅂㅄㅅㅆㅇㅈㅊㅋㅌㅍㅎ')

# Lengths of the phonemes.
NUM_ONSETS = len(ONSETS)
NUM_NUCLEUSES = len(NUCLEUSES)
NUM_CODAS = len(CODAS)

#: The Unicode offset of "가" which is the base offset for all Hangul letters.
FIRST_HANGUL_OFFSET = ord(u'가')


def is_hangul(letter):
    return u'가' <= letter <= u'힣'


def is_consonant(letter):
    return u'ㄱ' <= letter <= u'ㅎ'


def join_phonemes(*args):
    """Joins a Hangul letter from Korean phonemes."""
    # Normalize arguments as onset, nucleus, coda.
    if len(args) == 1:
        # tuple of (onset, nucleus[, coda])
        args = args[0]
    if len(args) == 2:
        args += (CODAS[0],)
    try:
        onset, nucleus, coda = args
    except ValueError:
        raise TypeError('join_phonemes() takes at most 3 arguments')
    offset = (
        (ONSETS.index(onset) * NUM_NUCLEUSES + NUCLEUSES.index(nucleus)) *
        NUM_CODAS + CODAS.index(coda)
    )
    return unichr(FIRST_HANGUL_OFFSET + offset)


def split_phonemes(letter, onset=True, nucleus=True, coda=True):
    """Splits Korean phonemes as known as "자소" from a Hangul letter.

    :returns: (onset, nucleus, coda)
    :raises ValueError: `letter` is not a Hangul single letter.

    """
    if len(letter) != 1 or not is_hangul(letter):
        raise ValueError('Not Hangul letter: %r' % letter)
    offset = ord(letter) - FIRST_HANGUL_OFFSET
    phonemes = [None] * 3
    if onset:
        phonemes[0] = ONSETS[offset // (NUM_NUCLEUSES * NUM_CODAS)]
    if nucleus:
        phonemes[1] = NUCLEUSES[(offset // NUM_CODAS) % NUM_NUCLEUSES]
    if coda:
        phonemes[2] = CODAS[offset % NUM_CODAS]
    return tuple(phonemes)


def combine_words(word1, word2):
    """Combines two words.  If the first word ends with a vowel and the initial
    letter of the second word is only consonant, it merges them into one
    letter::

    >>> combine_words(u'다', u'ㄺ')
    닭
    >>> combine_words(u'가오', u'ㄴ누리')
    가온누리

    """
    if word1 and word2 and is_consonant(word2[0]):
        onset, nucleus, coda = split_phonemes(word1[-1])
        if not coda:
            glue = join_phonemes(onset, nucleus, word2[0])
            return word1[:-1] + glue + word2[1:]
    return word1 + word2
