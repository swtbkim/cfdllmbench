# BernardCells (Basic, 10 variants)

Solver `buoyantBoussinesqPimpleFoam`, turbulence laminar.

## Baseline prompt (variant 1)

> Perform a 2D Bernard Cell simulation using OpenFOAM buoyantBoussinesqPimpleFoam solver. The computational domain spans 9 m x 1 m in x and y, meshed with 90 x 10 cells, with a single cell of 2 m thickness in z and empty front and back patches. The simulation begins at t=0 seconds and runs until t=1000 seconds with a time step of 1 second, and results are written at intervals of every 50 seconds. The bottom wall (floor) has a temperature of 301 K and the top wall (ceiling) has a temperature of 300 K; the side walls are adiabatic (zero-gradient temperature).

## Variants

| Variant | Prompt change vs 1 | Files that differ from variant 1 |
|---|---|---|
| [1](1.md) | baseline | - |
| [2](2.md) | `t=1000` -> `t = 1000`; `301` -> `305` | `0/T` |
| [3](3.md) | `t=1000` -> `t = 1000`; `301` -> `310` | `0/T` |
| [4](4.md) | `t=1000` -> `t = 1000`; `301` -> `315` | `0/T` |
| [5](5.md) | `t=1000` -> `t = 1000`; `301` -> `305`; `300` -> `295` | `0/T` |
| [6](6.md) | `t=1000` -> `t = 1000`; `301` -> `305`; `300` -> `290` | `0/T` |
| [7](7.md) | `t=1000` -> `t = 1000`; `301` -> `310`; `300` -> `295` | `0/T` |
| [8](8.md) | `t=1000` -> `t = 1000`; `301` -> `310`; `300` -> `290` | `0/T` |
| [9](9.md) | `t=1000` -> `t = 1000`; `301` -> `315`; `300` -> `295` | `0/T` |
| [10](10.md) | `t=1000` -> `t = 1000`; `301` -> `315`; `300` -> `290` | `0/T` |

## Reference files (variant 1)

- `Allrun`
- `constant/g`
- `constant/turbulenceProperties`
- `constant/transportProperties`
- `0/p_rgh`
- `0/p`
- `0/epsilon`
- `0/k`
- `0/U`
- `0/nut`
- `0/T`
- `0/alphat`
- `system/fvSolution`
- `system/controlDict`
- `system/fvSchemes`
- `system/blockMeshDict`
