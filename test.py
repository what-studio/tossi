# -*- coding: utf-8 -*-
import pytest
from six import PY2, text_type as str, with_metaclass

from tossi import get_particle, postfix_particle as f, registry
from tossi.coda import pick_coda_from_decimal
from tossi.hangul import join_phonemes, split_phonemes
from tossi.particles import Euro, Ida, Particle, SingletonParticleMeta
from tossi.tolerance import (
    generate_tolerances, get_tolerance, get_tolerance_from_iterator,
    MORPH1_AND_OPTIONAL_MORPH2, MORPH1_ONLY, MORPH2_ONLY,
    OPTIONAL_MORPH2_AND_MORPH1, parse_tolerance_style)


Eun = get_particle(u'은')
Eul = get_particle(u'을')
Gwa = get_particle(u'과')


def test_about():
    __import__('tossi.__about__')


def test_particle():
    assert str(Eun) == u'은(는)'
    assert str(Eul) == u'을(를)'
    assert str(Ida) == u'(이)'
    if PY2:
        try:
            __import__('unidecode')
        except ImportError:
            assert repr(Ida) == u"<Particle: u'(\\uc774)'>"
        else:
            assert repr(Ida) == u'<Particle: (i)>'
    else:
        assert repr(Ida) == u'<Particle: (이)>'


def test_frontend():
    assert get_particle(u'을') is Eul
    assert get_particle(u'를') is Eul
    assert get_particle(u'을(를)') is Eul
    assert get_particle(u'이다') is Ida
    assert get_particle(u'이었다') is Ida


def test_split_phonemes():
    assert split_phonemes(u'쏚') == (u'ㅆ', u'ㅗ', u'ㄲ')
    assert split_phonemes(u'섭') == (u'ㅅ', u'ㅓ', u'ㅂ')
    assert split_phonemes(u'투') == (u'ㅌ', u'ㅜ', u'')
    assert split_phonemes(u'투', onset=False) == (None, u'ㅜ', u'')
    with pytest.raises(ValueError):
        split_phonemes(u'X')
    with pytest.raises(ValueError):
        split_phonemes(u'섭섭')


def test_join_phonemes():
    assert join_phonemes(u'ㅅ', u'ㅓ', u'ㅂ') == u'섭'
    assert join_phonemes((u'ㅅ', u'ㅓ', u'ㅂ')) == u'섭'
    assert join_phonemes(u'ㅊ', u'ㅠ') == u'츄'
    assert join_phonemes(u'ㅊ', u'ㅠ', u'') == u'츄'
    assert join_phonemes((u'ㅊ', u'ㅠ')) == u'츄'
    with pytest.raises(TypeError):
        join_phonemes(u'ㄷ', u'ㅏ', u'ㄹ', u'ㄱ')


def test_particle_tolerances():
    t = lambda _1, _2: set(generate_tolerances(_1, _2))
    s = lambda x: set(x.split(' '))
    assert t(u'이', u'가') == s(u'이(가) (이)가 가(이) (가)이 이 가')
    assert t(u'이', u'') == s(u'(이) 이 ')
    assert t(u'으로', u'로') == s(u'(으)로 으로 로')
    assert t(u'이여', u'여') == s(u'(이)여 이여 여')
    assert t(u'이시여', u'시여') == s(u'(이)시여 이시여 시여')
    assert t(u'아', u'야') == s(u'아(야) (아)야 야(아) (야)아 아 야')
    assert \
        t(u'가나다', u'나나다') == \
        s(u'가(나)나다 (가)나나다 나(가)나다 (나)가나다 가나다 나나다')
    assert \
        t(u'가나다', u'마바사') == \
        s(u'가나다(마바사) (가나다)마바사 마바사(가나다) (마바사)가나다 가나다 마바사')


def test_euro():
    assert Euro[u'나오'] == u'로'
    assert Euro[u'키홀'] == u'로'
    assert Euro[u'모리안'] == u'으로'
    assert Euro[u'Nao'] == u'(으)로'
    assert Euro[u'나오':u'로서'] == u'로서'
    assert Euro[u'키홀':u'로서'] == u'로서'
    assert Euro[u'모리안':u'로서'] == u'으로서'
    assert Euro[u'나오':u'로써'] == u'로써'
    assert Euro[u'키홀':u'로써'] == u'로써'
    assert Euro[u'모리안':u'로써'] == u'으로써'
    assert Euro[u'나오':u'로부터'] == u'로부터'
    assert Euro[u'키홀':u'로부터'] == u'로부터'
    assert Euro[u'모리안':u'로부터'] == u'으로부터'
    assert Euro[u'나오':u'(으)로부터의'] == u'로부터의'
    assert Euro[u'밖':u'론'] == u'으론'


