__author__ = 'tzelleke'

import numpy as np
from heapq import heappush as hpush, heappop as hpop

from path import Point, Path


class EmptyHeapError(Exception):
    pass


class Flooder(object):
    def __init__(self, grid_func):
        self.gf = grid_func
        pot_1D = grid_func.pot_1D
        size = grid_func.nnodes
        self.sidx = np.argsort(pot_1D)
        self.inv_sidx = np.argsort(self.sidx)
        self.color = np.zeros(size, dtype=np.int)
        self.p_idx = np.zeros(size, dtype=np.int)
        self.heap = []

    def flood(self, p1, p2):
        idx1 = self.gf.idx(p1)
        idx2 = self.gf.idx(p2)
        self._flood_init(idx1, idx2)
        meeting_node_A, meeting_node_B = self._floodfill()
        path_idx = self._follow_path(meeting_node_A, meeting_node_B)

        path = Path()
        for idx in path_idx:
            coords_idx = self.gf.coords_idx(idx)
            coords = self.gf.coords(coords_idx)
            pot = self.gf.pot_1D[idx]
            has_nan_neighbor = False
            for neighbor in self.gf.neighbors_idx(idx):
                if np.isnan(self.gf.pot_1D[neighbor]):
                    has_nan_neighbor = True
                    break
            path.append(Point(coords_idx=coords_idx,
                              coords=coords,
                              pot=pot,
                              has_nan_neighbor=has_nan_neighbor))

        return path

    def _flood_init(self, idx1, idx2):
        self.heap = []
        self.color[:] = 0
        self.p_idx[:] = -1
        self.color[idx1] = 1
        self.color[idx2] = 2
        hpush(self.heap, self.inv_sidx[idx1])
        hpush(self.heap, self.inv_sidx[idx2])

    def _floodfill(self):
        other_color_nodes = []
        while not other_color_nodes:
            if not self.heap:
                raise EmptyHeapError()
            current_node = self.sidx[hpop(self.heap)]
            current_color = self.color[current_node]
            for node in self.gf.neighbors_idx(current_node):
                node_color = self.color[node]
                if node_color == current_color:
                    continue
                if node_color == 0:
                    self.color[node] = current_color
                    self.p_idx[node] = current_node
                    hpush(self.heap, self.inv_sidx[node])
                else:
                    other_color_nodes.append(self.inv_sidx[node])
        node = self.sidx[min(other_color_nodes)]
        node_color = self.color[node]
        if current_color < node_color:

            return (current_node, node)
        else:

            return (node, current_node)

    def _follow_path(self, meeting_node_A, meeting_node_B):
        path_idx = []

        path_idx.append(meeting_node_A)
        while self.p_idx[path_idx[-1]] > -1:
            path_idx.append(self.p_idx[path_idx[-1]])
        path_idx.reverse()

        path_idx.append(meeting_node_B)
        while self.p_idx[path_idx[-1]] > -1:
            path_idx.append(self.p_idx[path_idx[-1]])

        return path_idx


if __name__ == '__main__':
    from grid_func import GridFunc

    gf = GridFunc.from_file('../data/surface.txt')
    flooder = Flooder(gf)
    p1 = gf.g_minimize(None, (None, 0.5))
    p2 = gf.g_minimize(None, (0.5, None))
    path = flooder.flood(p1, p2)

    for p in path:
        print p
