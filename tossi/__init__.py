# -*- coding: utf-8 -*-
"""
   tossi
   ~~~~~

   Supports Korean particles.

   :copyright: (c) 2016-2017 by What! Studio
   :license: BSD, see LICENSE for more details.

"""
import re
import warnings

from tossi.coda import guess_coda
from tossi.formatter import Formatter
from tossi.particles import Euro, Ida, Particle
from tossi.tolerance import (
    MORPH1_AND_OPTIONAL_MORPH2, MORPH2_AND_OPTIONAL_MORPH1,
    OPTIONAL_MORPH1_AND_MORPH2, OPTIONAL_MORPH2_AND_MORPH1,
    parse_tolerance_style)


__all__ = ['get_particle', 'guess_coda', 'MORPH1_AND_OPTIONAL_MORPH2',
           'MORPH2_AND_OPTIONAL_MORPH1', 'OPTIONAL_MORPH1_AND_MORPH2',
           'OPTIONAL_MORPH2_AND_MORPH1', 'parse', 'parse_tolerance_style',
           'Particle', 'pick', 'postfix', 'postfix_particle',
           'Formatter', 'format']


def index_particles(particles):
    """Indexes :class:`Particle` objects.  It returns a regex pattern which
    matches to any particle morphs and a dictionary indexes the given particles
    by regex groups.
    """
    patterns, indices = [], {}
    for x, p in enumerate(particles):
        group = u'_%d' % x
        indices[group] = x
        patterns.append(u'(?P<%s>%s)' % (group, p.regex_pattern()))
    pattern = re.compile(u'|'.join(patterns))
    return pattern, indices


class ParticleRegistry(object):

    __slots__ = ('default', 'particles', 'pattern', 'indices')

    def __init__(self, default, particles):
        self.default = default
        self.particles = particles
        self.pattern, self.indices = index_particles(particles)

    def _get_by_match(self, match):
        x = self.indices[match.lastgroup]
        return self.particles[x]

    def parse(self, morph):
        m = self.pattern.match(morph)
        if m is None:
            return self.default
        return self._get_by_match(m)

    def pick(self, word, morph, **kwargs):
        particle = self.get(morph)
        return particle.allomorph(word, morph, **kwargs)

    def postfix(self, word, morph, **kwargs):
        return word + self.pick(word, morph, **kwargs)

    def get(self, morph):
        warnings.warn(DeprecationWarning('Use parse() instead'))
        return self.parse(morph)

    def postfix_particle(self, word, morph, **kwargs):
        warnings.warn(DeprecationWarning('Use postfix() instead'))
        return self.postfix(word, morph, **kwargs)


#: The default registry for well-known Korean particles.
registry = ParticleRegistry(Ida, [
    # Simple allomorphic rule:
    Particle(u'이', u'가', final=True),
    Particle(u'을', u'를', final=True),
    Particle(u'은', u'는'),  # "은(는)" includes "은(는)커녕".
    Particle(u'과', u'와'),
    # Vocative particles:
    Particle(u'아', u'야', final=True),
    Particle(u'이여', u'여', final=True),
    Particle(u'이시여', u'시여', final=True),
    # Invariant particles:
    Particle(u'의', final=True),
    Particle(u'도', final=True),
    Particle(u'만'),
    Particle(u'에'),
    Particle(u'께'),
    Particle(u'뿐'),
    Particle(u'하'),
    Particle(u'보다'),
    Particle(u'밖에'),
    Particle(u'같이'),
    Particle(u'부터'),
    Particle(u'까지'),
    Particle(u'마저'),
    Particle(u'조차'),
    Particle(u'마냥'),
    Particle(u'처럼'),
    Particle(u'커녕'),
    # Special particles:
    Euro,
])
formatter = Formatter(registry)


def parse(morph):
    """Shortcut for :class:`ParticleRegistry.parse` of the default registry."""
    return registry.parse(morph)


def pick(word, morph, **kwargs):
    """Shortcut for :class:`ParticleRegistry.pick` of the default registry.
    """
    return registry.pick(word, morph, **kwargs)


def postfix(word, morph, **kwargs):
    """Shortcut for :class:`ParticleRegistry.postfix` of the default registry.
    """
    return registry.postfix(word, morph, **kwargs)


def get_particle(morph):
    warnings.warn(DeprecationWarning('Use parse() instead'))
    return parse(morph)


def postfix_particle(word, morph, **kwargs):
    warnings.warn(DeprecationWarning('Use postfix() instead'))
    return postfix(word, morph, **kwargs)


def format(message, *args, **kwargs):
    """Shortcut for :class:`tossi.Formatter.format` of the default registry.
    """
    return formatter.vformat(message, args, kwargs)
