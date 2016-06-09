# -*- coding: utf-8 -*-
"""
   tossi
   ~~~~~

   Supports Korean particles.

   :copyright: (c) 2016 by What! Studio
   :license: BSD, see LICENSE for more details.

"""
import re

from .particles import Euro, Ida, Particle
from .tolerance import (
    FORM1_AND_OPTIONAL_FORM2, FORM2_AND_OPTIONAL_FORM1,
    OPTIONAL_FORM1_AND_FORM2, OPTIONAL_FORM2_AND_FORM1, parse_tolerance_style)


__all__ = ['FORM1_AND_OPTIONAL_FORM2', 'FORM2_AND_OPTIONAL_FORM1',
           'get_particle', 'guess_particle', 'OPTIONAL_FORM1_AND_FORM2',
           'OPTIONAL_FORM2_AND_FORM1', 'parse_tolerance_style', 'Particle',
           'postfix_particle']


def index_particles(particles):
    """Indexes :class:`Particle` objects.  It returns a regex pattern which
    matches to any particle forms and a dictionary indexes the given particles
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

    def get(self, form):
        m = self.pattern.match(form)
        if m is None:
            return self.default
        return self._get_by_match(m)

    def postfix_particle(self, word, form, **kwargs):
        particle = self.get(form)
        return word + particle.allomorph(word, form, **kwargs)


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


def get_particle(form):
    """Shortcut for :class:`ParticleRegistry.get` of the default registry."""
    return registry.get(form)


def postfix_particle(word, form, **kwargs):
    """Shortcut for :class:`ParticleRegistry.postfix_particle` of the default
    registry.
    """
    return registry.postfix_particle(word, form, **kwargs)
