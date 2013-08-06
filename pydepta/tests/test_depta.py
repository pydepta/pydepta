#coding=utf-8
import re
import unittest
import os
from lxml.html import document_fromstring
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
        'records': [u'Service 8.0 Atmosphere 6.0 Cuisine 8.0 7.3 Wij hebben een heerlijke avond gehad. En het eten was heel erg lekker. Dus bijzonder genoten. Alleen de drankjes waren vonden wij veel te duur. Bij binnenkomst werd ons gevraagd of we een aperitiefje van het huis wilde.Ja dat wilde wij wel. Het is maar hoe je het bekijkt. Van het huis of toch betalen. Het koste ons 34 euro. 7 glazen wijn 45,75 euro. We waren alles bij elkaar 86.50 kwijt aan drank en water. Ik vind dit eigenlijk wel een domper op deze leuke avond. Je denkt lekker uit eten te gaan, maar dan krijg je rekening en is de drank de helft meer dan je 4 gangen dinee. georgina de winter, 13 Mar 2013, 12:30',
                    u'Service 7.0 Atmosphere 7.0 Cuisine 8.0 7.3 Het dnig wat jammer was dat ik niet wist dat je van te voren aan moest geven of je een vis of vlees menu wilde. Wat ook jammer was dat je als laatste koffie bestelde dat men niet vroeg of je alleen koffie wilde of koffie compleet. Je kreeg gewoon compleet (zonder te vragen) maar daar moest je dan ook gelijk bijna 7 euro voor betalen. Terwijl je alleen koffie besteld had. Men had dit eerst moeten aangeven!! 12 Mar 2013, 20:41']
        }),

    ('3.html', 'http://www.iens.nl/restaurant/12229/nijmegen-pasta-e-fagioli', {
        'regions': [('<hr #greyBreak .>', 8, 4, 20)],
        'records': [u"20 juni 2013 8 Eten 8 Service 8 Decor Een echte Italiaanse restaurant, waar heerlijke gerechten, bereid met verse ingrediënten. Ik miste traditionele een minestrone, maar tortellini met truffels gecreëerd een perfecte voorgerecht. Pasta e fagioli pasta biedt een zeer goede selectie scherpgeprijsde wijnen. Wij hebben bijna drie uur doorgebracht, genietend van leuke sfeer, Italiaanse muziek en een uitstekende service. Zal terug! Gegeten op: 1 mei 2013. 2 van de 2 proevers vinden dit nuttig. Nuttig Meld de redactie benny21 Expertproever"]
        }),

    ('4.html', 'http://www.yp.com.hk/Dining-Entertainment-Shopping-Travel-b/Entertainment-Production-Services/CD-VCD-DVD-Manufacturers/p1/en/', {
        'regions': [('<div #listing_div .>', 0, 1, 13)],
        'records': [u'Smartlink Group (Hong Kong) Ltd 2688 0686 \u2502 1/F., Far East Factory Building, 334-336 Kwun Tong Road, Kwun Tong www.smartlinkgroup.hk Business Hours Share Update CD, VCD, DVD Accessories Email helen@smartlinkgroup.hk * Mandatory Smartlink Group (Hong Kong) Ltd Send To : helen@smartlinkgroup.hk Your Name * \uff1a Your Email \uff1a Message * \uff1a Share By Email * Mandatory Smartlink Group (Hong Kong) Ltd Smartlink Group (Hong Kong) Ltd Tel\uff1a2688 0686 1/F., Far East Factory Building, 334-336 Kwun Tong Road, Kwun Tong www.smartlinkgroup.hk helen@smartlinkgroup.hk Email * \uff1a Your Name * \uff1a More Related Search\uff1a CD, VCD, DVD Manufacturers CD Blu-Ray \u5149\u789f\u8907\u88fd \u5149\u789f\u88fd\u4f5c VCD \u71d2\u789f DVD \u5149\u789f']
        }),
    ]

def normalize_text(text):
    return re.sub(r'\s+', ' ', text.replace(u'\u00a0', ' '))

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
                        self.assertTrue(v in start_elements, '%s region failed' %fn)
                if k == 'records':
                    texts = []
                    for items in region_items:
                        for item in items:
                            root = document_fromstring(item)
                            text = u" ".join([text.strip() for text in root.xpath('//text()') if text.strip()])
                            texts.append(normalize_text(text))
                    for v in vs:
                        self.assertTrue(v in texts, '%s record failed' %fn)

if __name__ == '__main__':
    unittest.main()

