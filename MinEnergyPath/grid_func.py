__author__ = 'tzelleke'

import numpy as np
from scipy.ndimage.filters import gaussian_filter

import grid


class _OptimizationMixin(object):
    """
    Mixin class that provides functionality to find
    minima of a GridFunc on the grid.
    """

    def minimize(self, coords):
        coords_idx = self.map_nearest(coords)
        idx = self.idx(coords_idx)
        min_idx = self._minimize(idx)
        return self.coords_idx(min_idx)

    def _minimize(self, idx):
        min_idx = idx
        min_pot = self.pot_1D[idx]
        found_min = False
        while not found_min:
            found_min = True
            for node in self.neighbors_idx(min_idx):
                if self.pot_1D[node] < min_pot:
                    min_idx = node
                    min_pot = self.pot_1D[node]
                    found_min = False
        return min_idx

    def _filter_min(self, bounds_idx):
        pot = self.pot_1D.reshape(self.shape)
        slices = [slice(*_) for _ in bounds_idx]
        shape = [(ub - lb) for lb, ub in bounds_idx]
        # dim = len(shape)
        min_idx = np.nanargmin(pot[slices])

        # min_coords_idx = []
        #         r = min_idx
        #         for i in range(dim):
        #             offset = 1
        #             for j in range(i+1, dim):
        #                 offset *= shape[j]
        #             coord_idx, r = divmod(r, offset)
        #             min_coords_idx.append(bounds_idx[i][0] + coord_idx)
        min_coords_idx = np.unravel_index(min_idx, shape)
        offset = [lb for lb, ub in bounds_idx]
        return tuple([(o + c) for o, c in zip(offset, min_coords_idx)])

    def g_minimize(self, *args, **kwargs):
        dim = len(self.shape)
        bounds = [None] * dim

        if len(args) > dim:
            raise RuntimeError('more arguments than dimensionality')
        for i, bound in enumerate(args):
            if bound is None:
                continue
            if type(bound) in [int, float]:
                bound = (bound,)
            if not type(bound) in [tuple, list]:
                raise TypeError('encountered not allowed argument type')
            if not len(bound) in [1, 2]:
                raise RuntimeError('encountered invalid bound')
            bounds[i] = bound

        bounds_idx = []
        for i, bound in enumerate(bounds):
            max_ub = self.shape[i]
            gv = self.grid_vecs[i].ravel()
            if bound is None:
                bounds_idx.append((0, max_ub))
            elif len(bound) is 1:
                p = bound[0]
                p = np.argmin(np.abs(p - gv))
                bounds_idx.append((p, p + 1))
            elif len(bound) is 2:
                lb, ub = bound
                lb = (np.searchsorted(gv, lb)
                      if not lb is None
                      else 0)
                ub = (np.searchsorted(gv, ub)
                      if not ub is None
                      else max_ub)
                bounds_idx.append((lb, ub))
            else:
                assert False, 'invalid bound'

        min_coords_idx = self._filter_min(bounds_idx)
        return min_coords_idx


class GridFunc(grid.Grid, _OptimizationMixin):
    """
    Object that represents a given n-dimensional ndarray
    of function values (pot) evaluated on a grid of same
    shape.
    
    Parameters
    ----------
    
    pot : n-dimensianal ndarray
    
    linspaces : list/ tuple of lists/tuples that specify
    the shape of the grid.
    Example: [[-2., 2., 100],
              [0, 1, 15],
              [30, 50, 5]]
    specifies a 3-dimensional grid of shape (100, 15, 5)
    ranging from -2 to 2 in the first dim. and 0 to 1 in
    the second dim and 30 to 50 in the last dim.
    """

    def __init__(self, pot, linspaces):
        super(GridFunc, self).__init__(linspaces)
        self.pot_1D = pot.ravel()
        assert pot.size == self.nnodes

    @classmethod
    def from_grid_vecs(cls, pot, grid_vecs):
        """
        convenience method to construct a GridFunc from
        grid vectors. Grid vectors hold the gridpoints
        along the axes of the grid.
        """
        linspaces = []
        for gv in grid_vecs:
            gv = gv.ravel()
            linspaces.append((gv[0], gv[-1], gv.size))
        return cls(pot, linspaces)

    @classmethod
    def from_file(cls, filepath):
        """
        convenience method to construct a GridFunc from
        a file, for instance from
        V.Final.out obtained through vreco
        """
        data = np.loadtxt(filepath)
        pot = data[:, -1]
        linspaces = []
        for dim in range(data.shape[-1] - 1):
            gv = np.unique(data[:, dim])
            linspaces.append((gv[0], gv[-1], gv.size))
        return cls(pot, linspaces)

    def _copy(self):
        """
        Creates a deep copy of a GridFunc instance
        :return: GridFunc
        """
        pot = self.pot_1D.reshape(self.shape)
        copy = self.__class__(pot, self.linspaces)
        return copy

    def neighbors_idx(self, idx):
        return [_ for _ in
                super(GridFunc, self).neighbors_idx(idx)
                if not np.isnan(self.pot_1D[_])]

    def smooth(self, sigma, cval=0., copy=False):
        pot = self.pot_1D.reshape(self.shape)
        pot_smoothed = gaussian_filter(pot, sigma, cval=cval, mode='constant')
        if not copy:
            gf = self
        else:
            gf = self._copy()
        gf.pot_1D = pot_smoothed.ravel()
        return gf

    def save(self, filepath_or_buffer):
        if isinstance(filepath_or_buffer, str):
            with open(filepath_or_buffer, 'w') as buffer:
                self._save(buffer)
        else:
            self._save(filepath_or_buffer)

    def _save(self, buffer):
        data = np.meshgrid(*self.grid_vecs, indexing='ij')
        data = [_.ravel() for _ in data]
        data.append(self.pot_1D)
        data = np.column_stack(data)
        chunksize = self.grid_vecs[-1].size
        for i in range(0, self.nnodes, chunksize):
            np.savetxt(buffer, data[i:i+chunksize], fmt='%16.8f', delimiter=' ')
            buffer.write('\n')


# TESTS
if __name__ == '__main__':
    def f(x, y):
        return 1. / np.exp(-(.1 * x ** 2 + 0.2 * y ** 2))

    linspaces = [[-2., 2., 11],
                 [-3, 3, 15]]
    slices = [slice(b, e, complex(0, n)) for b, e, n in linspaces]
    pot = f(*(np.mgrid[slices[0], slices[1]]))

    gf = GridFunc(pot=pot, linspaces=linspaces)
    assert gf.minimize((9, 14)) == (5, 7)

    gf = GridFunc.from_file('../data/surface.txt')
    assert gf.shape == (241, 101)

    from StringIO import StringIO
    gf = GridFunc.from_file('../data/surface.txt')
    buffer = StringIO()
    gf.save(buffer)
    with open('../data/surface.txt') as f:
        orig = f.read()
    assert orig == buffer.getvalue()
