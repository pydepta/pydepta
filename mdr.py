from collections import namedtuple
from trees import SimpleTreeMatch, tree_depth

GeneralizedNode = namedtuple('GeneralizedNode', ['element', 'length'])
DataRecord = namedtuple('DataRecord', ['element', 'size'])

class DataRegion(object):
    def __init__(self, **dict):
        self.__dict__.update(dict)

    def __str__(self):
        return 'parent {}, start {}, k {} covered {} length {}'.format(self.parent, self.start, self.k, self.covered,
                                                                       len(self.parent))

    def iter(self, k):
        """
        >>> root = [1, 2, 3, 4, 5]
        >>> region = DataRegion(parent=root, start=1, k=1, covered=4)
        >>> list(region.iter(1))
        [[2], [3], [4], [5]]

        >>> region = DataRegion(parent=root, start=1, k=2, covered=4)
        >>> list(region.iter(2))
        [[2, 3], [4, 5]]

        >>> region = DataRegion(parent=root, start=1, k=1, covered=4)
        >>> list(region.iter(2))
        [[2, 3], [4, 5]]

        """
        for i in xrange(self.start, self.start + self.covered, k):
            yield self.parent[i:i + k]

def pairwise(a, K, start=0):
    """
    A generator to return the comparison pair.

    for example:
    >>> list(pairwise([1, 2, 3, 4, 5, 6, 7, 8, 9, 10], 3))
    [([1], [2]), ([2], [3]), ([3], [4]), ([4], [5]), ([5], [6]), ([6], [7]), ([7], [8]), ([8], [9]), ([9], [10]), ([1, 2], [3, 4]), ([3, 4], [5, 6]), ([5, 6], [7, 8]), ([7, 8], [9, 10]), ([1, 2, 3], [4, 5, 6]), ([4, 5, 6], [7, 8, 9])]
    >>> list(pairwise([1, 2, 3, 4, 5, 6, 7, 8, 9, 10], 2))
    [([1], [2]), ([2], [3]), ([3], [4]), ([4], [5]), ([5], [6]), ([6], [7]), ([7], [8]), ([8], [9]), ([9], [10]), ([1, 2], [3, 4]), ([3, 4], [5, 6]), ([5, 6], [7, 8]), ([7, 8], [9, 10])]
    >>> list(pairwise([1, 2, 3, 4, 5, 6, 7, 8, 9, 10], 3, 1))
    [([2], [3]), ([3], [4]), ([4], [5]), ([5], [6]), ([6], [7]), ([7], [8]), ([8], [9]), ([9], [10]), ([2, 3], [4, 5]), ([4, 5], [6, 7]), ([6, 7], [8, 9]), ([2, 3, 4], [5, 6, 7]), ([5, 6, 7], [8, 9, 10])]
    """
    for k in xrange(1, K + 1):
        for i in xrange(start, len(a), k):
            slice_a = a[i:i + k]
            slice_b = a[i + k: i + 2 * k]

            if len(slice_a) >= k and len(slice_b) >= k:
                yield slice_a, slice_b

class MiningDataRegion(object):
    def __init__(self, root, max_generalized_nodes=3, threshold=0.3, **options):
        self.root = root
        self.max_generalized_nodes = max_generalized_nodes
        self.threshold = threshold
        self.stm = SimpleTreeMatch()
        self.options = options

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
        cur_region = DataRegion(parent=root, start=0, k=0, covered=0)
        max_region = DataRegion(parent=root, start=0, k=0, covered=0)
        data_regions = []

        for k in xrange(1, max_generalized_nodes + 1):
            for i in xrange(start, k + start):
                flag = True
                for j in xrange(i, len(root) - k, k):
                    pair = GeneralizedNode(root[j], k), GeneralizedNode(root[j + k], k)
                    score = scores.get(pair)
                    if score >= threshold:
                        if flag:
                            cur_region.k = k
                            cur_region.start = j
                            cur_region.covered = 2 * k
                            flag = False
                        else:
                            cur_region.covered += k
                    elif not flag:  # doesn't match but previous match
                        break

                if max_region.covered < cur_region.covered and (
                        max_region.start == 0 or cur_region.start <= max_region.start):
                    max_region.k = cur_region.k
                    max_region.start = cur_region.start
                    max_region.covered = cur_region.covered

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
            score = self.stm.normalized_match_score(a, b)
            gn1 = GeneralizedNode(a[0], len(a))
            gn2 = GeneralizedNode(b[0], len(b))
            scores.setdefault((gn1, gn2), score)
            if self.options.get('debug'):
                print self._format_generalized_node(gn1, gn2), score
        return scores

    def _format_generalized_node(self, gn1, gn2):
        assert gn1.length == gn2.length, 'must be have same K generalized nodes'
        return "{}:{} {}:{}".format(gn1.element.tag, gn1.length, gn2.element.tag, gn1.length)


class MiningDataRecord(object):
    """
    mining the data record from a region.

    basic assumption:
    the subtree of data records also similar. so if not any adjacent pair of them are
    similar (less than threshold), data region itself is a data record,
    otherwise children are individual data record.
    """

    def __init__(self, threshold=0.3):
        self.stm = SimpleTreeMatch()
        self.threshold = threshold

    def find_records(self, region):
        records = []
        if region.k == 1:
            for i in xrange(region.start, region.start + region.covered):
                for child1, child2 in pairwise(region.parent, 1, region.start):
                    similarity = self.stm.normalized_match_score(child1, child2)
                    if similarity < self.threshold:
                        return self.slice_region(region)
                else:
                    # each child of generalized node is a data record
                    for gn in region.iter(1):
                        records.extend([DataRecord(element=c, size=1) for c in gn])

        return self.slice_region(region)

    def slice_region(self, region):
        """
        slice every generalized node of region to a data record
        """
        records = []
        for gn in region.iter(region.k):
            records.append(DataRecord(element=gn[0], size=len(gn)))
        return records

