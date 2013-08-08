cimport cython

def _get_root(e):
    return e.tag if e is not None else None

def _get_child(e, i):
    return e[i] if i < len(e) else None

def _get_children_count(e):
    return len(e)

@cython.boundscheck(False)
@cython.wraparound(False)
def tree_match(t1, t2):

    if _get_root(t1) is None or _get_root(t2) is None:
        return 0
    if _get_root(t1) != _get_root(t2):
        return 0

    m = create_2d_matrix(_get_children_count(t1) + 1, _get_children_count(t2) + 1)
    cdef int i
    cdef int j
    cdef int rows = len(m)
    cdef int cols = len(m[0])

    for i from 1 <= i < rows:
        for j from 1 <= j < cols:
            m[i][j] = max(m[i][j - 1], m[i - 1][j])
            m[i][j] = max(m[i][j], m[i - 1][j - 1] + \
                                             tree_match(_get_child(t1, i - 1),
                                                        _get_child(t2, j - 1)))
    return 1 + m[len(m) - 1][len(m[0]) - 1]

@cython.boundscheck(False)
@cython.wraparound(False)
def create_2d_matrix(rows, cols):
    return [[0 for _ in range(cols)] for _ in range(rows)]
