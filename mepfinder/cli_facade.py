from docopt import docopt
from flooder import Flooder
from grid_func import GridFunc

_doc = """\
Usage: floodfill_vreco.py <v_final_out>
       floodfill_vreco.py <v_final_out> <p1> <p2>

"""

_split_bounds = lambda s: [_.split(':') for _ in s.split(',')]
_parse_bound = lambda b: [None if _ is '' else float(_) for _ in b]
_filter_none_list = lambda b: [None if len(_) == 1 and _[0] is None
                               else _ for _ in b]


def run():
    # argv = ['/home/tzelleke/git/MinEnergyPath/data/surface.txt', ',:0.5', ',0.5:']
    argv = docopt(_doc)
    gf = GridFunc.from_file(argv['<v_final_out>'])
    template = '{:8.4f}' * (len(gf.shape) + 1)

    if argv['<p1>'] and argv['<p2>']:
        p1 = _filter_none_list([_parse_bound(_) for _ in _split_bounds(argv['<p1>'])])
        p2 = _filter_none_list([_parse_bound(_) for _ in _split_bounds(argv['<p2>'])])

        p1 = gf.g_minimize(*p1)
        p2 = gf.g_minimize(*p2)

        flooder = Flooder(gf)
        path = flooder.flood(p1, p2)

        for p in path:
            print template.format(p.pot, *p.coords)
    else:
        pmin = gf.g_minimize()
        print 'global minimum'
        print template.format(gf.pot_1D[gf.idx(pmin)], *gf.coords(pmin))