def test_combinations():
    assert f(u'이 방법', u'만으로는') == u'이 방법만으로는'
    assert f(u'나', u'조차도') == u'나조차도'
    assert f(u'그 친구', u'과는') == u'그 친구와는'
    assert f(u'그것', u'와는') == u'그것과는'
    assert f(u'사건', u'과(와)는') == u'사건과는'
    assert f(u'그 친구', u'관') == u'그 친구완'


def test_exceptions():
    # Empty.
    assert f(u'', u'를') == u'을(를)'
    # Onsets only.
    assert f(u'ㅋㅋㅋ', u'를') == u'ㅋㅋㅋ을(를)'


def test_insignificant():
    assert f(u'나오(Lv.25)', u'으로') == u'나오(Lv.25)로'
    assert f(u'나오 (Lv.25)', u'을') == u'나오 (Lv.25)를'
    assert f(u'나(?)오', u'으로') == u'나(?)오로'
    assert f(u'헬로월드!', u'으로') == u'헬로월드!로'
    assert f(u'?_?', u'으로') == u'?_?(으)로'
    assert f(u'임창정,,,', u'가') == u'임창정,,,이'
    assert f(u'《듀랑고》', u'을') == u'《듀랑고》를'
    assert f(u'불완전괄호)', u'은') == u'불완전괄호)는'
    assert f(u'이상한괄호)))', u'는') == u'이상한괄호)))는'
    assert f(u'이상한괄호)()', u'은') == u'이상한괄호)()는'
    assert f(u'이상한괄호())', u'(는)은') == u'이상한괄호())는'
    assert f(u'^_^', u'이었다.') == u'^_^(이)었다.'
    assert f(u'웃는얼굴^_^', u'이었다.') == u'웃는얼굴^_^이었다.'
    assert f(u'폭탄(가짜)...', u'이었다.') == u'폭탄(가짜)...이었다.'
    assert f(u'16(7)?!', u'으로') == u'16(7)?!으로'
    assert f(u'7(16)?!', u'으로') == u'7(16)?!로'
    assert f(u'검색\ue000', u'를') == u'검색\ue000을'


def test_only_parentheses():
    assert f(u'(1, 2)', u'를') == u'(1, 2)를'
    assert f(u'(2, 3)', u'를') == u'(2, 3)을'


def test_vocative_particles():
    assert f(u'친구', u'야') == u'친구야'
    assert f(u'사랑', u'야') == u'사랑아'
    assert f(u'사랑', u'아') == u'사랑아'
    assert f(u'친구', u'여') == u'친구여'
    assert f(u'사랑', u'여') == u'사랑이여'
    assert f(u'하늘', u'이시여') == u'하늘이시여'
    assert f(u'바다', u'이시여') == u'바다시여'


def test_ida():
    """Cases for '이다' which is a copulative and existential verb."""
    # Do or don't inject '이'.
    assert f(u'나오', u'이다') == u'나오다'
    assert f(u'키홀', u'이다') == u'키홀이다'
    # Merge with the following vowel as /j/.
    assert f(u'나오', u'이에요') == u'나오예요'
    assert f(u'키홀', u'이에요') == u'키홀이에요'
    # No allomorphs.
    assert f(u'나오', u'입니다') == u'나오입니다'
    assert f(u'키홀', u'입니다') == u'키홀입니다'
    # Give up to select an allomorph.
    assert f(u'God', u'이다') == u'God(이)다'
    assert f(u'God', u'이에요') == u'God(이)에요'
    assert f(u'God', u'입니다') == u'God입니다'
    assert f(u'God', u'였습니다') == u'God(이)었습니다'
    # Many examples.
    assert f(u'키홀', u'였습니다') == u'키홀이었습니다'
    assert f(u'나오', u'였습니다') == u'나오였습니다'
    assert f(u'나오', u'이었다') == u'나오였다'
    assert f(u'나오', u'이었지만') == u'나오였지만'
    assert f(u'나오', u'이지만') == u'나오지만'
    assert f(u'키홀', u'이지만') == u'키홀이지만'
    assert f(u'나오', u'지만') == u'나오지만'
    assert f(u'키홀', u'지만') == u'키홀이지만'
    assert f(u'나오', u'다') == u'나오다'
    assert f(u'키홀', u'다') == u'키홀이다'
    assert f(u'나오', u'이에요') == u'나오예요'
    assert f(u'키홀', u'이에요') == u'키홀이에요'
    assert f(u'나오', u'고') == u'나오고'
    assert f(u'키홀', u'고') == u'키홀이고'
    assert f(u'모리안', u'고') == u'모리안이고'
    assert f(u'나오', u'여서') == u'나오여서'
    assert f(u'키홀', u'여서') == u'키홀이어서'
    assert f(u'나오', u'이어서') == u'나오여서'
    assert f(u'키홀', u'라고라') == u'키홀이라고라'
    assert f(u'키홀', u'든지') == u'키홀이든지'
    assert f(u'키홀', u'던가') == u'키홀이던가'
    assert f(u'키홀', u'여도') == u'키홀이어도'
    assert f(u'키홀', u'야말로') == u'키홀이야말로'
    assert f(u'키홀', u'인양') == u'키홀인양'
    assert f(u'나오', u'인양') == u'나오인양'


