from copy import copy
from urllib import urlopen

from w3lib.encoding import html_to_unicode

from .htmls import DomTreeBuilder
from .mdr import MiningDataRegion, MiningDataRecord, MiningDataField, Record
from .trees import SimpleTreeMatch


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

    def infer(self, seed, html='', **kwargs):
        """
        extract the page has single record interested from with given region.
        """
        if 'url' in kwargs:
            info = urlopen(kwargs.pop('url'))
            _, html = html_to_unicode(info.headers.get('content_type'), info.read())

        stm = SimpleTreeMatch()
        field_finder = MiningDataField()

        builder = DomTreeBuilder(html)
        document = builder.build()

        xpath = self._get_anchor_xpath(seed)
        elements = document.xpath(xpath)
        regions = []

        if len(elements):
            items = []
            parent = elements[0].getparent()
            start = parent.index(elements[0])
            l1 = [seed_region.parent[seed_region.start+i] for i in range(seed_region.k)]
            seed = Record(*l1)
            region = copy(seed_region)
            region.parent = parent
            region.start = start

            while start < len(parent):
                l2 = self._populate_siblings(parent[start], seed_region.k)
                sim = stm.normalized_match_score(l1, l2)
                if sim > self.threshold:
                    record = Record(*l2)
                    aligned_item = field_finder.align_record(seed, record)
                    items.append(aligned_item)
                start += seed_region.k
            if items:
                region.items = items
                region.covered = len(items) * region.k
                regions.append(region)

        return regions

    def _get_anchor_xpath(self, region):
        start = region.start
        anchor = region.parent[start]
        if anchor.get('class', ''):
            return '//{}[@class="{}"]'.format(anchor.tag, anchor.get('class', ''))
        else:
            return '//{}[{}]'.format(anchor.getparent().tag, start)

    def _populate_siblings(self, anchor, size):
        r = [anchor]
        r.extend(list(anchor.itersiblings())[:size-1])
        return r
