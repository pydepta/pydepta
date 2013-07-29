"""
DEPTA main driver
"""
from random import choice
from urllib2 import urlopen

from lxml.html import tostring
from w3lib import encoding
from pyquery import PyQuery as pq

from pydepta.htmls import DomTreeBuilder
from pydepta.mdr import MiningDataRegion, MiningDataRecord, MiningDataField

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
        self.text = text
        self.html = html

class Depta(object):
    def __init__(self, threshold=0.7, k=3):
        self.threshold = threshold
        self.k = k

    def extract(self, html='', **kwargs):
        """
        extract data field from raw html or from a url.

        return a list of data field.
        """
        if 'url' in kwargs:
            info = urlopen(kwargs.pop('url'))
            _, html = encoding.html_to_unicode(info.headers.get('content_type'), info.read())
        builder = DomTreeBuilder(html)
        root = builder.build()

        region_finder = MiningDataRegion(root, self.k, self.threshold)
        regions = region_finder.find_regions(root)

        record_finder = MiningDataRecord()
        field_finder = MiningDataField()

        region_records = {}
        region_items = []
        for i, region in enumerate(regions):
            records = record_finder.find_records(region)
            items, _ = field_finder.align_records(records)
            region_items.append(items)
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

        return region_items

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
    from lxml.html import document_fromstring
    info = urlopen(sys.argv[1])
    _, html = encoding.html_to_unicode(info.headers.get('content_type'), info.read())
    depta = Depta()

    region_items = depta.extract(html, verbose=True)
    for i, items in enumerate(region_items):
        for item in items:
            for field in item.fields:
                root = document_fromstring(field.html)
                texts = [text.strip() for text in root.xpath('//text()') if text.strip()]
                print texts
        print