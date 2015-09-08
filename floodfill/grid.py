'''
@author: tzelleke
'''

from itertools import product

import numpy as np


class Grid(object):
    def __init__(self, linspaces):
        self.shape = tuple([lsp[2] for lsp in linspaces])
        self.extents = tuple([(lsp[0], lsp[1]) for lsp in linspaces])
        self.nnodes = self._init_nnodes(self.shape)
        self.grid_vecs = self._init_grid_vecs(linspaces)
        self._dim_offsets = self._init_dim_offsets(self.shape)
        self._neigbor_offsets = self._init_neighbor_offsets(self._dim_offsets)

    @classmethod
    def from_size(cls, extents, size, weights=None):
        dim = len(extents)
        f = np.ceil(np.power(size, 1. / dim))
        linspaces = [(ext[0], ext[1], f) for ext in extents]

        return cls(linspaces)

    @classmethod
    def from_range(cls, ranges):
        from math import floor

        linspaces = []
        for start, limit, stepsize in ranges:
            nsteps = floor((limit - start) / float(stepsize))
            stop = start + nsteps * stepsize
            lower, upper = start, stop
            if stepsize < 0:
                lower, upper = upper, lower
            linspaces.append((lower, upper, nsteps + 1))

        return cls(linspaces)

    @staticmethod
    def _init_nnodes(shape):
        nnodes = 1
        for s in shape:
            nnodes *= s

        return nnodes

    @staticmethod
    def _init_grid_vecs(linspaces):
        dim = len(linspaces)
        base_shape = [1] * dim

        grid_vecs = []
        for i in range(dim):
            vec = np.linspace(*(linspaces[i]))
            vec_shape = base_shape[:]
            vec_shape[i] = linspaces[i][2]
            grid_vecs.append(vec.reshape(vec_shape))

        return tuple(grid_vecs)

    @staticmethod
    def _init_dim_offsets(shape):
        dim = len(shape)
        offsets = []
        for i in range(dim):
            offset = 1
            for j in range(i + 1, dim):
                offset *= shape[j]
            offsets.append(offset)

        return tuple(offsets)

    @staticmethod
    def _init_neighbor_offsets(dim_offsets):
        s = (-1, 0, 1)
        dim = len(dim_offsets)
        n = 3 ** dim
        identiy_idx = (n - 1) / 2
        coord_idx_offset = list(product(*([s] * dim)))
        coord_idx_offset.pop(identiy_idx)

        # return np.dot(np.array(coord_idx_offset),
        # np.array(dim_offsets)[:, None])
        return np.array(coord_idx_offset)

    def map_nearest(self, coords):
        g_vecs = self.grid_vecs

        return tuple([np.argmin(np.abs(d[0] - d[1]))
                      for d in zip(g_vecs, coords)])

    def coords(self, coords_idx):

        return tuple([self.grid_vecs[dim].ravel()[idx]
                      for dim, idx in enumerate(coords_idx)])

    def idx(self, coords_idx):

        return sum([coord_idx * dim_offset
                    for coord_idx, dim_offset in zip(coords_idx, self._dim_offsets)])

    def coords_idx(self, idx):
        r = idx
        coords_idx = []
        for offset in self._dim_offsets:
            coord_idx, r = divmod(r, offset)
            coords_idx.append(coord_idx)

        return tuple(coords_idx)

    def neighbors(self, coords_idx):

        return self.neighbors_idx(self.idx(coords_idx))

    def neighbors_idx(self, idx):
        coords_idx = self.coords_idx(idx)
        neighbors = coords_idx + self._neigbor_offsets

        return [self.idx(_) for _ in
                neighbors[np.all(
                    (self.shape > neighbors) & (neighbors >= 0),
                    axis=1)]]

    def refine(self, size, sub_grids=True):
        stepsizes = np.array([_ - 1 for _ in self.shape])
        current_shape = np.array(self.shape[:])
        nsubpoints = 0
        while np.prod(current_shape) < size:
            nsubpoints += 1
            current_shape += stepsizes

        grid = Grid(self.extents, current_shape.tolist())
        if sub_grids:
            gvs = [_.ravel() for _ in self.grid_vecs]
            sub_grids = []
            ncorners = 2
            sub_shape = [nsubpoints + ncorners] * self.dim
            for p in product(*[range(_ - 1) for _ in self.shape[::-1]]):
                extents = [(gv[i], gv[i + 1]) for gv, i in zip(gvs, p[::-1])]
                sub_grids.append(Grid(extents, sub_shape))

            return grid, tuple(sub_grids)
        else:

            return grid

# TESTS
if __name__ == '__main__':
    g = Grid([(-5, 5, 20),
              (0, 1, 15),
              (0, 30, 10)])
    assert g.shape == (20, 15, 10)
    assert g.extents == ((-5, 5),
                         (0, 1),
                         (0, 30))
    assert g.nnodes == 3000
    assert g._dim_offsets == (150, 10, 1)

    point = (-0.1, 0.45, 22)
    coords_nearest = g.map_nearest(point)
    assert coords_nearest == (9, 6, 7)
    idx = g.idx(coords_nearest)
    assert idx == 1417
    coords_idx = g.coords_idx(idx)
    assert coords_idx == coords_nearest

    print 'point:', point
    print 'nearest gridpoint:', g.coords(coords_idx)
