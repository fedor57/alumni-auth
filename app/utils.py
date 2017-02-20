# -*- coding: utf-8 -*-

import re


LETTER_RE = re.compile(r'^[^\W\d_]$', re.UNICODE)
YEAR_RE = re.compile(r'^\d{2,4}$')
LETTER_YEAR_RE = re.compile(r'^[^\W\d_]\d{2,4}$', re.UNICODE)
YEAR_LETTER_RE = re.compile(r'^\d{2,4}[^\W\d_]$', re.UNICODE)

LETTER_MAP = {
    'a': u'А',
    'b': u'Б',
    'v': u'В',
    'g': u'Г',
    'd': u'Д',
    'm': u'М',
}

for key, value in LETTER_MAP.items():
    LETTER_MAP[key.upper()] = value


def _normalize_year(year):
    if year:
        year = int(year)
        if year < 50:
            year += 2000
        elif year >= 50 and year < 100:
            year += 1900
    return year


def _normalize_letter(letter):
    if letter in LETTER_MAP:
        letter = LETTER_MAP[letter]
    return letter


def split_search(query):
    names = []
    year = None
    letter = None
    terms = query.split()

    for term in terms:
        if LETTER_RE.match(term) and not letter:
            letter = term
        elif YEAR_RE.match(term):
            year = term
        elif LETTER_YEAR_RE.match(term):
            letter, year = term[0], term[1:]
        elif YEAR_LETTER_RE.match(term):
            letter, year = term[-1], term[:-1]
        else:
            names.append(term)

    if letter and not year:
        letter = None
    return names, _normalize_year(year), _normalize_letter(letter)
