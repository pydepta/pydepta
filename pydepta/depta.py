from urllib import urlopen
from scrapely import HtmlPage, Scraper
from lxml.html import tostring

from w3lib.encoding import html_to_unicode

from .htmls import DomTreeBuilder
from .mdr import MiningDataRegion, MiningDataRecord, MiningDataField


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

    def infer(self, seed, data, html='', **kwargs):
        """
        extract data with seed region and the data you expect to scrape from there.
        """
        if 'url' in kwargs:
            info = urlopen(kwargs.pop('url'))
            _, html = html_to_unicode(info.headers.get('content_type'), info.read())

        builder = DomTreeBuilder(html)
        doc = builder.build()
        page = HtmlPage(body=tostring(doc, encoding=unicode, method='html'))

        scraper = Scraper()
        scraper.train_from_htmlpage(self._region_to_htmlpage(seed), data)
        return scraper.scrape_page(page)

    def _region_to_htmlpage(self, region):
        seed_body = tostring(region.parent[region.start], encoding=unicode, method='html')
        return HtmlPage(body=seed_body)