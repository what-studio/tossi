# -*- coding: utf-8 -*-
"""
   tossi.particles
   ~~~~~~~~~~~~~~~

   Models for Korean allomorphic particles.

   :copyright: (c) 2016 by What! Studio
   :license: BSD, see LICENSE for more details.

"""
from itertools import chain
import re

from bidict import bidict
from six import PY2, python_2_unicode_compatible, text_type, with_metaclass

from .coda import guess_coda, pick_coda_from_letter
from .hangul import combine_words, is_consonant, join_phonemes, split_phonemes
from .tolerance import (
    generate_tolerances, get_tolerance, get_tolerance_from_iterator,
    MORPH1_AND_OPTIONAL_MORPH2)
from .utils import cached_property, CacheMeta


__all__ = ['DEFAULT_GUESS_CODA', 'DEFAULT_TOLERANCE_STYLE',
           'Euro', 'Ida', 'Particle']


#: The default tolerance style.
DEFAULT_TOLERANCE_STYLE = MORPH1_AND_OPTIONAL_MORPH2

#: The default function to guess the coda from a word.
DEFAULT_GUESS_CODA = guess_coda


@python_2_unicode_compatible
class Particle(with_metaclass(CacheMeta)):
    """Represents a Korean particle as known as "조사".

    This also implements the general allomorphic rule for most common
    particles.

    :param morph1: an allomorph after a consonant.
    :param morph2: an allomorph after a vowel.  If it is omitted, there's no
                  no alternative allomorph.  So `morph1` always will be
                  selected.
    :param final: whether the particle disallows combination with another
                  postpositions.  (default: ``False``)

    """

    __slots__ = ('morph1', 'morph2', 'final')

    def __init__(self, morph1, morph2=None, final=False):
        self.morph1 = morph1
        self.morph2 = morph1 if morph2 is None else morph2
        self.final = final

    @cached_property
    def tolerances(self):
        """The tuple containing all the possible tolerant morphs."""
        return tuple(generate_tolerances(self.morph1, self.morph2))

    def tolerance(self, style=DEFAULT_TOLERANCE_STYLE):
        """Gets a tolerant morph."""
        return get_tolerance(self.tolerances, style)

    def rule(self, coda):
        """Determines one of allomorphic morphs based on a coda."""
        if coda:
            return self.morph1
        else:
            return self.morph2

    def allomorph(self, word, morph, tolerance_style=DEFAULT_TOLERANCE_STYLE,
                  guess_coda=DEFAULT_GUESS_CODA):
        """Determines one of allomorphic morphs based on a word.

        .. see also:: :meth:`allomorph`.

        """
        suffix = self.match(morph)
        if suffix is None:
            return None
        coda = guess_coda(word)
        if coda is not None:
            # Coda guessed successfully.
            morph = self.rule(coda)
        elif isinstance(tolerance_style, text_type):
            # User specified the style themselves
            morph = tolerance_style
        elif not suffix or not is_consonant(suffix[0]):
            # Choose the tolerant morph.
            morph = self.tolerance(tolerance_style)
        else:
            # Suffix starts with a consonant.  Generate a new tolerant morph
            # by combined morphs.
            morph1 = (combine_words(self.morph1, suffix)
                      if self.morph1 else suffix[1:])
            morph2 = (combine_words(self.morph2, suffix)
                      if self.morph2 else suffix[1:])
            tolerances = generate_tolerances(morph1, morph2)
            return get_tolerance_from_iterator(tolerances, tolerance_style)
        return combine_words(morph, suffix)

    def __getitem__(self, key):
        """The syntax sugar to determine one of allomorphic morphs based on a
        word::

           eun = Particle(u'은', u'는')
           assert eun[u'나오'] == u'는'
           assert eun[u'모리안'] == u'은'

        """
        if isinstance(key, slice):
            word = key.start
            morph = key.stop or self.morph1
            tolerance_style = key.step or DEFAULT_TOLERANCE_STYLE
        else:
            word, morph = key, self.morph1
            tolerance_style = DEFAULT_TOLERANCE_STYLE
        return self.allomorph(word, morph, tolerance_style)

    @cached_property
    def regex(self):
        return re.compile(self.regex_pattern())

    @cached_property
    def morphs(self):
        """The tuple containing the given morphs and all the possible tolerant
        morphs.  Longer is first.
        """
        seen = set()
        saw = seen.add
        morphs = chain([self.morph1, self.morph2], self.tolerances)
        unique_morphs = (x for x in morphs if x and not (x in seen or saw(x)))
        return tuple(sorted(unique_morphs, key=len, reverse=True))

    def match(self, morph):
        m = self.regex.match(morph)
        if m is None:
            return None
        x = m.end()
        if self.final or m.group() == self.morphs[m.lastindex - 1]:
            return morph[x:]
        coda = pick_coda_from_letter(morph[x - 1])
        return coda + morph[x:]

    def regex_pattern(self):
        if self.final:
            return u'^(?:%s)$' % u'|'.join(re.escape(f) for f in self.morphs)
        patterns = []
        for morph in self.morphs:
            try:
                onset, nucleus, coda = split_phonemes(morph[-1])
            except ValueError:
                coda = None
            if coda == u'':
                start = morph[-1]
                end = join_phonemes(onset, nucleus, u'ㅎ')
                pattern = re.escape(morph[:-1]) + u'[%s-%s]' % (start, end)
            else:
                pattern = re.escape(morph)
            patterns.append(pattern)
        return u'^(?:%s)' % u'|'.join(u'(%s)' % p for p in patterns)

    def __str__(self):
        return self.tolerance()

    if PY2:
        def __repr__(self):
            try:
                from unidecode import unidecode
            except ImportError:
                return '<Particle: %r>' % self.tolerance()
            else:
                return '<Particle: %s>' % unidecode(self.tolerance())
    else:
        def __repr__(self):
            return '<Particle: %s>' % self.tolerance()


