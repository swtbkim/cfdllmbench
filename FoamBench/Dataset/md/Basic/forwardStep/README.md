# forwardStep (Basic, 10 variants)

Solver `rhoCentralFoam`, turbulence laminar.

## Baseline prompt (variant 1)

> do a laminar, compressible flow over a forward-facing step using the rhoCentralFoam solver. Boundary conditions include a fixed velocity of 4m/s and temperature of 1 K at the inlet and slip conditions on the obstacle. Use timestep of 0.002 and output every 0.1. Finaltime is 4. Do not use more than 17000 cells in your mesh.

## Variants

| Variant | Prompt change vs 1 | Files that differ from variant 1 |
|---|---|---|
| [1](1.md) | baseline | - |
| [2](2.md) | `4m/s` -> `1.1m/s` | `0/U` |
| [3](3.md) | `4m/s` -> `1.3m/s` | `0/U` |
| [4](4.md) | `4m/s` -> `1.5m/s` | `0/U` |
| [5](5.md) | `4m/s` -> `1.7m/s` | `0/U` |
| [6](6.md) | `4m/s` -> `1.9m/s` | `0/U` |
| [7](7.md) | `4m/s` -> `2.1m/s` | `0/U` |
| [8](8.md) | `4m/s` -> `2.3m/s` | `0/U` |
| [9](9.md) | `4m/s` -> `2.5m/s` | `0/U` |
| [10](10.md) | `4m/s` -> `2.7m/s` | `0/U` |

## Reference files (variant 1)

- `Allrun`
- `constant/turbulenceProperties`
- `constant/thermophysicalProperties`
- `0/p`
- `0/U`
- `0/T`
- `system/fvSolution`
- `system/controlDict`
- `system/fvSchemes`
- `system/blockMeshDict`
