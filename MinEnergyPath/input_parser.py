__author__ = 'tzelleke'

from argparse import ArgumentParser
from pyparsing import (nums, Word, Suppress,
                       Or, ZeroOrMore, delimitedList,
                       Empty, Group)
from numpy import searchsorted as ss
from numpy import argmin, abs


def gen_args_parser():
    parser = ArgumentParser()
    parser.add_argument("-c", dest='colvar', required=True,
                        help="path to colvar_mtd")
    parser.add_argument("-p", dest='parvar', required=True,
                        help="path to parvar_mtd")
    parser.add_argument("-n", dest='ngridpoints', required=True,
                        type=int, help="path to parvar_mtd")
    parser.add_argument("-m", dest='endpoints', required=True,
                        help="endpoints")
    return parser


def gen_points_parser():
    def _gen_slice(lb, ub):
        def g(grid_vec):
            _lb = ss(grid_vec, lb) if not lb is None else 0
            _ub = ss(grid_vec, ub) + 1 if not ub is None else None
            return slice(_lb, _ub)

        return g

    def _gen_point(p):
        def f(grid_vec):
            _p = argmin(abs(p - grid_vec))
            return slice(_p, _p + 1)

        return f

    lt = Suppress('<')
    colon = Suppress(':')
    lsqr = Suppress('[')
    rsqr = Suppress(']')

    number = Word(nums + '.').setParseAction(lambda t: float(t[0]))
    lbound = (number + lt)
    ubound = (lt + number)
    lubound = (lbound + ubound)
    cv = Or((lubound('lubound').setParseAction(lambda t: _gen_slice(t[0], t[1])),
             lbound('lbound').setParseAction(lambda t: _gen_slice(t[0], None)),
             ubound('ubound').setParseAction(lambda t: _gen_slice(None, t[0])),
             number('point').addParseAction(lambda t: _gen_point(t[0])),
             Empty().setParseAction(lambda t: _gen_slice(None, None))))
    point = Group(lsqr + delimitedList(cv) + rsqr)
    point_list = (point + ZeroOrMore(colon + point))
    return point_list


if __name__ == '__main__':
    points_parser = gen_points_parser()

    test = '[,4]:[4.5<,3<<5]'
    match = points_parser.parseString(test)
    print match
