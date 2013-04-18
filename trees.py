from __future__ import division
import copy


def tree_size(root):
    """
    Get the subtree size.

    for example:
    >>> from lxml.html import fragment_fromstring

    >>> root = fragment_fromstring("<p> </p>")
    >>> tree_size(root)
    1

    >>> root = fragment_fromstring("<p> <font> <a href='#top'> </a> </font> </p>")
    >>> tree_size(root)
    3

    >>> html = "<p><font><font>^ </font><a href='#top'><font>Return to the top</font></a></font><br><font>--</font> </p>"
    >>> root = fragment_fromstring(html)
    >>> tree_size(root)
    7
    """
    if len(root) == 0:
        return 1
    return sum([tree_size(child) for child in root]) + 1

def tree_depth(root):
    """
    Get the subtree depth.

    for example:
    >>> from lxml.html import fragment_fromstring

    >>> root = fragment_fromstring("<p> </p>")
    >>> tree_depth(root)
    1

    >>> root = fragment_fromstring("<p> <font> </font> </p>")
    >>> tree_depth(root)
    2

    >>> html = "<p><font><font>^ </font><a href='#top'><font>Return to the top</font></a></font><br><font>--</font> </p>"
    >>> root = fragment_fromstring(html)
    >>> tree_depth(root)
    4

    """
    if len(root) == 0:
        return 1
    return max([tree_depth(child) for child in root]) + 1

def _get_root(e):
    return e.tag if e is not None else None

def _get_child(e, i):
    return e[i] if i < len(e) else None

def _get_children_count(e):
    return len(e)

class SimpleTreeMatch(object):
    """
    Simple Tree Match.
    """
    def __init__(self, ger_root=_get_root, get_children_count=_get_children_count, get_child=_get_child):
        self.get_root = ger_root
        self.get_children_count = get_children_count
        self.get_child = get_child

    def match(self, l1, l2):
        """
        match two trees list.
        """
        matrix = _create_2d_matrix(len(l1) + 1, len(l2) + 1)
        for i in xrange(1, len(matrix)):
            for j in xrange(1, len(matrix[0])):
                matrix[i][j] = max(matrix[i][j - 1], matrix[i - 1][j])
                matrix[i][j] = max(matrix[i][j], matrix[i - 1][j - 1] + self._single_match(l1[i - 1], l2[j - 1]))
        return 1 + matrix[i][j]

    def normalized_match_score(self, t1, t2):
        t1size = sum([tree_size(e) for e in t1]) + 1
        t2size = sum([tree_size(e) for e in t2]) + 1
        return self.match(t1, t2) / ((t1size + t2size) / 2)

    def _single_match(self, t1, t2):
        """
        match two single trees.
        >>> get_root = lambda x: x[0]
        >>> get_children_count = lambda x: len(x) - 1
        >>> get_child = lambda x, i: x[i+1]
        >>> stm = SimpleTreeMatch(get_root, get_children_count, get_child)
        >>> t1 = ('tr', ('td',), ('td',))
        >>> t2 = ('tr', ('td',), ('tr',))
        >>> get_children_count(t1)
        2
        >>> stm._single_match(t1, t2)
        2
        """
        if self.get_root(t1) is None or self.get_root(t2) is None:
            return 0
        if self.get_root(t1) != self.get_root(t2):
            return 0
        matrix = _create_2d_matrix(self.get_children_count(t1) + 1, self.get_children_count(t2) + 1)
        for i in xrange(1, len(matrix)):
            for j in xrange(1, len(matrix[0])):
                matrix[i][j] = max(matrix[i][j - 1], matrix[i - 1][j])
                matrix[i][j] = max(matrix[i][j], matrix[i - 1][j - 1] + \
                                                 self._single_match(self.get_child(t1, i - 1),
                                                                    self.get_child(t2, j - 1)))
        return 1 + matrix[len(matrix) - 1][len(matrix[0]) - 1]


class TreeAlignment(object):

    TRACE_LEFT = 1
    TRACE_UP = 2
    TRACE_DIAG = 3

    def __init__(self, first=None, second=None, score=0):
        self.first = first
        self.second = second
        self.score = score
        self.subs = []

    def add(self, alignment):
        if self.first is None and self.second is None:
            self.first, self.second = alignment.first, alignment.second
        else:
            self.subs.append(alignment)
        self.subs.extend(alignment.subs)

    @property
    def tag(self):
        assert self.first.tag == self.second.tag
        return self.first.tag

    def __str__(self):
        return '{} {}: {}'.format(self.first, self.subs, self.score)


