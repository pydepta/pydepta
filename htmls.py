#coding=utf-8
from urllib2 import urlopen
from lxml import etree
from mdr import MiningDataRegion
from pyquery import PyQuery as pq

class DomTreeBuilder(object):
    def __init__(self, html, **options):
        self.html = html
        self.options = options

    def build(self):
        parser = etree.HTMLParser()
        return etree.fromstring(self.html, parser)

def main(url=None, html=None):
    if not html:
        html = urlopen(url).read()
    builder = DomTreeBuilder(html, debug=False)
    root = builder.build()
    mdr = MiningDataRegion(root, threshold=0.8, debug=False)
    regions = mdr.find_regions(root)
    print '{} regions founds.'.format(len(regions))
    for region in regions:
        print '------------------------------------------------------------'
        print 'region: {}, {}, {}, {}'.format(region.root.tag, region.start + 1, region.k, region.covered)
        # for i in range(region.covered):
        #     print pq(region.element[region.start+i]).text()

if __name__ == '__main__':
    html = open('1.html').read()
    main(html=html)