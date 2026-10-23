# pitzDaily (Basic, 10 variants)

Solver `pimpleFoam`, turbulence RAS kEpsilon.

## Baseline prompt (variant 1)

> do a Reynolds-Averaged Simulation (RAS) pitzdaily simulation. Use PIMPLE algorithm. The domain is a 2D millimeter-scale channel geometry. Use the standard OpenFOAM pitzDaily geometry and mesh. Boundary conditions specify a fixed velocity of 10m/s at the inlet (left),fixed-value pressure of 0 at the outlet (right) with zero-gradient velocity there, and no-slip conditions for walls. Use timestep of 0.0001 and output every 0.01. Finaltime is 0.3. use nu value of 1e-5. Use the standard k-epsilon RAS model with k = 0.375 m^2/s^2 and epsilon = 14.855 m^2/s^3 at the inlet and as initial values, and standard wall functions (kqRWallFunction, epsilonWallFunction, nutkWallFunction) on upperWall and lowerWall. Do not use more than 13000 cells in your mesh.

## Variants

| Variant | Prompt change vs 1 | Files that differ from variant 1 |
|---|---|---|
| [1](1.md) | baseline | - |
| [2](2.md) | `10m/s` -> `15m/s`; `1e-5.` -> `1e-05.` | `0/U` |
| [3](3.md) | `10m/s` -> `15m/s`; `1e-5.` -> `1e-04.` | `constant/transportProperties`, `0/U` |
| [4](4.md) | `10m/s` -> `15m/s`; `1e-5.` -> `1e-03.` | `constant/transportProperties`, `0/U` |
| [5](5.md) | `10m/s` -> `20m/s`; `1e-5.` -> `1e-05.` | `0/U` |
| [6](6.md) | `10m/s` -> `20m/s`; `1e-5.` -> `1e-04.` | `constant/transportProperties`, `0/U` |
| [7](7.md) | `10m/s` -> `20m/s`; `1e-5.` -> `1e-03.` | `constant/transportProperties`, `0/U` |
| [8](8.md) | `10m/s` -> `25m/s`; `1e-5.` -> `1e-05.` | `0/U` |
| [9](9.md) | `10m/s` -> `25m/s`; `1e-5.` -> `1e-04.` | `constant/transportProperties`, `0/U` |
| [10](10.md) | `10m/s` -> `25m/s`; `1e-5.` -> `1e-03.` | `constant/transportProperties`, `0/U` |

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
- `system/fvSolution`
- `system/controlDict`
- `system/fvSchemes`
- `system/blockMeshDict`
