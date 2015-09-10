"""
@author: tzelleke
"""

from numpy import mgrid, argmin

import input_parser
import vreco
import grid_func
import flooder
import plot


def _filter_min(pot, coords_idx, slices):
    min_idx = argmin(pot[slices])
    p_coords_idx = []
    for i in range(len(pot.shape)):
        idx = coords_idx[[i] + slices].ravel()[min_idx]
        p_coords_idx.append(idx)

    return p_coords_idx


def _filter_min_points(slice_gen_set, grid_vecs, pot):
    coords_idx = mgrid[map(slice, pot.shape)]
    points = []
    for slice_gens in slice_gen_set:
        slices = [gen(vec) for gen, vec in zip(slice_gens, grid_vecs)]
        point = _filter_min(pot, coords_idx, slices)
        points.append(point)

    return points


def _floodfill(colvar, parvar, ngridpoints, endpoints):
    points_parser = input_parser.gen_points_parser()
    slices_gen_set = points_parser.parseString(endpoints)

    v = vreco.Vreco(colvar, parvar)
    pot, grid_vecs = v.pot(ngridpoints)

    gf = grid_func.GridFunc.from_grid_vecs(pot, grid_vecs)

    p0, p1 = _filter_min_points(slices_gen_set, grid_vecs, pot)[:2]
    print p0, p1
    p0 = gf.minimize(p0)
    p1 = gf.minimize(p1)
    print p0, p1

    flooder_ = flooder.Flooder(gf)
    path_coords, path_pot = flooder_.flood(p0, p1)

    for i in range(len(path_pot)):
        print path_pot[i], path_coords[i]

    canvas = plot.produce_profile_plot(path_coords, path_pot)
    canvas.print_figure('test.png')
    print 'finished'


if __name__ == '__main__':
    from input_parser import gen_args_parser

    args_parser = gen_args_parser()
    args = args_parser.parse_args()
    _floodfill(args.colvar,
               args.parvar,
               args.ngridpoints,
               args.endpoints)
