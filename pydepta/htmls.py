from lxml import etree
from lxml.html.clean import Cleaner


class DomTreeBuilder(object):
    def __init__(self, html):
        cleaner = Cleaner(style=True, page_structure=False)
        self.html = cleaner.clean_html(html)

    def build(self):
        parser = etree.HTMLParser(encoding='utf-8')
        return etree.fromstring(self.html, parser)