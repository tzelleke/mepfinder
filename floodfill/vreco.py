'''
@author: tzelleke
'''

import numpy as np


class Vreco(object):
    E_CONV = 627.5132632235
    BOHR_2_ANG = 0.52918

    def __init__(self, colvar_file, parvar_file):
        self.colvar_file = colvar_file
        self.parvar_file = parvar_file
        self.dim = 0
        self.ngaussians = 0
        self.g_coords = None
        self.g_scals = None
        self.g_width = None
        self.g_height = None
        self._parse()

    def _parse(self):
        _2D, _3D = (5, 6), (7, 8)
        colv = np.loadtxt(self.colvar_file)
        parv = np.loadtxt(self.parvar_file)
        if colv.shape[0] != parv.shape[0]:
            raise Exception('different length: colvar_mtd vs parvar_mtd')
        self.ngaussians = colv.shape[0]
        if colv.shape[1] in _3D:
            self.g_coords = colv[:, 1:4].copy()
            self.g_scals = colv[:, 4:7].copy()
            self.dim = 3
        elif colv.shape[1] in _2D:
            self.g_coords = colv[:, 1:3].copy()
            self.g_scals = colv[:, 3:5].copy()
            self.dim = 2
        else:
            raise Exception('failed to detect dimensionality')
        self.g_width = parv[:, 2].copy()
        self.g_height = parv[:, 3].copy()

    def _grid_points(self, npoints, pad_factor=0.1):
        g = self.g_coords
        grid_vecs = []
        base_shape = [1] * self.dim

        means = g.mean(axis=0)
        spreads = g.max(axis=0) - g.min(axis=0)
        padded_halves = (pad_factor + 0.5) * spreads

        # f = npoints / np.prod(spreads)
        # f = np.power(f, 1./self.dim)
        #        dim_points = np.ceil(f * spreads)
        f = np.ceil(np.power(npoints, 1. / self.dim))
        dim_points = f * np.ones(self.dim)

        upper_limits = means + padded_halves
        lower_limits = means - padded_halves
        for i in range(self.dim):
            vec = np.linspace(lower_limits[i],
                              upper_limits[i],
                              dim_points[i])
            shape = base_shape[:]
            shape[i] = dim_points[i]
            grid_vecs.append(vec.reshape(shape))
        return grid_vecs

    def pot(self, n_points):
        return self._pot2(n_points)

    def _pot_p(self, p):
        raise NotImplementedError()

    def _pot_grid(self, grid_vecs, idx):
        g_coords = self.g_coords[idx, :]
        g_scals = self.g_scals[idx, :]
        width = self.g_width[idx]
        height = self.g_height[idx]

        d = np.zeros([1] * self.dim)
        for i in range(self.dim):
            d_i = g_coords[i] - grid_vecs[i]
            d_i /= g_scals[i]
            d_i *= d_i
            d = d + d_i
        d /= (2 * width * width)
        return height * np.exp(-d)

    def _pot2(self, npoints):
        grid_vecs = self._grid_points(npoints)
        shape = [np.shape(gv)[i] for i, gv in enumerate(grid_vecs)]
        s = np.zeros(shape)
        for i in range(self.ngaussians):
            s += self._pot_grid(grid_vecs, i)
        pot = -self.E_CONV * s
        return [pot, [gv.ravel() for gv in grid_vecs]]

# def pot_p(self, p):
# x, y = p
#         g = self.gaussians
#         dist = (g[:, 1:3] - [x, y]) / g[:, 3:5]
#         denom = 2. * (g[:, 5] ** 2)
#         return np.sum(
#                       g[:, 6] * 
#                       np.exp(-np.sum(dist * dist, axis=1) / denom))


#     def _pot1(self, npoints):
#         [x_vec, y_vec] = self._grid_points(npoints)
#         calc = np.vectorize(self.pot_p)
#         pot = - self.E_CONV * calc(x_vec, y_vec)
#         return [pot, (x_vec.ravel(), y_vec.ravel())]


if __name__ == '__main__':
    v = Vreco('data/colvar_padmesh', 'data/parvar_padmesh')
    pot, grid_vecs = v.pot(4000)
    print np.min(pot)