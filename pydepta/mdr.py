from __future__ import division
from collections import namedtuple, defaultdict, Counter
import copy
from cStringIO import StringIO
from lxml import etree
from lxml.html import tostring, fragment_fromstring
from .trees import SimpleTreeMatch, tree_depth, PartialTreeAligner, SimpleTreeAligner, tree_size

GeneralizedNode = namedtuple('GeneralizedNode', ['element', 'length'])
Field = namedtuple('Field', ['text', 'html'])

def element_repr(e):
    return '<%s #%s .%s>' %(e.tag, e.get('class', ''), e.get('id', ''))

def region_to_dict(region):
    return {
        'parent': tostring(region.parent, encoding=unicode, method='html'),
        'start': region.start,
        'k': region.k,
        'covered': region.covered,
        'items': region.items
    }

def dict_to_region(json_region):
    parser = etree.HTMLParser(encoding='unicode')
    parent = fragment_fromstring(json_region['parent'], parser=parser)
    return Region(parent=parent, start=json_region['start'], k=json_region['k'],
                  covered=json_region['covered'],
                  items=json_region['items'])

class Region(object):
    def __init__(self, **dict):
        self.__dict__.update(dict)

    def __str__(self):
        return "<Region: parent {}, start {}:{}, k {}, covered {}>".format(element_repr(self.parent),
                                                                                     self.start,
                                                                                     element_repr(self.parent[self.start]),
                                                                                     self.k,
                                                                                     self.covered)
    __repr__ = __str__

    def __getstate__(self):
        odict = self.__dict__.copy()
        odict['parent'] = tostring(odict['parent'], encoding=unicode, method='html')
        odict['start'] = odict['start']
        odict['k'] = odict['k']
        odict['covered'] = odict['covered']
        odict['items'] = odict['items']
        return odict

    def __setstate__(self, dict):
        parser = etree.HTMLParser(encoding='unicode')
        dict['parent'] = fragment_fromstring(dict['parent'], parser=parser)
        dict['start'] = dict['start']
        dict['k'] = dict['k']
        dict['covered'] = dict['covered']
        dict['items'] = dict['items']
        self.__dict__.update(dict)

    def iter(self, k):
        """
        >>> root = [1, 2, 3, 4, 5]
        >>> region = Region(parent=root, start=1, k=1, covered=4)
        >>> list(region.iter(1))
        [[2], [3], [4], [5]]

        >>> region = Region(parent=root, start=1, k=2, covered=4)
        >>> list(region.iter(2))
        [[2, 3], [4, 5]]

        >>> region = Region(parent=root, start=1, k=1, covered=4)
        >>> list(region.iter(2))
        [[2, 3], [4, 5]]

        """
        for i in xrange(self.start, self.start + self.covered, k):
            yield self.parent[i:i + k]

    def as_html_table(self, headers=None, show_id=False):
        """
        convert the region to a HTML table
        """
        f = StringIO()
        print >> f, '<table>'

        # print headers
        if headers:
            print >> f, '<tr>'
            if isinstance(headers, dict):
                if show_id:
                    print >> f, '<th></th>'
                for i in range(len(self.items[0])):
                    print >> f, '<th>%s</th>' %headers.get(i, '')
            elif isinstance(headers, list):
                if show_id:
                    print >> f, '<th></th>'
                for h in headers:
                    print >> f, '<th>%s</th>' %h
            print >> f, '</tr>'

        # print content
        for i, item in enumerate(self.items):
            print >> f, '<tr>'
            if show_id:
                print >> f, '<td>%s</td>' %(i+1)
            for field in item:
                print >> f, '<td>%s</td>' %field[0].encode('utf8', 'ignore')
            print >> f, '</tr>'
        print >> f, '</table>'

        return f.getvalue()

    def as_plain_texts(self):
        """
        convert the region to a two dim plain texts.
        """
        return [[field[0] for field in item] for item in self.items]