def test_invariant_particles():
    assert f(u'나오', u'도') == u'나오도'
    assert f(u'모리안', u'도') == u'모리안도'
    assert f(u'판교', u'에서') == u'판교에서'
    assert f(u'판교', u'에서는') == u'판교에서는'
    assert f(u'선생님', u'께서도') == u'선생님께서도'
    assert f(u'나오', u'의') == u'나오의'
    assert f(u'모리안', u'만') == u'모리안만'
    assert f(u'키홀', u'하고') == u'키홀하고'
    assert f(u'콩', u'만큼') == u'콩만큼'
    assert f(u'콩', u'마냥') == u'콩마냥'
    assert f(u'콩', u'처럼') == u'콩처럼'


def test_tolerances():
    assert f(u'나오', u'은(는)') == u'나오는'
    assert f(u'나오', u'(은)는') == u'나오는'
    assert f(u'나오', u'는(은)') == u'나오는'
    assert f(u'나오', u'(는)은') == u'나오는'
    assert f(u'나오', u'은') == u'나오는'
    assert f(u'나오', u'는') == u'나오는'


def test_decimal():
    assert f(u'레벨30', u'이') == u'레벨30이'
    assert f(u'레벨34', u'이') == u'레벨34가'
    assert f(u'레벨7', u'으로') == u'레벨7로'
    assert f(u'레벨42', u'으로') == u'레벨42로'
    assert f(u'레벨100', u'으로') == u'레벨100으로'
    assert pick_coda_from_decimal('1') == u'ㄹ'
    assert pick_coda_from_decimal('2') == u''
    assert pick_coda_from_decimal('3') == u'ㅁ'
    assert pick_coda_from_decimal('10') == u'ㅂ'
    assert pick_coda_from_decimal('16') == u'ㄱ'
    assert pick_coda_from_decimal('19') == u''
    assert pick_coda_from_decimal('200') == u'ㄱ'
    assert pick_coda_from_decimal('30000') == u'ㄴ'
    assert pick_coda_from_decimal('400000') == u'ㄴ'
    assert pick_coda_from_decimal('500000000') == u'ㄱ'
    assert pick_coda_from_decimal('1' + '0' * 50) == u'ㄱ'
    assert pick_coda_from_decimal('1' + '0' * 100) is None
    assert pick_coda_from_decimal('0') == u'ㅇ'
    assert pick_coda_from_decimal('1.0') == u'ㅇ'
    assert pick_coda_from_decimal('1.234567890') == u'ㅇ'
    assert pick_coda_from_decimal('3.14') == u''


def test_match():
    # (n)eun
    assert Eun.match(u'은') == u''
    assert Eun.match(u'는') == u''
    assert Eun.match(u'은(는)') == u''
    assert Eun.match(u'는(은)') == u''
    assert Eun.match(u'(은)는') == u''
    assert Eun.match(u'(는)은') == u''
    assert Eun.match(u'는는') == u'는'
    # (r)eul (final=True)
    assert Eul.match(u'를') == u''
    assert Eul.match(u'을을') is None
    # (g)wa
    assert Gwa.match(u'과') == u''
    assert Gwa.match(u'과는') == u'는'
    assert Gwa.match(u'관') == u'ㄴ'
    # (eu)ro
    assert Euro.match(u'으로도') == u'도'
    assert Euro.match(u'론') == u'ㄴ'


def test_combine():
    assert Euro[u'집':u'로'] == u'으로'
    assert Euro[u'집':u'론'] == u'으론'
    assert Euro[u'집':u'로는'] == u'으로는'
    assert Euro[u'집':u'론123'] == u'으론123'


def test_tolerances_for_coda_combination():
    assert Euro[u'Hello':u'론'] == u'(으)론'
    assert Gwa[u'Hello':u'완'] == u'관(완)'
    assert Gwa[u'Hello':u'완':OPTIONAL_MORPH2_AND_MORPH1] == u'(완)관'
    assert Gwa[u'Hello':u'완완완'] == u'관(완)완완'
    assert Particle(u'크', u'')[u'Hello':u'큰큰'] == u'(큰)큰'


