# Cavity (Basic, 10 variants)

Solver `pisoFoam`, turbulence RAS kEpsilon.

## Baseline prompt (variant 1)

> do an incompressible lid driven cavity flow using pisoFoam. The cavity is a square with dimensions normalized to 1 unit on both the x and y axes and very thin in the z-direction (0.1 units) and entire domain scaled down by a factor of 0.1 making it effectively 2D. Use a grid of 20X20 in x and y direction and 1 cell in z-direction(due to the expected 2D flow characteristics). The top wall ('movingWall') moves in the x-direction with a uniform velocity of 1 m/s. The 'fixedWalls' have a no-slip boundary condition (velocity equal to zero at the wall). The front and back faces are designated as 'empty'. The simulation runs from time 0 to 10 with a time step of 0.005 units, and results are output every 100 time steps. The viscosity (`nu`) is set as constant with a value of 1e-05 m^2/s. Model turbulence with the standard k-epsilon RAS model (simulationType RAS, RASModel kEpsilon), with uniform initial values k = 0.00375 m^2/s^2 and epsilon = 0.00754 m^2/s^3, nut initialised to 0, and standard wall functions on movingWall and fixedWalls (kqRWallFunction for k, epsilonWallFunction for epsilon, nutkWallFunction for nut).

## Variants

| Variant | Prompt change vs 1 | Files that differ from variant 1 |
|---|---|---|
| [1](1.md) | baseline | - |
| [2](2.md) | `1 m/s.` -> `1.5m/s.` | `0/U` |
| [3](3.md) | `1 m/s.` -> `1.5m/s.`; `simulation` -> `simulations`; `1e-05` -> `1e-04` | `constant/transportProperties`, `0/U` |
| [4](4.md) | `1 m/s.` -> `1.5m/s.`; `1e-05` -> `1e-03` | `constant/transportProperties`, `0/U` |
| [5](5.md) | `1 m/s.` -> `2m/s.` | `0/U` |
| [6](6.md) | `1 m/s.` -> `2m/s.`; `(`nu`)` -> `(nu`)`; `1e-05` -> `1e-04` | `constant/transportProperties`, `0/U` |
| [7](7.md) | `1 m/s.` -> `2m/s.`; `1e-05` -> `1e-03` | `constant/transportProperties`, `0/U` |
| [8](8.md) | `1 m/s.` -> `3m/s.` | `0/U` |
| [9](9.md) | `1 m/s.` -> `3m/s.`; `1e-05` -> `1e-04` | `constant/transportProperties`, `0/U` |
| [10](10.md) | `1 m/s.` -> `3m/s.`; `1e-05` -> `1e-03` | `constant/transportProperties`, `0/U` |

## Reference files (variant 1)

- `Allrun`
- `constant/turbulenceProperties`
- `constant/transportProperties`
- `0/nuTilda`
- `0/p`
- `0/epsilon`
- `0/k`
- `0/U`
- `0/nut`
- `0/omega`
- `system/fvSolution`
- `system/controlDict`
- `system/fvSchemes`
- `system/blockMeshDict`
