from __future__ import division

def tree_size(root):
    """
    Get the subtree size.

    for example:
    >>> from lxml.html import fragment_fromstring, tostring

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
    if e is not None and len(e):
        return e.tag
    return None

def _get_child(e, i):
    if i >= len(e):
        return None
    return e[i]

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

    def match(self, t1, t2):
        """
        match two trees with generalized node.
        """
        matrix = _create_2d_matrix(len(t1) + 1, len(t2) + 1)
        for i in xrange(1, len(matrix)):
            for j in xrange(1, len(matrix[0])):
                matrix[i][j] = max(matrix[i][j - 1], matrix[i - 1][j])
                matrix[i][j] = max(matrix[i][j], matrix[i - 1][j - 1] + self._single_match(t1[i - 1], t2[j - 1]))
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

    def __init__(self, e=None, score=0):
        self.element = e
        self.score = score
        self.subs = []

    def add(self, alignment):
        self.subs.append(alignment)
        if len(alignment.subs):
            self.subs.extend(alignment.subs)

    def __str__(self):
        return '{}: {}'.format(self.e, self.score)


class SimpleTreeAlign(object):
    """
    Simple Tree Alignment.
    """
    def __init__(self, ger_root=_get_root, get_children_count=_get_children_count, get_child=_get_child):
        self.get_root = ger_root
        self.get_children_count = get_children_count
        self.get_child = get_child

    def _single_align(self, t1, t2):
        """
        match two single trees.
        >>> get_root = lambda x: x[0]
        >>> get_children_count = lambda x: len(x) - 1
        >>> get_child = lambda x, i: x[i+1]
        >>> sta = SimpleTreeAlign(get_root, get_children_count, get_child)

        >>> t1 = ('a', ('b',), ('c',), ('e',))
        >>> t2 = ('a', ('b',), ('c',), ('d',))
        >>> alignment = sta._single_align(t1, t2)
        >>> alignment.score
        3
        >>> [align.element for align in alignment.subs]
        ['c', 'b']

        >>> t1 = ('c', ('b',), ('e',))
        >>> t2 = ('c', ('b',), ('e',))
        >>> alignment = sta._single_align(t1, t2)
        >>> alignment.score
        3
        >>> [align.element for align in alignment.subs]
        ['e', 'b']

        >>> t1 = ('a', ('b',), ('c', ('b',), ('e',)), ('e',))
        >>> t2 = ('a', ('b',), ('c', ('b',), ('e',)), ('d',))
        >>> alignment = sta._single_align(t1, t2)
        >>> alignment.score
        5
        >>> [align.element for align in alignment.subs]
        ['c', 'e', 'b', 'b']

        >>> t1 = ('a', ('b',), ('c', ('b', ('a',)), ('e',)), ('e',))
        >>> t2 = ('a', ('b',), ('c', ('b', ('a',)), ('e',)), ('d',))
        >>> alignment = sta._single_align(t1, t2)
        >>> alignment.score
        6
        >>> [align.element for align in alignment.subs]
        ['c', 'e', 'b', 'a', 'b']

        """
        if self.get_root(t1) is None or self.get_root(t2) is None:
            return TreeAlignment()
        if self.get_root(t1) != self.get_root(t2):
            return TreeAlignment()

        alignment = TreeAlignment(self.get_root(t1))

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
                alignment_matrix[i - 1][j - 1] = self._single_align(self.get_child(t1, i - 1), self.get_child(t2, j - 1))
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
