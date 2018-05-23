"""
Holds a class for storing lists of data (timeseries etc), and related methods.
"""
from collections import MutableSequence
from math import inf
from .utils import to_float
from numpy import array, isnan, interp, flatnonzero


def fill_na(arr):
    """Get an estimate for missing value based on closest non-missing values in
    series.
    https://stackoverflow.com/questions/9537543/replace-nans-in-numpy-array-with-closest-non-nan-value

    >>> fill_na([2.0, None, 4.0])
    [2.0, 3.0, 4.0]
    """
    if isinstance(arr, list):
        arr = array(arr)
    arr = arr.astype(float)
    mask = isnan(arr)
    arr[mask] = interp(flatnonzero(mask),
                       flatnonzero(~mask),
                       arr[~mask])

    return arr.tolist()


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
    def values(self):
        """ Return values from each data serie """
        return [[to_float(x[1]) for x in s] for s in self.list]

    @property
    def as_dict(self):
        """ Return data points as dictionaries """
        return [{x[0]: x[1] for x in s} for s in self.list]

    @property
    def filled_values(self):
        """ Return values with all gaps filled, so that each series has the
        same number of points.

        >>>> dl = DataList([
                    [("a", 5), ("b", 6), ("c", 7)],
                    [("a", 1), ("c", 3)]
             ])
        >>>> dl.filled_y_values
        [[5, 6, 7], [1, 2, 3]]
        """

        x_points = self.x_points
        return [fill_na([to_float(d[x])
                        if x in d else None
                        for x in x_points])
                for d in self.as_dict]

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
