"""
Holds a class for storing lists of data (timeseries etc), and related methods.
"""
from collections.abc import MutableSequence
from math import inf
from numpy import array, isnan, interp, flatnonzero
import numpy as np
from io import StringIO
import csv
from .utils import to_float


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

    def __init__(self, *args):
        self.min_val = inf
        self.max_val = -inf
        self._x_points = set()
        self.list = list()
        self.extend(list(args))

    def check(self, v):
        # Update metadata with newly added data
        values = [to_float(x[1]) for x in v]
        values = [x for x in values if x is not None]
        if values:
            self.min_val = min(self.min_val, min(values))
            self.max_val = max(self.max_val, max(values))
        self._x_points.update([x[0] for x in v])

        # Normalize to 3 digit syntax
        v = [x if len(x) > 2
             else (x[0], x[1], None)
             for x in v]
        # Automatically enumerate empty x values / category names if empty
        v = [x if x[0] not in ["", None]
             else (i, x[1], x[2])
             for i, x in enumerate(v)]
        return v

    @property
    def values(self):
        """ Return values from each data serie """
        return [[to_float(x[1]) for x in s] for s in self.list]

    @property
    def stacked_values(self):
        """Returns the sum of all y values in each x """
        # converts None to np.na for np.sum()
        values = array(self.values, dtype=float)
        return np.nansum(values, axis=0).tolist()

    @property
    def stacked_max_val(self):
        return max(self.stacked_values)

    @property
    def as_dict(self):
        """ Return data points as dictionaries """
        return [{x[0]: x[1] for x in s} for s in self.list]

    @property
    def as_csv(self):
        """Render as csv string.
        """
        # transform data as list of lists
        ll = [self.x_points] + self.as_list_of_lists
        # transpose
        ll = [x for x in map(list, zip(*ll))]
        csv_str = StringIO()
        writer = csv.writer(csv_str)
        writer.writerows(ll)
        return csv_str.getvalue()

    @property
    def as_list_of_lists(self):
        """Return values with all gaps filled, so that each series has the
        same number of points as a list of list.
        """
        return [[d[x] if x in d else None
                 for x in self.x_points]
                for d in self.as_dict]

    @property
    def filled_values(self):
        """ Return values with all gaps filled, so that each series has the
        same number of points. Estimates missing values as the mean between
        the previous and next value.

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

    @property
    def inner_min_x(self):
        return max(list(filter(lambda x: x[1] is not None, s))[0][0] for s in self.list)

    @property
    def inner_max_x(self):
        return min(list(filter(lambda x: x[1] is not None, s))[-1][0] for s in self.list)

    @property
    def outer_min_x(self):
        return min(list(filter(lambda x: x[1] is not None, s))[0][0] for s in self.list)

    @property
    def outer_max_x(self):
        return max(list(filter(lambda x: x[1] is not None, s))[-1][0] for s in self.list)



    def __len__(self):
        return len(self.list)

    def __getitem__(self, i):
        return self.list[i]

    def __delitem__(self, i):
        del self.list[i]

    def __setitem__(self, i, v):
        v = self.check(v)
        self.list[i] = v

    def insert(self, i, v):
        v = self.check(v)
        self.list.insert(i, v)

    def __str__(self):
        return str(self.list)
