# Floodfill

Floodfill finds minimum potential paths connecting
minima on multidimensional potential surfaces

    from floodfill.gridFunc import GridFunc 
    from floodfill.flooder import Flooder

    gf = GridFunc.from_vreco('data/V.final.out')

    gf.shape
    # (241, 101)
