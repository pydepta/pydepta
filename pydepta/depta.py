from urllib import urlopen
from lxml.html import document_fromstring

from w3lib.encoding import html_to_unicode

from pydepta.htmls import DomTreeBuilder
from pydepta.mdr import MiningDataRegion, MiningDataRecord, MiningDataField, Record
from pydepta.trees import SimpleTreeMatch


class Depta(object):

    def __init__(self, threshold=0.75, k=5):
        self.threshold = threshold
        self.k = k

    def extract(self, html='', **kwargs):
        """
        extract data field from raw html or from a url.
        """
        if not html and 'url' in kwargs:
            info = urlopen(kwargs.pop('url'))
            _, html = html_to_unicode(info.headers.get('content_type'), info.read())
        builder = DomTreeBuilder(html)
        root = builder.build()

        region_finder = MiningDataRegion(root, self.k, self.threshold)
        regions = region_finder.find_regions(root)

        record_finder = MiningDataRecord(self.threshold)
        field_finder = MiningDataField()

        for region in regions:
            records = record_finder.find_records(region)
            items, _ = field_finder.align_records(records)
            region.items = items
            if 'verbose' in kwargs:
                print region
                for record in records:
                    print '\t', record

        return regions

    def infer(self, region, html='', **kwargs):
        """
        extract the page has single record interested from with given region.
        """
        if 'url' in kwargs:
            info = urlopen(kwargs.pop('url'))
            _, html = html_to_unicode(info.headers.get('content_type'), info.read())
        document = document_fromstring(html)
        xpath = self._get_anchor_xpath(region)
        anchors = document.xpath(xpath)

        if len(anchors) > 0:
            l1 = [region.parent[region.start+i] for i in range(region.k)]
            l2 = self._populate_siblings(anchors[0], region.k)

            seed = Record(*l1)
            record = Record(*l2)

            stm = SimpleTreeMatch()
            sim =  stm.normalized_match_score(l1, l2)

            if sim > self.threshold:
                field_finder = MiningDataField()
                items, _ = field_finder.align_records([record], seed=seed)
                return items

        return []

    def _get_anchor_xpath(self, region):
        start = region.start
        anchor = region.parent[start]
        if anchor.get('class', ''):
            return '//{}[@class="{}"]'.format(anchor.tag, anchor.get('class', ''))
        else:
            return '//{}[{}]'.format(anchor.getparent().tag, start)

    def _populate_siblings(self, anchor, size):
        r = [anchor]
        for _ in range(size-1):
            r.append(anchor.itersiblings())
        return r