class SimpleTreeAligner(object):
    """
    Simple Tree Aligner.
    """
    def __init__(self, ger_root=_get_root, get_children_count=_get_children_count, get_child=_get_child):
        self.get_root = ger_root
        self.get_children_count = get_children_count
        self.get_child = get_child

    def align(self, l1, l2):
        """
        align 2 lists of trees

        for example:
        >>> get_root = lambda x: x[0]
        >>> get_children_count = lambda x: len(x) - 1
        >>> get_child = lambda x, i: x[i+1]
        >>> sta = SimpleTreeAligner(get_root, get_children_count, get_child)

        >>> l1 = [('a', ('b',), ('c',), ('e',))]
        >>> l2 = [('a', ('b',), ('c',), ('d',))]
        >>> alignment = sta.align(l1, l2)
        >>> get_root(alignment.first)
        'a'
        >>> alignment.score
        4
        >>> [get_root(align.first) for align in alignment.subs]
        ['c', 'b']
        """
        alignment = TreeAlignment()
        matrix = _create_2d_matrix(len(l1) + 1, len(l2) + 1)
        alignment_matrix = _create_2d_matrix(len(l1), len(l2))
        trace = _create_2d_matrix(len(l1), len(l2))

        for i in xrange(1, len(matrix)):
            for j in xrange(1, len(matrix[0])):
                if matrix[i][j-1] > matrix[i-1][j]:
                    matrix[i][j] = matrix[i][j-1]
                    trace[i-1][j-1] = TreeAlignment.TRACE_LEFT
                else:
                    matrix[i][j] = matrix[i-1][j]
                    trace[i-1][j-1] = TreeAlignment.TRACE_UP

                alignment_matrix[i-1][j-1] = self.single_align(l1[i - 1], l2[j - 1])
                score = matrix[i-1][j-1] + alignment_matrix[i-1][j-1].score

                if score > matrix[i-1][j-1]:
                    matrix[i][j] = score
                    trace[i-1][j-1] = TreeAlignment.TRACE_DIAG

        row = len(trace) - 1
        col = len(trace[0]) - 1

        while row >= 0 and col >= 0:
            if trace[row][col] == TreeAlignment.TRACE_DIAG:
                alignment.add(alignment_matrix[row][col])
                row -= 1
                col -= 1
            elif trace[row][col] == TreeAlignment.TRACE_UP:
                row -= 1
            elif trace[row][col] == TreeAlignment.TRACE_LEFT:
                col -= 1

        alignment.score = 1 + matrix[len(matrix)-1][len(matrix[0]) - 1]
        return alignment

    def single_align(self, t1, t2):
        """
        match two single trees.
        >>> get_root = lambda x: x[0]
        >>> get_children_count = lambda x: len(x) - 1
        >>> get_child = lambda x, i: x[i+1]
        >>> sta = SimpleTreeAligner(get_root, get_children_count, get_child)

        >>> t1 = ('a', ('b',), ('c',), ('e',))
        >>> t2 = ('a', ('b',), ('c',), ('d',))
        >>> alignment = sta.single_align(t1, t2)
        >>> (get_root(alignment.first), get_root(alignment.second))
        ('a', 'a')
        >>> alignment.score
        3
        >>> [get_root(align.first) for align in alignment.subs]
        ['c', 'b']

        >>> t1 = ('c', ('b',), ('e',))
        >>> t2 = ('c', ('b',), ('e',))
        >>> alignment = sta.single_align(t1, t2)
        >>> alignment.score
        3
        >>> [get_root(align.first) for align in alignment.subs]
        ['e', 'b']

        >>> t1 = ('a', ('b',), ('c', ('b',), ('e',)), ('e',))
        >>> t2 = ('a', ('b',), ('c', ('b',), ('e',)), ('d',))
        >>> alignment = sta.single_align(t1, t2)
        >>> alignment.score
        5
        >>> [get_root(align.first) for align in alignment.subs]
        ['c', 'e', 'b', 'b']

        >>> t1 = ('a', ('b',), ('c', ('b', ('a',)), ('e',)), ('e',))
        >>> t2 = ('a', ('b',), ('c', ('b', ('a',)), ('e',)), ('d',))
        >>> alignment = sta.single_align(t1, t2)
        >>> alignment.score
        6
        >>> [get_root(align.first) for align in alignment.subs]
        ['c', 'e', 'b', 'a', 'b']

        >>> t1 = ('p', ('a',), ('b',), ('e',))
        >>> t2 = ('p', ('b',), ('c',), ('d',), ('e',))

        >>> alignment = sta.single_align(t1, t2)
        >>> alignment.score
        3

        >>> from lxml.html import fragment_fromstring, tostring
        >>> t1 = fragment_fromstring("<div> <h1></h1> <h2></h2> <h5></h5> </div>")
        >>> t2 = fragment_fromstring("<div> <h2></h2> <h3></h3> <h4></h4> <h5></h5> </div>")

        >>> (_get_root(t1), _get_children_count(t1), _get_child(t1, 1).tag)
        ('div', 3, 'h2')

        >>> (_get_root(t2), _get_children_count(t2), _get_child(t2, 1).tag)
        ('div', 4, 'h3')

        >>> sta = SimpleTreeAligner()
        >>> alignment = sta.single_align(t1, t2)
        >>> alignment.score
        3

        """
        if self.get_root(t1) is None or self.get_root(t2) is None:
            return TreeAlignment()
        if self.get_root(t1) != self.get_root(t2):
            return TreeAlignment()

        alignment = TreeAlignment(t1, t2)

        t1_len = self.get_children_count(t1)
        t2_len = self.get_children_count(t2)

        matrix = _create_2d_matrix(t1_len + 1, t2_len + 1)
        alignment_matrix = _create_2d_matrix(t1_len, t2_len)
        trace = _create_2d_matrix(t1_len, t2_len)

        for i in xrange(1, len(matrix)):
            for j in xrange(1, len(matrix[0])):
                if matrix[i][j - 1] > matrix[i - 1][j]:
                    matrix[i][j] = matrix[i][j - 1]
                    trace[i - 1][j - 1] = TreeAlignment.TRACE_LEFT
                else:
                    matrix[i][j] = matrix[i - 1][j]
                    trace[i - 1][j - 1] = TreeAlignment.TRACE_UP
                alignment_matrix[i - 1][j - 1] = self.single_align(self.get_child(t1, i - 1), self.get_child(t2, j - 1))
                score = matrix[i - 1][j - 1] + alignment_matrix[i - 1][j - 1].score
                if score > matrix[i][j]:
                    matrix[i][j] = score
                    trace[i - 1][j - 1] = TreeAlignment.TRACE_DIAG

        row = len(trace) - 1

        if row >= 0:
            col = len(trace[0]) - 1
        else:
            col = -1

        while row >= 0 and col >= 0:
            if trace[row][col] == TreeAlignment.TRACE_DIAG:
                alignment.add(alignment_matrix[row][col])
                row -= 1
                col -= 1
            elif trace[row][col] == TreeAlignment.TRACE_UP:
                row -= 1
            elif trace[row][col] == TreeAlignment.TRACE_LEFT:
                col -= 1

        alignment.score = 1 + matrix[len(matrix) - 1][len(matrix[0]) - 1]
        return alignment

