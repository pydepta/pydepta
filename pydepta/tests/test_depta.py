import unittest
import os
from pydepta.depta import Depta
from pydepta.mdr import element_repr

CASES = [
    # TODO: allow non-adjacent generalized nodes
    # ('1.html', 'http://www.iens.nl/restaurant/10545/enschede-rhodos', {
    #     'regions': [],
    #     }),
    #
    ('2.html', 'http://www.diningcity.com/en/zeeland/restaurant_oesterbeurs', {
        'regions': [('<div #review_content .>', 3, 1, 4)],
        }),

    ('3.html', 'http://www.iens.nl/restaurant/12229/nijmegen-pasta-e-fagioli', {
        'regions': [('<hr #greyBreak .>', 8, 4, 20)],
        }),

    ('4.html', 'http://www.yp.com.hk/Dining-Entertainment-Shopping-Travel-b/Entertainment-Production-Services/CD-VCD-DVD-Manufacturers/p1/en/', {
        'regions': [('<div #listing_div .>', 0, 1, 13)],
        }),
    ]

class DeptaTest(unittest.TestCase):
    def _get_html(self, fn):
        path = os.path.join(os.path.dirname(__file__), 'htmlpages', fn)
        return open(path, 'rb').read().decode('utf-8')

    def test_depta(self):
        depta = Depta()
        for fn, url, case in CASES:
            body = self._get_html(fn)
            regions, region_items = depta.extract(body)
            for k, vs in case.iteritems():
                if k == 'regions':
                    start_elements = [(element_repr(region.parent[region.start]), region.start, region.k, region.covered) for region in regions]
                    for v in vs:
                        self.assertTrue(v in start_elements, '%s failed' %fn)

if __name__ == '__main__':
    unittest.main()

