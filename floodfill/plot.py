'''
@author: tzelleke
'''


from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.ticker import FixedLocator, FixedFormatter


def _path_to_1D(coords):
    return range(len(coords))


def produce_profile_plot(coords, pot):
    coords_1D = _path_to_1D(coords)
    
    fig = Figure()
    canvas = FigureCanvasAgg(fig)
    ax = fig.add_subplot('111')
    ax.set_xmargin(0.1)
    ax.set_ymargin(0.1)
    ax.plot(coords_1D, pot)
    ax.set_ylabel('Free Energy')
    ax.set_xlabel('Reaction Path')
    
    ax.xaxis.set_major_locator(FixedLocator([coords_1D[0],
                                             coords_1D[-1]]))
    ax.xaxis.set_major_formatter(FixedFormatter(['start', 'end']))
    ax.yaxis.set_major_locator(FixedLocator([pot[0],
                                             max(pot),
                                             pot[-1]]))
    ax.yaxis.grid(True)
    
    return canvas


if __name__ == '__main__':
    pot = [1,2.5,3.2,3.5,2.7,1.3]
    coords = [1,2,3,4,5,6]
    canvas = produce_profile_plot(coords, pot)
    canvas.print_figure('test.png')