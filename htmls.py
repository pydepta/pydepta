#coding=utf-8
from urllib2 import urlopen
from lxml import etree
from lxml.html import tostring
from mdr import MiningDataRegion
from pyquery import PyQuery as pq

class DomTreeBuilder(object):
    def __init__(self, html, **options):
        self.html = html
        self.options = options

    def build(self):
        parser = etree.HTMLParser()
        return etree.fromstring(self.html, parser)

def pyquery_highlight(element):
    p = pq(element)
    p.wrap("<div class='MDR' style='color:#ffff42; border:solid 5px'></div>")

def annotate(element, region_elements, highlight=pyquery_highlight):

    if element in region_elements:
        highlight(element)

    for child in element:
        annotate(child, region_elements)

def main(url=None, html=None):
    if not html:
        html = urlopen(url).read()
    builder = DomTreeBuilder(html, debug=False)
    root = builder.build()
    mdr = MiningDataRegion(root, threshold=0.8, debug=False)
    regions = mdr.find_regions(root)
    region_elements = set()

    for i, region in enumerate(regions):
        print 'region {}: {}, {} {}, {}, {}'.format(i, region.root.tag, region.root[region.start].tag, region.start, region.k, region.covered)
        for j in xrange(region.start, region.start + region.covered):
            region_elements.add(region.root[j])

    annotate(root, region_elements)

    with open('output.html', 'w') as f:
        print >> f, tostring(root, pretty_print=True)

    print 'write to output.html.'

if __name__ == '__main__':
    html = open('1.html').read()
    main(html=html)