class Record(object):
    def __init__(self, *elements):
        self.elements = elements

    def __len__(self):
        return len(self.elements)

    def __str__(self):
        return 'DataRecord: %s' % ", ".join(element_repr(e) for e in self.elements)

    def __iter__(self):
        return iter(self.elements)

    def __getitem__(self, item):
        return self.elements[item]

    @staticmethod
    def size(record):
        s = 0
        for element in record.elements:
            s += tree_size(element)
        return s

def pairwise(a, K, start=0):
    """
    A generator to return the comparison pair.

    for example:
    >>> list(pairwise([1, 2, 3, 4], 1))
    [([1], [2]), ([2], [3]), ([3], [4])]
    >>> list(pairwise([1, 2, 3, 4], 2))
    [([1], [2]), ([2], [3]), ([3], [4]), ([2], [3]), ([3], [4]), ([1, 2], [3, 4])]
    >>> list(pairwise([1, 2, 3, 4, 5, 6, 7, 8, 9, 10], 2))
    [([1], [2]), ([2], [3]), ([3], [4]), ([4], [5]), ([5], [6]), ([6], [7]), ([7], [8]), ([8], [9]), ([9], [10]), ([2], [3]), ([3], [4]), ([4], [5]), ([5], [6]), ([6], [7]), ([7], [8]), ([8], [9]), ([9], [10]), ([1, 2], [3, 4]), ([3, 4], [5, 6]), ([5, 6], [7, 8]), ([7, 8], [9, 10]), ([2, 3], [4, 5]), ([4, 5], [6, 7]), ([6, 7], [8, 9])]
    >>> list(pairwise([1, 2, 3, 4, 5, 6, 7, 8, 9, 10], 3, 1))
    [([2], [3]), ([3], [4]), ([4], [5]), ([5], [6]), ([6], [7]), ([7], [8]), ([8], [9]), ([9], [10]), ([3], [4]), ([4], [5]), ([5], [6]), ([6], [7]), ([7], [8]), ([8], [9]), ([9], [10]), ([4], [5]), ([5], [6]), ([6], [7]), ([7], [8]), ([8], [9]), ([9], [10]), ([2, 3], [4, 5]), ([4, 5], [6, 7]), ([6, 7], [8, 9]), ([3, 4], [5, 6]), ([5, 6], [7, 8]), ([7, 8], [9, 10]), ([4, 5], [6, 7]), ([6, 7], [8, 9]), ([2, 3, 4], [5, 6, 7]), ([5, 6, 7], [8, 9, 10]), ([3, 4, 5], [6, 7, 8]), ([4, 5, 6], [7, 8, 9])]
    """
    for k in xrange(1, K + 1):
        for i in xrange(0, K):
            for j in xrange(start+i, len(a), k):
                slice_a = a[j:j + k]
                slice_b = a[j + k: j + 2 * k]

                if len(slice_a) >= k and len(slice_b) >= k:
                    yield slice_a, slice_b

