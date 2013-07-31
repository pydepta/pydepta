"""
DEPTA main driver
"""
from random import choice
from urllib2 import urlopen

from lxml.html import tostring
from w3lib.encoding import html_to_unicode

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
    def __init__(self, threshold=0.75, k=5):
        self.threshold = threshold
        self.k = k

    def extract(self, html='', **kwargs):
        """
        extract data field from raw html or from a url.

        return a list of data field.
        """
        if 'url' in kwargs:
            info = urlopen(kwargs.pop('url'))
            _, html = html_to_unicode(info.headers.get('content_type'), info.read())
        builder = DomTreeBuilder(html)
        root = builder.build()

        region_finder = MiningDataRegion(root, self.k, self.threshold)
        regions = region_finder.find_regions(root)

        record_finder = MiningDataRecord(self.threshold)
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
            colors = ['#ffff42', '#ff0000', '#00ff00', '#ff00ff']
            for i, region in enumerate(regions):
                color = choice(colors)
                for j, record in enumerate(region_records.get(region)):
                    self.annotate(i, j, record.elements, color)

            with open(kwargs.pop('annotate'), 'w') as f:
                print >> f, tostring(root, pretty_print=True)

        return regions, region_items

    def annotate(self, region, record, elements, color):
        """
        annotate the HTML elements with PyQuery.
        """
        from pyquery import PyQuery as pq
        p = pq(elements[0])
        div = p.wrap('<div class="mdr_region" region_id={} record_id={} style="border:solid 1px {}"></div>'.format(region, record, color))
        for e in elements[1:]:
            div.append(e)

if __name__ == '__main__':
    import sys
    from lxml.html import document_fromstring
    info = urlopen(sys.argv[1])
    _, html = html_to_unicode(info.headers.get('content_type'), info.read())
    depta = Depta()

    regions, region_items = depta.extract(html, annotate='output.html')
    from lxml.html import document_fromstring
    for i, items in enumerate(region_items):
        print '====================== region {} ====================== '.format(i)
        for j, item in enumerate(items):
            print '------------- record {} ------------------'.format(j)
            for field in item.fields:
                if field.html:
                    root = document_fromstring(field.html)
                    texts = [text.strip() for text in root.xpath('//text()') if text.strip()]
                    print " | ".join(texts)
            print
