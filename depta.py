"""
DEPTA main driver
"""
from random import choice
from urllib2 import urlopen
from lxml.html import tostring
import sys
from w3lib import encoding
from htmls import DomTreeBuilder
from mdr import MiningDataRegion, MiningDataRecord, MiningDataField
from pyquery import PyQuery as pq

class Depta(object):
    def __init__(self, threshold=0.8, k=3, **options):
        self.threshold = threshold
        self.k = k
        self.options = options

    def extract(self, html):
        builder = DomTreeBuilder(html)
        root = builder.build()

        region_m = MiningDataRegion(root, self.k, self.threshold, debug=False)
        regions = region_m.find_regions(root)

        if self.options.get('debug'):
            for i, region in enumerate(regions):
                print 'region {}: {}[{}], {}, {}, {}'.format(i, region.parent.tag, region.start,
                                                             region.parent[region.start].tag, region.k, region.covered)

        record_m = MiningDataRecord()
        records_list = []

        for region in regions:
            records_list.append(record_m.find_records(region))

        mdf = MiningDataField()

        record_fields = []
        for i, records in enumerate(records_list):
            _, fields = mdf.align_records(*records)
            record_fields.append(fields)

        # always annotate at last to avoid modify the DOM tree
        for i, records in enumerate(records_list):
            for record in records:
                self.annotate(i, record)

        if self.options.get('debug'):
            with open('output.html', 'w') as f:
                print >> f, tostring(root, pretty_print=True)

        return record_fields

    def annotate(self, id, elements):
        """
        annotate the HTML elements with PyQuery.
        """
        colors = ['#ffff42', '#ff0000', '#00ff00', '#ff00ff']
        p = pq(elements[0])
        div = p.wrap('<div class="mdr_region" id={} style="color:{}; border:solid 5px"></div>'.format(id, choice(colors)))
        for e in elements[1:]:
            div.append(e)


if __name__ == '__main__':
    info = urlopen(sys.argv[1])
    _, html = encoding.html_to_unicode(info.headers.get('content_type'), info.read())
    depta = Depta(debug=True)

    record_fields = depta.extract(html)
    for fields in record_fields:
        print '----------------------------------------------------------------'
        for field in fields:
            print " ".join(field.texts)