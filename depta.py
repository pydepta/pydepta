"""
DEPTA main driver
"""
from random import choice
from urllib2 import urlopen

from lxml.html import tostring
from w3lib import encoding
from pyquery import PyQuery as pq

from htmls import DomTreeBuilder
from mdr import MiningDataRegion, MiningDataRecord, MiningDataField

class Item(object):
    def __init__(self, fields):
        self.fields = fields

    def __len__(self):
        return len(self.fields)

    def __getitem__(self, item):
        return self.fields[item]

    def __iter__(self):
        return iter(self.fields)

class Field(object):
    def __init__(self, text, html):
        self.text = text.strip()
        self.html = html

class Depta(object):
    def __init__(self, threshold=0.6, k=3):
        self.threshold = threshold
        self.k = k

    def extract(self, html='', **kwargs):
        """
        extract data regions from raw html or from a url.
        """
        if 'url' in kwargs:
            info = urlopen(kwargs.pop('url'))
            _, html = encoding.html_to_unicode(info.headers.get('content_type'), info.read())
        builder = DomTreeBuilder(html)
        root = builder.build()

        mining_region = MiningDataRegion(root, self.k, self.threshold)
        regions = mining_region.find_regions(root)

        mining_record = MiningDataRecord()
        mining_field = MiningDataField()

        region_records = {}
        all_items = []
        for i, region in enumerate(regions):
            records = mining_record.find_records(region)
            items, _ = mining_field.align_records(records)
            all_items.extend(items)
            assert len(items) == len(records)
            region_records.update({region: records})

            if 'verbose' in kwargs:
                print region
                for record in records:
                    print '\t', record

        # always annotate at last to avoid modify the DOM tree
        if 'annotate' in kwargs:
            for i, region in enumerate(regions):
                for j, record in enumerate(region_records.get(region)):
                    self.annotate(i, j, record.elements)

            with open(kwargs.pop('annotate'), 'w') as f:
                print >> f, tostring(root, pretty_print=True)

        return all_items

    def annotate(self, region, record, elements):
        """
        annotate the HTML elements with PyQuery.
        """
        colors = ['#ffff42', '#ff0000', '#00ff00', '#ff00ff']
        p = pq(elements[0])
        div = p.wrap('<div class="mdr_region" region_id={} record_id={} style="color:{}; border:solid 5px"></div>'.format(region, record, choice(colors)))
        for e in elements[1:]:
            div.append(e)

if __name__ == '__main__':
    import sys
    info = urlopen(sys.argv[1])
    _, html = encoding.html_to_unicode(info.headers.get('content_type'), info.read())
    depta = Depta()

    items = depta.extract(html, annotate='output.html', verbose=True)
    for i, item in enumerate(items):
        print i, ' | '.join(map(lambda x: x.text, item.fields))