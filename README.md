# 토씨

[![Build Status](
  https://travis-ci.org/what-studio/tossi.svg?branch=master
)](https://travis-ci.org/what-studio/tossi)
[![Coverage Status](
  https://coveralls.io/repos/github/what-studio/tossi/badge.svg?branch=master
)](https://coveralls.io/r/what-studio/tossi)
[![README in English](
  https://img.shields.io/badge/readme-english-blue.svg?style=flat
)](README.en.md)

'토씨'는 '조사'의 순우리말 이름입니다. 토씨 라이브러리는 임의의 단어 뒤에 올
가장 자연스러운 한국어 조사 형태를 골라줍니다.

## 설치

```console
$ pip install tossi
```

## 사용법

```python
>>> import tossi
>>> tossi.postfix(u'집', u'(으)로')
집으로
>>> tossi.postfix(u'말', u'으로는')
말로는
>>> tossi.postfix(u'대한민국', u'은(는)')
대한민국은
>>> tossi.postfix(u'민주공화국', u'다')
민주공화국이다
```

## 자연스러운 조사 선택

`의`, `도`, `만~`, `에~`, `께~`, `뿐~`, `하~`, `보다~`, `밖에~`, `같이~`,
`부터~`, `까지~`, `마저~`, `조차~`, `마냥~`, `처럼~`, `커녕~`에는 어떤 단어가
앞서도 형태가 변하지 않습니다:

> 나오**의**, 모리안**의**, 키홀**의**, 나오**도**, 모리안**도**, 키홀**도**

반면 `은(는)`, `이(가)`, `을(를)`, `과(와)~`는 앞선 단어의 마지막 음절의 받침
유무에 따라 형태가 달라집니다:

> 나오**는**, 모리안**은**, 키홀**은**

`(으)로~`도 비슷한 규칙을 따르지만 앞선 받침이 `ㄹ`일 경우엔 받침이 없는 것과
같게 취급합니다:

> 나오**로**, 모리안**으로**, 키홀**로**

서술격 조사 `(이)다`는 어미가 활용되어 다양한 형태로 변형될 수 있습니다:

> 나오**지만**, 모리안**이지만**, 키홀**이에요**, 나오**예요**

토씨는 가장 자연스러운 조사 형태를 선택합니다.  만약 어떤 형태가 자연스러운지
알 수 없을 때에는 `은(는)`, `(으)로`처럼 모든 형태를 병기합니다:

```python
>>> tossi.postfix(u'벽돌', u'으로')
벽돌로
>>> tossi.postfix(u'짚', u'으로')
짚으로
>>> tossi.postfix(u'黃金', u'으로')
黃金(으)로
```

단어가 숫자로 끝나더라도 자연스러운 조사 형태가 선택됩니다:

```python
>>> tossi.postfix(u'레벨 10', u'이')
레벨 10이
>>> tossi.postfix(u'레벨 999', u'이')
레벨 999가
```

괄호 속 단어나 구두점은 조사 형태를 선택할 때 참고하지 않습니다:

```python
>>> tossi.postfix(u'나뭇가지(만렙)', u'을')
나뭇가지(만렙)를
```

## 병기 순서

조사의 형태를 모두 병기해야할 때 병기할 순서를 고를 수 있습니다. 가령 대부분의
인자가 일본어 단어일 경우엔 단어가 모음으로 끝날 확률이 높습니다. 이 경우
기본형인 `은(는)` 스타일보단 `는(은)` 스타일이 더 자연스러울 수 있습니다:

```python
>>> tolerance_style = tossi.parse_tolerance_style(u'는(은)')
>>> tossi.postfix(u'さくら', u'이', tolerance_style=tolerance_style)
さくら가(이)
```

`은(는)`, `(은)는`, `는(은)`, `(는)은` 네 가지 스타일 중 프로젝트에 맞는 것을
고르세요.

## API

### `tossi.pick(word, morph) -> str`

`word`에 자연스럽게 뒤따르는 조사 형태를 구합니다.

```python
>>> tossi.pick(u'토씨', '은')
는
>>> tossi.pick(u'우리말', '은')
은
```

### `tossi.postfix(word, morph) -> str`

단어와 조사를 자연스럽게 연결합니다.

```python
>>> tossi.postfix(u'토씨', '은')
토씨는
>>> tossi.postfix(u'우리말', '은')
우리말은
```

### `tossi.parse(morph) -> Particle`

문자열로 된 조사 표기로부터 조사 객체를 얻습니다.

```python
>>> tossi.parse(u'으로')
<Particle: u'(으)로'>
>>> tossi.parse(u'(은)는')
<Particle: u'은(는)'>
>>> tossi.parse(u'이면')
<Particle: u'(이)'>
```

### `Particle[word[:morph]] -> str`

`word`에 뒤따르는 표기를 구합니다.

```python
>>> Eun = tossi.parse(u'은')
>>> Eun[u'라면']
은
>>> Eun[u'라볶이']
는
```

`morph`를 지정해서 어미에 변화를 줄 수 있습니다.

```python
>>> Euro = tossi.parse(u'으로')
>>> Euro[u'라면':u'으론']
으론
>>> Euro[u'라볶이':u'으론']
론
```

## 만든이와 사용권

[넥슨][nexon] [왓 스튜디오][what-studio]의 [이흥섭][sublee]과
[김찬웅][kexplo]이 만들었고 [제3조항을 포함하는 BSD 허가서][bsd-3-clause]를
채택했습니다.

[nexon]: http://nexon.com/
[what-studio]: https://github.com/what-studio
[sublee]: http://subl.ee/
[kexplo]: http://chanwoong.kim/
[bsd-3-clause]: http://opensource.org/licenses/BSD-3-Clause
