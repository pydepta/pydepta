from urllib2 import urlopen
from w3lib.encoding import html_to_unicode

from pydepta.htmls import DomTreeBuilder
from pydepta.mdr import MiningDataRegion, MiningDataRecord, MiningDataField

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

        for region in regions:
            records = record_finder.find_records(region)
            items, _ = field_finder.align_records(records)
            region.items = items
            if 'verbose' in kwargs:
                print region
                for record in records:
                    print '\t', record

        return regions