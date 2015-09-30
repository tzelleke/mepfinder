__author__ = 'tzelleke'

import collections
import numpy as np

class Point(object):
    attribs = {'coords': np.nan,
               'coords_idx': np.nan,
               'pot': np.nan,
               'has_nan_neighbor': False}

    def __init__(self, **kwargs):
        self.__dict__.update(Point.attribs)
        self.__dict__.update(kwargs)

    def __repr__(self):
        return repr(self.__dict__)


class Path(collections.MutableSequence):
    def __init__(self):
        self.__points = []

    def __getitem__(self, index):
        return self.__points[index]

    def __setitem__(self, index, value):
        self.__points[index] = value

    def __delitem__(self, index):
        del self.__points[index]

    def __len__(self):
        return len(self.__points)

    def insert(self, index, value):
        self.__points.insert(index, value)

    def __getattr__(self, attrname):
        if attrname in Point.attribs:
            vals = []
            for point in self.__points:
                vals.append(getattr(point, attrname, None))
            return np.array(vals)
        else:
            raise AttributeError(attrname)

    @property
    def points(self):
        return np.hstack((self.coords, self.pot[:, None]))