def test_igyuho2006():
    """Particles from <Classification and List of Conjunctive Particles>,
    I Gyu-ho, 2006.
    """
    def ff(particle_string):
        return f(u'남', particle_string), f(u'나', particle_string)
    # p181-182:
    assert ff(u'의') == (u'남의', u'나의')
    assert ff(u'과') == (u'남과', u'나와')
    assert ff(u'와') == (u'남과', u'나와')
    assert ff(u'하고') == (u'남하고', u'나하고')
    assert ff(u'이랑') == (u'남이랑', u'나랑')
    assert ff(u'이니') == (u'남이니', u'나니')
    assert ff(u'이다') == (u'남이다', u'나다')
    assert ff(u'이라든가') == (u'남이라든가', u'나라든가')
    assert ff(u'이라든지') == (u'남이라든지', u'나라든지')
    assert ff(u'이며') == (u'남이며', u'나며')
    assert ff(u'이야') == (u'남이야', u'나야')
    assert ff(u'이요') == (u'남이요', u'나요')
    assert ff(u'이랴') == (u'남이랴', u'나랴')
    assert ff(u'에') == (u'남에', u'나에')
    assert ff(u'하며') == (u'남하며', u'나하며')
    assert ff(u'커녕') == (u'남커녕', u'나커녕')
    assert ff(u'은커녕') == (u'남은커녕', u'나는커녕')
    assert ff(u'이고') == (u'남이고', u'나고')
    assert ff(u'이나') == (u'남이나', u'나나')
    assert ff(u'에다') == (u'남에다', u'나에다')
    assert ff(u'에다가') == (u'남에다가', u'나에다가')
    assert ff(u'이란') == (u'남이란', u'나란')
    assert ff(u'이면') == (u'남이면', u'나면')
    assert ff(u'이거나') == (u'남이거나', u'나거나')
    assert ff(u'이건') == (u'남이건', u'나건')
    assert ff(u'이든') == (u'남이든', u'나든')
    assert ff(u'이든가') == (u'남이든가', u'나든가')
    assert ff(u'이든지') == (u'남이든지', u'나든지')
    assert ff(u'인가') == (u'남인가', u'나인가')
    assert ff(u'인지') == (u'남인지', u'나인지')
    # p188-189:
    assert ff(u'인') == (u'남인', u'나인')
    assert ff(u'는') == (u'남은', u'나는')
    assert ff(u'이라는') == (u'남이라는', u'나라는')
    assert ff(u'이네') == (u'남이네', u'나네')
    assert ff(u'도') == (u'남도', u'나도')
    assert ff(u'이면서') == (u'남이면서', u'나면서')
    assert ff(u'이자') == (u'남이자', u'나자')
    assert ff(u'하고도') == (u'남하고도', u'나하고도')
    assert ff(u'이냐') == (u'남이냐', u'나냐')


def test_tolerance_style():
    assert Gwa[u'Hello'::OPTIONAL_MORPH2_AND_MORPH1] == u'(와)과'
    assert parse_tolerance_style(0) == MORPH1_AND_OPTIONAL_MORPH2
    assert parse_tolerance_style(u'을(를)') == MORPH1_AND_OPTIONAL_MORPH2
    assert parse_tolerance_style(u'(를)을') == OPTIONAL_MORPH2_AND_MORPH1
    assert parse_tolerance_style(u'과') == MORPH1_ONLY
    assert parse_tolerance_style(u'로') == MORPH2_ONLY
    with pytest.raises(ValueError):
        parse_tolerance_style(u'이다')
    with pytest.raises(ValueError):
        parse_tolerance_style(u'만')
    parse_tolerance_style(u'(이)') == MORPH1_AND_OPTIONAL_MORPH2
    assert get_tolerance([u'예제'], OPTIONAL_MORPH2_AND_MORPH1) == u'예제'
    assert get_tolerance_from_iterator(iter([u'예제']),
                                       OPTIONAL_MORPH2_AND_MORPH1) == u'예제'


def test_custom_guess_coda():
    def dont_guess_coda(word):
        return None
    assert Euro.allomorph(u'밖', u'으로',
                          guess_coda=dont_guess_coda) == u'(으)로'


def test_unmatch():
    assert Eul[u'예제':u'는'] is None


def test_singleton_error():
    with pytest.raises(TypeError):
        class Fail(with_metaclass(SingletonParticleMeta, object)):
            pass


def test_deprecations():
    pytest.deprecated_call(registry.postfix_particle, u'테스트', u'으로부터')
