#coding=utf-8
from collections import deque
from urllib2 import urlopen
from lxml import etree
from mdr import MiningDataRegion

class DomTreeBuilder(object):
    def __init__(self, html, **options):
        self.html = html
        self.options = options

    def build(self):
        parser = etree.HTMLParser()
        root = etree.fromstring(self.html, parser)
        dict = {}
        for i, element in enumerate(self._bfs(root)):
            if self.options.get('debug'):
                print i, element.tag
            dict.setdefault(element, i)
        return root, dict

    def _bfs(self, element):
        queue = deque([element])
        while queue:
            el = queue.popleft()
            queue.extend(el)
            yield el

def main(url=None, html=None):
    if not html:
        html = urlopen(url).read()
    builder = DomTreeBuilder(html, debug=False)
    root, ids = builder.build()
    mdr = MiningDataRegion(root, debug=True)
    regions = mdr.find_regions(root)
    print 'regions founds:'
    for region in regions:
        print 'region: {}, {}, {}, {}, {}'.format(ids.get(region.element),
                                                  region.element.tag, region.start+1, region.k, region.covered)

if __name__ == '__main__':
    html = open('1.html').read()
    main(html=html)