class SingletonParticleMeta(type(Particle)):

    def __new__(meta, name, bases, attrs):
        base_meta = super(SingletonParticleMeta, meta)
        cls = base_meta.__new__(meta, name, bases, attrs)
        if not issubclass(cls, Particle):
            raise TypeError('Not particle class')
        # Instantiate directly instead of returning a class.
        return cls()


class SingletonParticle(Particle):

    # Concrete classes should set these strings.
    morph1 = morph2 = final = NotImplemented

    def __init__(self):
        pass


def singleton_particle(*bases):
    """Defines a singleton instance immediately when defining the class.  The
    name of the class will refer the instance instead.
    """
    return with_metaclass(SingletonParticleMeta, SingletonParticle, *bases)


class Euro(singleton_particle(Particle)):
    """Particles starting with "으로" have a special allomorphic rule after
    coda "ㄹ".  "으로" can also be extended with some of suffixes such as
    "으로서", "으로부터".
    """

    __slots__ = ()

    morph1 = u'으로'
    morph2 = u'로'
    final = False

    def rule(self, coda):
        if coda and coda != u'ㄹ':
            return self.morph1
        else:
            return self.morph2


class Ida(singleton_particle(Particle)):
    """"이다" is a verbal prticle.  Like other Korean verbs, it is also
    fusional.
    """

    __slots__ = ()

    morph1 = u'이'
    morph2 = u''
    final = False

    #: Matches with initial "이" or "(이)" to normalize fusioned verbal morphs.
    I_PATTERN = re.compile(u'^이|\(이\)')

    #: The mapping for vowels which should be transmorphed by /j/ injection.
    J_INJECTIONS = bidict({u'ㅓ': u'ㅕ', u'ㅔ': u'ㅖ'})

    def allomorph(self, word, morph, tolerance_style=DEFAULT_TOLERANCE_STYLE,
                  guess_coda=DEFAULT_GUESS_CODA):
        suffix = self.I_PATTERN.sub(u'', morph)
        coda = guess_coda(word)
        next_onset, next_nucleus, next_coda = split_phonemes(suffix[0])
        if next_onset == u'ㅇ':
            if next_nucleus == u'ㅣ':
                # No allomorphs when a morph starts with "이" and has a coda.
                return suffix
            mapping = None
            if coda == u'' and next_nucleus in self.J_INJECTIONS:
                # Squeeze "이어" or "이에" to "여" or "예"
                # after a word which ends with a nucleus.
                mapping = self.J_INJECTIONS
            elif coda != u'' and next_nucleus in self.J_INJECTIONS.inv:
                # Lengthen "여" or "예" to "이어" or "이에"
                # after a word which ends with a consonant.
                mapping = self.J_INJECTIONS.inv
            if mapping is not None:
                next_nucleus = mapping[next_nucleus]
                next_letter = join_phonemes(u'ㅇ', next_nucleus, next_coda)
                suffix = next_letter + suffix[1:]
        if coda is None:
            morph = self.tolerance(tolerance_style)
        else:
            morph = self.rule(coda)
        return morph + suffix