def _create_2d_matrix(rows, cols):
    """
    >>> m = _create_2d_matrix(2, 3)
    >>> (len(m), len(m[0]))
    (2, 3)
    """
    return [[0 for _ in range(cols)] for _ in range(rows)]

def find_subsequence(iterable, predicate):
    """
    find the subsequence in iterable which predicted return true

    for example:
    >>> find_subsequence([1, 10, 2, 3, 5, 8, 9],  lambda x: x in [1, 0, 2, 3, 4, 5, 8, 9])
    [[1], [2, 3, 5, 8, 9]]

    >>> find_subsequence([1, 10, 2, 3, 5, 8, 9],  lambda x: x not in [1, 0, 2, 3, 4, 5, 8, 9])
    [[10]]

    """
    seqs = []
    seq = []
    continuous = False
    for i in iterable:
        if predicate(i):
            if continuous:
                seq.append(i)
            else:
                seq = [i]
                continuous = True
        elif continuous:
            seqs.append(seq)
            seq = []
            continuous = False
    if len(seq):
        seqs.append(seq)
    return seqs

class PartialTreeAligner(object):
    def __init__(self, aligner, **options):
        self.sta = aligner
        self.options = options

    def align(self, l1, l2):
        """
        partial align lxml tree list (l2) to another lxml tree list (l1).

        for example (from Web Data Extraction Based on Partial Tree Alignment):
        >>> from lxml.html import fragment_fromstring, tostring
        >>> sta = SimpleTreeAligner()
        >>> pta = PartialTreeAligner(sta)

        "flanked by 2 sibling nodes"
        >>> t1 = fragment_fromstring("<p> <a></a> <b></b> <e></e> </p>")
        >>> t2 = fragment_fromstring("<p> <b></b> <c></c> <d></d> <e></e> </p>")
        >>> _, _, mapping = pta.align([t1], [t2])
        >>> [e.tag for e in t1]
        ['a', 'b', 'c', 'd', 'e']
        >>> sorted([e.tag for e in mapping.itervalues()])
        ['b', 'c', 'd', 'e', 'p']

        "rightmost nodes"
        >>> t1 = fragment_fromstring("<p> <a></a> <b></b> <e></e> </p>")
        >>> t2 = fragment_fromstring("<p> <e></e> <f></f> <g></g> </p>")
        >>> _, _, mapping = pta.align([t1], [t2])
        >>> [e.tag for e in t1]
        ['a', 'b', 'e', 'f', 'g']
        >>> sorted([e.tag for e in mapping.itervalues()])
        ['e', 'f', 'g', 'p']

        "leftmost nodes"
        >>> t1 = fragment_fromstring("<p> <a></a> <b></b> <e></e> </p>")
        >>> t2 = fragment_fromstring("<p> <f></f> <g></g> <a></a> </p>")
        >>> _, _, mapping = pta.align([t1], [t2])
        >>> [e.tag for e in t1]
        ['f', 'g', 'a', 'b', 'e']
        >>> sorted([e.tag for e in mapping.itervalues()])
        ['a', 'f', 'g', 'p']

        "no unique insertion"
        >>> t1 = fragment_fromstring("<p> <a></a> <b></b> <e></e> </p>")
        >>> t2 = fragment_fromstring("<p> <a></a> <g></g> <e></e> </p>")
        >>> _, _, mapping = pta.align([t1], [t2])
        >>> [e.tag for e in t1]
        ['a', 'b', 'e']
        >>> sorted([e.tag for e in mapping.itervalues()])
        ['a', 'e', 'p']

        "multiple unaligned nodes"
        >>> t1 = fragment_fromstring("<p> <x></x> <b></b> <d></d> </p>")
        >>> t2 = fragment_fromstring("<p> <b></b> <c></c> <d></d> <h></h> <k></k> </p>")
        >>> _, _, mapping = pta.align([t1], [t2])
        >>> [e.tag for e in t1]
        ['x', 'b', 'c', 'd', 'h', 'k']
        >>> sorted([e.tag for e in mapping.itervalues()])
        ['b', 'c', 'd', 'h', 'k', 'p']

        """
        alignment = self.sta.align(l1, l2)
        aligned = dict({alignment.first: alignment.second})
        for sub in alignment.subs:
            aligned.update({sub.first: sub.second})

        # add reverse mapping too
        reverse_aligned = dict(reversed(i) for i in aligned.items())

        modified = False

        unaligned_elements = self.find_unaligned_elements(aligned, l2)
        for l in unaligned_elements:
            left_most = l[0]
            right_most = l[-1]

            prev_sibling = left_most.getprevious()
            next_sibling = right_most.getnext()

            if prev_sibling is None:
                if next_sibling is not None:
                    # leftmost alignment
                    next_sibling_match = reverse_aligned.get(next_sibling, None)
                    for i, element in enumerate(l):
                        element_copy = copy.deepcopy(element)
                        next_sibling_match.getparent().insert(i, element_copy)
                        aligned.update({element_copy: element})
                    modified = True

            elif next_sibling is None:
                # rightmost alignment
                prev_sibling_match = reverse_aligned.get(prev_sibling, None)
                previous_match_index = self._get_index(prev_sibling_match)
                # unique insertion
                for i, element in enumerate(l):
                    element_copy = copy.deepcopy(element)
                    prev_sibling_match.getparent().insert(previous_match_index + 1 + i, element_copy)
                    aligned.update({element_copy: element})
                modified = True
            else:
                # flanked by two sibling elements
                prev_sibling_match = reverse_aligned.get(prev_sibling, None)
                next_sibling_match = reverse_aligned.get(next_sibling, None)

                if prev_sibling_match is not None and next_sibling_match is not None:
                    next_match_index = self._get_index(next_sibling_match)
                    previous_match_index = self._get_index(prev_sibling_match)
                    if next_match_index - previous_match_index == 1:
                        # unique insertion
                        for i, element in enumerate(l):
                            element_copy = copy.deepcopy(element)
                            prev_sibling_match.getparent().insert(previous_match_index + 1 + i, element_copy)
                            aligned.update({element_copy: element})
                        modified = True
        return modified, len(unaligned_elements) > 0, aligned

    def find_unaligned_elements(self, aligned, elements):
        """
        find the unaligned elements recursively from elements.

        >>> from lxml.html import fragment_fromstring
        >>> t1 = fragment_fromstring("<div> <h1></h1> <h2></h2> <h5></h5> </div>")
        >>> t2 = fragment_fromstring("<div> <h2></h2> <h3></h3> <h4></h4> <h5></h5> <h6></h6></div>")

        >>> sta = SimpleTreeAligner()
        >>> pta = PartialTreeAligner(None)
        >>> aligned = dict((align.first, align.second) for align in sta.align([t1], [t2]).subs)
        >>> unaligned = pta.find_unaligned_elements(aligned, [t2])
        >>> [[e.tag for e in l] for l in unaligned]
        [['h3', 'h4'], ['h6']]
        """
        predicate = lambda x: x not in aligned.values()
        unaligned = []

        for element in elements:
            current_level = find_subsequence(element, predicate)
            unaligned.extend(current_level)

            for child in element:
                unaligned.extend(find_subsequence(child, predicate))
        return unaligned

    def _get_index(self, element):
        """
        get the position of the element within the parent.
        """
        return element.getparent().index(element)