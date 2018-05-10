"""
Holds a class for storing lists of data (timeseries etc), and related methods.
"""
from collections import MutableSequence
from math import inf
from .utils import to_float


class DataList(MutableSequence):
    """ A list of datasets, that keeps track of some useful additional data
    such as min/max values.
    Datasets are on the format [(x1, y1), (x2, y2), ...]
    """
    min_val = inf
    max_val = -inf
    _x_points = set()

    def __init__(self, *args):
        self.list = list()
        self.extend(list(args))

    def check(self, v):
        """ Update metadata with newly added data """
        values = [to_float(x[1]) for x in v]
        values = [x for x in values if x is not None]
        self.min_val = min(self.min_val, min(values))
        self.max_val = max(self.max_val, max(values))
        self._x_points.update([x[0] for x in v])

    @property
    def x_points(self):
        return sorted(list(self._x_points))

    def __len__(self):
        return len(self.list)

    def __getitem__(self, i):
        return self.list[i]

    def __delitem__(self, i):
        del self.list[i]

    def __setitem__(self, i, v):
        self.check(v)
        self.list[i] = v

    def insert(self, i, v):
        self.check(v)
        self.list.insert(i, v)

    def __str__(self):
        return str(self.list)
