from random import choice
from urllib2 import urlopen
import sys

from lxml import etree
from lxml.html import tostring
from lxml.html.clean import Cleaner
from w3lib import encoding
from pyquery import PyQuery as pq

from mdr import MiningDataRegion, MiningDataRecord, MiningDataField


class DomTreeBuilder(object):
    def __init__(self, html, **options):
        cleaner = Cleaner(style=True, page_structure=False)
        self.html = cleaner.clean_html(html)
        self.options = options

    def build(self):
        parser = etree.HTMLParser(encoding='utf-8')
        return etree.fromstring(self.html, parser)

def annotate(id, elements):
    """
    annotate the HTML elements with PyQuery.
    """
    colors = ['#ffff42', '#ff0000', '#00ff00', '#ff00ff']
    p = pq(elements[0])
    div = p.wrap('<div class="mdr_region" id={} style="color:{}; border:solid 5px"></div>'.format(id, choice(colors)))
    for e in elements[1:]:
        div.append(e)

def main(html=None):
    builder = DomTreeBuilder(html, debug=False)
    root = builder.build()

    with open('verbose.html', 'w') as f:
        print >>f, tostring(root, pretty_print=True)

    region_m = MiningDataRegion(root, threshold=0.8, debug=False)
    regions = region_m.find_regions(root)

    for i, region in enumerate(regions):
        print 'region {}: {}[{}], {}, {}, {}'.format(i, region.parent.tag, region.start,
                                                     region.parent[region.start].tag, region.k, region.covered)

    record_m = MiningDataRecord()
    records_list = []

    for region in regions:
        records_list.append(record_m.find_records(region))

    mdf = MiningDataField()

    for i, records in enumerate(records_list):
        print '----------------------------------------------------------------'
        print 'records #{} length: {} elements/record: {} elements: {}'.format(i, len(records), len(records[0]), records[0])
        _, fields = mdf.align_records(*records)
        for field in fields:
            print len(field), "|".join(text for text in field)

    # always annotate at last to avoid modify the DOM tree
    for i, records in enumerate(records_list):
        for record in records:
            annotate(i, record)

    with open('output.html', 'w') as f:
        print >> f, tostring(root, pretty_print=True)

if __name__ == '__main__':
    if len(sys.argv) > 1:
        info = urlopen(sys.argv[1])
        _, html = encoding.html_to_unicode(info.headers.get('content_type'), info.read())
    else:
        html = open('1.html').read()
    main(html=html)