__author__ = 'tzelleke'

from functools import partial

from grid_func import GridFunc
from flooder import Flooder


def _point_callback(gf, point_spec):
    if 'coords' in point_spec:
        coords = point_spec['coords']
        if 'min' in point_spec and point_spec['min'] is True:
            return gf.minimize(coords)
        else:
            return gf.map_nearest(coords)
    if 'range' in point_spec:
        return gf.g_minimize(point_spec['range'])
    raise RuntimeError('Unknown point_spec')


def _evaluate_path(gf, points):
    pass


# surface: /path/to/surface-file
# smooth:
#   - sigma: 4.5
#     cval: 0
#     save: true
#   - sigma: 3.4
#     save: false
#   - sigma: 20.0
# points:
#   - coords: [2.3, 4.5]
#     min: true
#   - range: [[null,4], [3.5,null]]
def main(config):
    points = []
    unsmoothed_gf = GridFunc.from_file(config['surface'])
    surfaces = [unsmoothed_gf]
    for point_spec in config['points']:
        points.append(partial(_point_callback, point_spec=point_spec))
    for smooth_spec in config['smooth']:
        sigma = smooth_spec['sigma']
        cval = smooth_spec['cval'] if 'cval' in smooth_spec else 0.
        smoothed_gf = unsmoothed_gf.smooth(sigma, cval, copy=True)
        surfaces.append(smoothed_gf)
        if 'save' in smooth_spec and smooth_spec['save'] is True:
            pass  # TODO build filename from smooth_spec


if __name__ == '__main__':
    pass
