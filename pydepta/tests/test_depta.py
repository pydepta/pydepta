# -*- coding: utf8 -*-
import codecs
import unittest
import os
import re
import json
from ..depta import Depta
from ..mdr import element_repr, dict_to_region

CASES = [
    ('1', 'http://www.iens.nl/restaurant/10545/enschede-rhodos', {
        'test-index': 5
        }),

    ('2', 'http://www.diningcity.com/en/zeeland/restaurant_oesterbeurs', {
        'start-element': ('<div #review_content .>', 3, 1, 4),
        'test-index': 9
        }),

    ('3', 'http://www.iens.nl/restaurant/12229/nijmegen-pasta-e-fagioli', {
        'start-element': ('<hr #greyBreak .>', 8, 4, 20),
        'test-index': 5,
        }),

    ('4', 'http://www.yp.com.hk/Dining-Entertainment-Shopping-Travel-b/Entertainment-Production-Services/CD-VCD-DVD-Manufacturers/p1/en/', {
        'start-element': ('<div #listing_div .>', 1, 1, 12),
        }),

    ('5', 'http://www.eet.nu/enschede/rhodos', {
        'start-element': ('<li #feedback has-ratings has-scores .review_578725>', 2, 1, 20),
        }),
    ]

INFER_CASES = [
    ('6', 'http://www.diningcity.com/en/zeeland/restaurant_nelsons', {
        # seed trained from 2.html
        'seed': '2.json',
        'data': {'Service': '8.0',
                 'Atmosphere': '7.0',
                 'Cuisine': '9.0',
                 'General': '8.0',
                 'text': 'Heerlijk gegeten',
                 'date': '06 Sep 2013, 17:59'},
        'expected': {
            # empty
        }
    }),

    ('7', 'http://www.diningcity.com/en/zeeland/restaurant_hetbadpaviljoen', {
        # seed trained from 2.html
        'seed': '2.json',
        'data': {'Service': '8.0',
                 'Atmosphere': '7.0',
                 'Cuisine': '9.0',
                 'General': '8.0',
                 'text': 'Heerlijk gegeten',
                 'date': '06 Sep 2013, 17:59'},
        'expected': {u'Cuisine': [u'9.0', u'3.0', u'8.0', u'10.0'],
                     u'Atmosphere': [u'9.0', u'3.0', u'7.0', u'10.0'],
                     u'Service': [u'9.0', u'3.0', u'8.0', u'10.0'],
                     u'General': [u'9.0', u'3.0', u'7.7', u'10.0'],
                     u'text': [u'Vootreffelijk 5 gangen menu met goede bijpassende wijnen. Lichte keuken en alles heerlijk op smaak. Goede ontvangst en virendelijke attente bediening en sympathieke sfeer met een prachtig uitzicht.',
                               u'ondanks een zeer duidelijke melding in de reservering : mijn vrouw loopt met een rollator en we nemen zonder tegenbericht 2 Jack Russells mee - werd ons de toegang geweigerd. ja, het was wel bekend, maar ze hadden "vergeten" ons te melden dat honden niet welkom zijn. of we die dan maar ergens anders konden onderbrengen. geen excuus mogelijk, we konden ophoepelen. en dat moet een top zaak voorstellen? ronduit waardeloos en belachelijk. daar rijdt je dan een heel eind voor en verheug je je op. slechte bedrijfsleiding ? dat lijkt er toch wel erg op.',
                               u'Wij waren door fileleed wat later als aangegeven, maar de bediening ving dit heel professioneel op. Gezien de temperatuur was het diner binnen,maar dat gaf geen domper op de sfeer. Het eten was soms een herkenning maar ook wel een gokje, maar de bediening gaf uitleg wat er op het bord lag, zodat alles nog goed tot zijn recht kwam. Eten en wijn combinatie was goed in evenwicht, maar ikzelf had graag de spaanse rode wijn ingeruild voor een andere. Al met al een fijne avond.',
                               u'gewoon geweldig, prachtig uitzicht en zeer vriendelijk personeel. eten was heerlijk. We hebben een leuke dag gehad'],
                     u'date': [u'P. van den Booren, 01 May 2013, 10:10',
                               u'Jan Hollestelle, 29 Apr 2013, 07:35',
                               u'Bob de Jong, 27 Apr 2013, 19:00',
                               u'ad van de louw, 22 Apr 2013, 12:59']}
    }),

    ('9', 'http://www.couverts.nl/restaurant/domburg/strand-90', {
        # seed trained from 8.html
        'seed': '8.json',
        'data': {'text': 'Wir haben Sylvester dort verbracht und',
                 'date': '06-01-2014'},
        'assert_in': {
            'text': 'Het was heel lekker. Prachtige locatie.'
        }
    })
]

def _normalize_text(text):
    return re.sub(ur'\s+', u' ', text).replace(u'\u00a0', u' ').strip()

def _merge_list_of_dict(items):
    if not items:
        return {}
    d = {}
    for item in items:
        for k, v in item.iteritems():
            d.setdefault(k, []).append(_normalize_text(v[0]))
    return d

class DeptaTest(unittest.TestCase):

    def _get_html(self, fn):
        path = os.path.join(os.path.dirname(__file__), 'resources', fn + '.html')
        return open(path, 'rb').read().decode('utf-8')

    def _get_seed(self, fn):
        path = os.path.join(os.path.dirname(__file__), 'resources', fn)
        with open(path) as f:
            return json.load(f)

    def _get_texts(self, fn, sep='\t'):
        path = os.path.join(os.path.dirname(__file__), 'resources', fn + '.txt')
        lines = codecs.open(path, 'r', 'utf8').readlines()
        texts = []
        for line in lines:
            rows = [_normalize_text(text) for text in line.split(sep)]
            texts.append(rows)
        return texts

    def _normalize_region_text(self, region):
        texts = []
        for row in region.as_plain_texts():
            texts.append([_normalize_text(text) for text in row])
        return texts

    def test_extract(self):
        d = Depta()
        for fn, url, case in CASES:
            body = self._get_html(fn)
            texts = self._get_texts(fn)
            regions = d.extract(body)

            for k, v in case.iteritems():
                if 'test-index' in case:
                    self.assertEquals(self._normalize_region_text(regions[case.get('test-index')]), texts)
                if k == 'start-element':
                    start_elements = [(element_repr(region.parent[region.start]), region.start, region.k, \
                                       region.covered) for region in regions]
                    self.assertTrue(v in start_elements, '%s not found in testcase %s' %(v, fn))

    def test_infer(self):
        for fn, url, case in INFER_CASES:

            d = Depta()
            body = self._get_html(fn)
            seed = dict_to_region(self._get_seed(case.get('seed')))
            d.train(seed, case['data'])
            r = _merge_list_of_dict(d.infer(html=body))

            if 'expected' in case:
                self.assertDictEqual(case['expected'], r)

            if 'assert_in' in case:
                for k, v in case['assert_in'].iteritems():
                    self.assertIn(v, r[k])