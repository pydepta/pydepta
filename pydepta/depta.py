from urllib import urlopen
from scrapely import HtmlPage, Scraper, TemplateMaker, best_match, InstanceBasedLearningExtractor
from lxml.html import tostring
from scrapely.extraction.regionextract import *
from scrapely.extraction.similarity import first_longest_subsequence
from w3lib.encoding import html_to_unicode

from .htmls import DomTreeBuilder
from .mdr import MiningDataRegion, MiningDataRecord, MiningDataField

class DeptaExtractor(RecordExtractor):
    """
    A simple RecordExtractor variant to handle the tabulated data.
    """
    def __init__(self, extractors, template_tokens):
        super(DeptaExtractor, self).__init__(extractors, template_tokens)
        self.best_match = first_longest_subsequence

    def extract(self, page, start_index=0, end_index=None, ignored_regions=None, **kwargs):
        if ignored_regions is None:
            ignored_regions = []
        region_elements = sorted(self.extractors + ignored_regions, key=lambda x: _labelled(x).start_index)
        pindex, sindex, attributes = self._doextract(page, region_elements, start_index,
                                           end_index, **kwargs)

        if not end_index:
            end_index = len(page.page_tokens)

        # collect variant data, maintaining the order of variants
        r = []
        items = [(k, v) for k, v in attributes]

        # if the number of extracted data match
        if len(items) == len(region_elements):
            r.append(_attrs2dict(items))

            # if there are remaining items, extract recursively backward
            if sindex and sindex < end_index:
                r.extend(self.extract(page, 0, pindex - 1, ignored_regions, **kwargs))
        return r

    def __repr__(self):
        return str(self)

class DeptaIBLExtractor(InstanceBasedLearningExtractor):

    def build_extraction_tree(self, template, type_descriptor, trace=True):
        """Build a tree of region extractors corresponding to the
        template
        """
        attribute_map = type_descriptor.attribute_map if type_descriptor else None
        extractors = BasicTypeExtractor.create(template.annotations, attribute_map)
        if trace:
            extractors = TraceExtractor.apply(template, extractors)
        for cls in (DeptaExtractor,):
            extractors = cls.apply(template, extractors)
            if trace:
                extractors = TraceExtractor.apply(template, extractors)

        return TemplatePageExtractor(template, extractors)

    def extract(self, html, pref_template_id=None):
        extracted, template = super(DeptaIBLExtractor, self).extract(html, pref_template_id)
        if extracted:
            return extracted[::-1], template
        return None, None

class Depta(object):
    def __init__(self, threshold=0.75, k=5):
        self.threshold = threshold
        self.k = k
        self.scraper = Scraper()

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

    def train(self, seed, data):
        """
        train scrapely from give seed region and data.
        """
        assert data, "Cannot train with empty data"
        htmlpage = self._region_to_htmlpage(seed)
        tm = TemplateMaker(htmlpage)
        if isinstance(data, dict):
            data = data.items()

        for field, values in data:
            if not hasattr(values, '__iter__'):
                values = [values]
            for value in values:
                if isinstance(value, str):
                    value = value.decode(htmlpage.encoding or 'utf-8')
                tm.annotate(field, best_match(value), best_match=False)
        self.scraper.add_template(tm.get_template())


    def infer(self, html='', **kwargs):
        """
        extract data with seed region and the data you expect to scrape from there.
        """
        if 'url' in kwargs:
            info = urlopen(kwargs.pop('url'))
            _, html = html_to_unicode(info.headers.get('content_type'), info.read())

        builder = DomTreeBuilder(html)
        doc = builder.build()
        page = HtmlPage(body=tostring(doc, encoding=unicode, method='html'))

        return self._scrape_page(page)

    def _scrape_page(self, page):
        if self.scraper._ex is None:
            self.scraper._ex = DeptaIBLExtractor((t, None) for t in
                self.scraper._templates)
        return self.scraper._ex.extract(page)[0]

    def _region_to_htmlpage(self, region):
        seed_body = tostring(region.parent[region.start], encoding=unicode, method='html')
        return HtmlPage(body=seed_body)