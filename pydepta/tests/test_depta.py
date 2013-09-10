# -*- coding: utf8 -*-
from __future__ import absolute_import
import unittest
import os
import re
from ..depta import Depta
from ..mdr import element_repr

CASES = [
    ('1', 'http://www.iens.nl/restaurant/10545/enschede-rhodos', {
        #'anchor_after_gn': ['/restaurant/10545/enschede-rhodos/recensie#6']
        'region-index': 5
        }),

    ('2', 'http://www.diningcity.com/en/zeeland/restaurant_oesterbeurs', {
        'regions': [('<div #review_content .>', 3, 1, 4)],
        'anchor_after_gn': ['/en/zeeland/restaurant_oesterbeurs/createreview',
                            '/en/zeeland/restaurant_oesterbeurs/reviews'],
        'region-index': 9
        }),

    ('3', 'http://www.iens.nl/restaurant/12229/nijmegen-pasta-e-fagioli', {
        'regions': [('<hr #greyBreak .>', 8, 4, 20)],
        'region-index': 5,
        'anchor_after_gn': ['/restaurant/12229/nijmegen-pasta-e-fagioli/recensie#6']
        }),
    #
    ('4', 'http://www.yp.com.hk/Dining-Entertainment-Shopping-Travel-b/Entertainment-Production-Services/CD-VCD-DVD-Manufacturers/p1/en/', {
        'regions': [('<div #listing_div .>', 0, 1, 13)],
        }),

    ('5', 'http://www.eet.nu/enschede/rhodos', {
        'regions': [('<li #feedback has-ratings has-scores .review_604121>', 0, 3, 21)],
        }),
    ]

INFER_CASES = [
    ('2_infer', 'http://www.diningcity.com/en/zeeland/restaurant_hetbadpaviljoen', {
        'seed': '2',
        'regions': [('<div #review_content .>', 3, 1, 4)],
        'region-index': 10
    }),

]
def normalize_text(text):
    return re.sub(r'\s+', ' ', text.decode('utf8' ,'ignore').replace(u'\u00a0', ' ')).strip()

class DeptaTest(unittest.TestCase):

    def _get_html(self, fn):
        path = os.path.join(os.path.dirname(__file__), 'resources', fn + '.html')
        return open(path, 'rb').read().decode('utf-8')

    def _get_texts(self, fn):
        path = os.path.join(os.path.dirname(__file__), 'resources', fn + '.txt')
        lines = open(path, 'r').readlines()
        texts = []
        for line in lines:
            rows = [normalize_text(text) for text in line.split('\t')]
            texts.append(rows)
        return texts

    def _normalize_region_text(self, region):
        texts = []
        for row in region.as_plain_texts():
            texts.append([normalize_text(text) for text in row])
        return texts

    def test_depta(self):
        depta = Depta()
        for fn, url, case in CASES:
            body = self._get_html(fn)
            texts = self._get_texts(fn)
            regions = depta.extract(body)

            for k, vs in case.iteritems():
                if 'region-index' in case:
                    region_index = case['region-index']
                    self.assertEquals(self._normalize_region_text(regions[region_index]), texts)

                if k == 'regions':
                    start_elements = [(element_repr(region.parent[region.start]), region.start, region.k, region.covered) for region in regions]
                    for v in vs:
                        self.assertTrue(v in start_elements, '%s region failed' %fn)
                if k == 'anchor_after_gn':
                    anchors = []
                    for region in regions:
                        anchors.extend(anchor.get('href') for anchor in region.get_elements_after_generalized_node('a'))
                    for v in vs:
                        self.assertTrue(v in anchors, '%s not sees in %s.' %(v, fn))
