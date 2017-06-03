# Tossi

[![Build Status](
  https://travis-ci.org/what-studio/tossi.svg?branch=master
)](https://travis-ci.org/what-studio/tossi)
[![Coverage Status](
  https://coveralls.io/repos/github/what-studio/tossi/badge.svg?branch=master
)](https://coveralls.io/r/what-studio/tossi)

"Tossi(토씨)" is a pure-Korean name for grammatical particles.  Some of Korean
particles has allomorphic variant forms depending on a leading word.  The Tossi
library determines most natrual form.

## Installation

```console
$ pip install tossi
```

## Usage

```python
>>> import tossi
>>> tossi.postfix_particle(u'집', u'(으)로')
집으로
>>> tossi.postfix_particle(u'말', u'으로는')
말로는
>>> tossi.postfix_particle(u'대한민국', u'은(는)')
대한민국은
>>> tossi.postfix_particle(u'민주공화국', u'다')
민주공화국이다
```

## Natural Form for Particles

These particles do not have allomorphic variant.  They always appear in same
form: `의`, `도`, `만~`, `에~`, `께~`, `뿐~`, `하~`, `보다~`, `밖에~`, `같이~`,
`부터~`, `까지~`, `마저~`, `조차~`, `마냥~`, `처럼~`, and `커녕~`:

> 나오**의**, 모리안**의**, 키홀**의**, 나오**도**, 모리안**도**, 키홀**도**

Meanwhile, these particles appear in different form depending on whether the
leading word have a final consonant or not: `은(는)`, `이(가)`, `을(를)`, and
`과(와)~`:

> 나오**는**, 모리안**은**, 키홀**은**

`(으)로~` also have similar rule but if the final consonant is `ㄹ`, it appears
same with after non final consonant:

> 나오**로**, 모리안**으로**, 키홀**로**

`(이)다` which is a predicative particle have more diverse forms.  Its end can
be inflected in general:

> 나오**지만**, 모리안**이지만**, 키홀**이에요**, 나오**예요**

Tossi tries to determine most natrual form for particles.  But if it fails to
do, determines both forms like `은(는)` or `(으)로` for tolerance:

```python
>>> tossi.postfix_particle(u'벽돌', u'으로')
벽돌로
>>> tossi.postfix_particle(u'짚', u'으로')
짚으로
>>> tossi.postfix_particle(u'黃金', u'으로')
黃金(으)로
```

If the leading word ends with number, a natural form can be determined:

```python
>>> tossi.postfix_particle(u'레벨 10', u'이')
레벨 10이
>>> tossi.postfix_particle(u'레벨 999', u'이')
레벨 999가
```

Words in a parentheses are ignored:

```python
>>> tossi.postfix_particle(u'나뭇가지(만렙)', u'을')
나뭇가지(만렙)를
```

## Tolerance Styles

When Tossi can't determine the natural form, the result includes the both
forms.  In this case, you can choose the order of the forms.  For example, if
the most words are Japanese, they probably will not end with final consonants.
Therefore `는(은)` is better than `은(는)` which is the default style:

```python
>>> tolerance_style = tossi.parse_tolerance_style(u'는(은)')
>>> tossi.postfix_particle(u'さくら', u'이', tolerance_style=tolerance_style)
さくら가(이)
```

Choose one of `은(는)`, `(은)는`, `는(은)`, `(는)은` for your project.

## Licensing

Written by [Heungsub Lee][sublee] and [Chanwoong Kim][kexplo] at
[What! Studio][what-studio] in [Nexon][nexon], and distributed under
[the BSD 3-Clause license][bsd-3-clause].

[nexon]: http://nexon.com/
[what-studio]: https://github.com/what-studio
[sublee]: http://subl.ee/
[kexplo]: http://chanwoong.kim/
[bsd-3-clause]: http://opensource.org/licenses/BSD-3-Clause
