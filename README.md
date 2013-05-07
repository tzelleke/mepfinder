# Floodfill

Floodfill finds minimum (free) energy paths connecting
minima on multidimensional (free) energy surfaces

## Example

The example data can be found in the `data/` dir.

Import `GridFunc` and `Flooder`

    from floodfill.gridFunc import GridFunc 
    from floodfill.flooder import Flooder

Use the `vreco` tool to generate `V.final.out`
which contains the grid and the potential
Initialize a `GridFunc` from `V.final.out`.

    gf = GridFunc.from_vreco('data/V.final.out')

In this example the grid is 2D and contains 241 grid points
in the first dimension and 101 in the second.

    gf.shape
    # (241, 101)

Next, you need to specify the two points between you like
to find a path.

    p1 = gf.g_minimize(None,
                       (None, 0.5))
    print p1
    # (58, 25)
    
    p2 = gf.g_minimize(None,
                   (0.5, None))
    print p2
    # (87, 68)

Initialize a `Flooder` based on the `GridFunc`

    flooder = Flooder(gf)

Find the minimum energy path connecting `p1` and `p2`

    path = flooder.flood(p1, p2)