class MiningDataRegion(object):
    def __init__(self, root, max_generalized_nodes, threshold):
        self.root = root
        self.max_generalized_nodes = max_generalized_nodes
        self.threshold = threshold
        self.stm = SimpleTreeMatch()

    def find_regions(self, root):
        data_regions = []
        if tree_depth(root) >= 2:
            scores = self.compare_generalized_nodes(root, self.max_generalized_nodes)
            data_regions.extend(self.identify_regions(0, root, self.max_generalized_nodes, self.threshold, scores))
            covered = set()
            for data_region in data_regions:
                for i in xrange(data_region.start, data_region.covered):
                    covered.add(data_region.parent[i])

            for child in root:
                if child not in covered:
                    data_regions.extend(self.find_regions(child))
        return data_regions


    def identify_regions(self, start, root, max_generalized_nodes, threshold, scores):
        cur_region = Region(parent=root, start=0, k=0, covered=0, score=0)
        max_region = Region(parent=root, start=0, k=0, covered=0, score=0)
        data_regions = []

        for k in xrange(1, max_generalized_nodes + 1):
            for i in xrange(0, max_generalized_nodes):
                flag = True
                for j in xrange(start + i, len(root) - k, k):
                    pair = GeneralizedNode(root[j], k), GeneralizedNode(root[j + k], k)
                    # Note Johannes: I was getting "Unorderable None >= float"
                    #   in python 2.x "None >= thresh" yields False, while
                    #   in python 3.x it's illegal
                    #   https://stackoverflow.com/questions/7383782/
                    #   technically in py2 "None" evaluates to something less
                    #       than 0
                    score = scores.get(pair, 0)
                    if score >= threshold:
                        if flag:
                            cur_region.k = k
                            cur_region.start = j
                            cur_region.score = score
                            cur_region.covered = 2 * k
                            flag = False
                        else:
                            cur_region.covered += k
                            cur_region.score += score
                    elif not flag:  # doesn't match but previous match
                        break

                if self.calculate_score(cur_region) > self.calculate_score(max_region):
                    max_region.k = cur_region.k
                    max_region.start = cur_region.start
                    max_region.covered = cur_region.covered
                    max_region.score = cur_region.score

        if max_region.covered:
            data_regions.append(max_region)
            if max_region.start + max_region.covered < len(max_region.parent):
                data_regions.extend(self.identify_regions(max_region.start + max_region.covered, root,
                                                          max_generalized_nodes, threshold, scores))

        return data_regions


    def compare_generalized_nodes(self, parent, k):
        """
         compare the adjacent children generalized nodes similarity of a given element

         Arguments:
         `parent`: the lxml element to compare children of.
         `k`: the maximum length of generalized node.
        """
        scores = {}
        for a, b in pairwise(parent, k):
            gn1 = GeneralizedNode(a[0], len(a))
            gn2 = GeneralizedNode(b[0], len(b))
            if (gn1, gn2) not in scores:
                score = self.stm.normalized_match_score(a, b)
                scores.setdefault((gn1, gn2), score)
        return scores

    def calculate_score(self, region):
        if region.covered == 0:
            return 0
        count = region.covered / region.k
        return region.score / count

class MiningDataRecord(object):
    """
    mining the data record from a region.

    basic assumption:
    the subtree of data records also similar. so if not any adjacent pair of them are
    similar (less than threshold), data region itself is a data record,
    otherwise children are individual data record.
    """

    def __init__(self, threshold):
        self.stm = SimpleTreeMatch()
        self.threshold = threshold

    def find_records(self, region):
        if region.k == 1:
            records = []
            # if all the individual node of children node of Generalized node are similar
            for i in xrange(region.start, region.start + region.covered):
                for child1, child2 in pairwise(region.parent[i], 1, 0):
                    sim = self.stm.normalized_match_score(child1, child2)
                    if sim < self.threshold:
                        return self.slice_region(region)
            else:
                # each child of generalized node is a data record
                for gn in region.iter(1):
                    records.extend([Record(c) for c in gn])
            return records
        else:
            # if almost all the individual node in Generalized Node are similar
            children = [region.parent[region.start + i] for i in range(region.covered)]
            sizes = Counter([tree_size(child) for child in children])
            most_common_size, _= sizes.most_common(1)[0]
            most_typical_child = [child for child in children if tree_size(child) == most_common_size][0]
            similarities = dict([child, self.stm.normalized_match_score([most_typical_child], [child])] for child in children)
            if self.almost_similar(similarities.values(), self.threshold):
                return [Record(child) for child in children if similarities[child] >= self.threshold]
            else:
                return self.slice_region(region)

    def slice_region(self, region):
        """
        slice every generalized node of region to a data record
        """
        records = []
        for gn in region.iter(region.k):
            elements = [element for element in gn]
            records.append(Record(*elements))
        return records

    def almost_similar(self, similarities, threshold):
        sims = [1 for sim in similarities if sim >= threshold]
        return len(sims) / len(similarities) > 0.8

class MiningDataField(object):
    """
    Mining the data item from data records with partial tree alignment.
    """
    def __init__(self):
        self.pta = PartialTreeAligner(SimpleTreeAligner())
        self.sta = SimpleTreeAligner()

    def align_records(self, records):
        """partial align multiple records.

        for example (from paper Web Data Extraction Based on Partial Tree Alignment):
        >>> from lxml.html import fragment_fromstring
        >>> t1 = fragment_fromstring("<p> <x1></x1> <x2></x2> <x3></x3> <x></x> <b></b> <d></d> </p>")
        >>> t2 = fragment_fromstring("<p> <b></b> <n></n> <c></c> <k></k> <g></g> </p>")
        >>> t3 = fragment_fromstring("<p> <b></b> <c></c> <d></d> <h></h> <k></k> </p>")
        >>> mdf = MiningDataField()
        >>> _, seed = mdf.align_records([Record(t1), Record(t2), Record(t3)])
        >>> [e.tag for e in seed[0]]
        ['x1', 'x2', 'x3', 'x', 'b', 'n', 'c', 'd', 'h', 'k', 'g']
        >>> [e.tag for e in t1]
        ['x1', 'x2', 'x3', 'x', 'b', 'd']
        """

        # sort by the tree size
        sorted_records = sorted(records, key=Record.size)

        # seed is the largest tree
        seed = sorted_records.pop()

        # a dict like {'t2': {}, 't3': {}, etc}
        # the nested dictionary is like {'seed_element' : 'original_element'}
        mappings = defaultdict(dict)
        seed_copy = copy.deepcopy(seed)
        mappings.setdefault(seed, self._create_seed_mapping(seed_copy, seed))

        R = []
        items = []
        while len(sorted_records):
            next = sorted_records.pop()
            modified, partial_match, aligned = self.pta.align(seed_copy, next)
            mappings.update({next: aligned})

            if modified:
                sorted_records.extend(R)
                R = []
            else:
                # add it back to try it later since seed might change
                if partial_match:
                    R.append(next)

        for record in records:
            aligned = mappings[record]
            items.append(self._extract_item(seed_copy, aligned))

        return items, seed_copy

    def align_record(self, seed, record):
        """simple align the given record with given seed
        """
        alignment = self.sta.align(seed, record)
        aligned = dict({alignment.first: alignment.second})
        for sub in alignment.subs:
            aligned.update({sub.first: sub.second})
        return self._extract_item(seed, aligned)

    def _create_seed_mapping(self, seed, record):
        """create a mapping from seed record to data record.

        for example:
        >>> from lxml.html import fragment_fromstring
        >>> t1 = fragment_fromstring("<p id='1'> <a></a> <b></b> </p>")
        >>> d1 = Record(t1)
        >>> p1 = t1

        >>> t2 = fragment_fromstring("<p id='2'> <a></a> <b></b> </p>")
        >>> d2 = Record(t2)
        >>> p2 = t2

        >>> mdr = MiningDataField()
        >>> d = mdr._create_seed_mapping(d1, d2)
        >>> d[p1] == p2
        True

        """
        d = {}
        for s, e in zip(seed, record):
            d[s] = e
            d.update(self._create_seed_mapping(s, e))
        return d

    def _extract_item(self, seed, mapping):
        """extract data item from the tree.

        seed: the seed tree
        mapping: a seed element to original element dict
        """
        r = []
        for element in seed:
            r.extend(self._extract_element(element, mapping))
        return r

    def _extract_element(self, seed, mapping):
        r = []
        e = mapping.get(seed, None)

        # handle text
        if e is not None:
            if seed.text and seed.text.strip():
                r.append(Field(self._get_text(e.text), ''))
        else:
            if seed.text and seed.text.strip():
                r.append(Field(u'', ''))

        # handle children
        for child in seed:
            r.extend(self._extract_element(child, mapping))

        # handle tail
        if e is not None:
            if seed.tail and seed.tail.strip():
                r.append(Field(self._get_text(e.tail) or u'', ''))
        else:
            if seed.tail and seed.tail.strip():
                r.append(Field(u'', ''))

        return r

    def _get_text(self, text):
        if text != None:
            if not isinstance(text, unicode):
                return text.decode('utf8', 'ignore')
            return text
        return u''

