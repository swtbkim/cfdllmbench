# Cylinder (Basic, 10 variants)

Solver `pimpleFoam`, turbulence laminar (generalizedNewtonian).

## Baseline prompt (variant 1)

> do a laminar offsetcylinder simulation. Use PIMPLE algorithm with a generalized Newtonian model and Cross-Power-Law viscosity for momentum transport, characterized by specific parameters nuInf=10, m=0.4, n=3. Boundary conditions specify a fixed velocity of 1m/s at the inlet (left),fixed-value pressure of 0 at the outlet (right) with zero-gradient velocity there, and no-slip conditions for walls, including the cylinder surface. Use timestep of 0.0025 and output every 0.05. Finaltime is 0.5. use a Newtonian transport model with nu value of 0.01 in transportProperties. Do not use more than 1800 cells in your mesh.

## Variants

| Variant | Prompt change vs 1 | Files that differ from variant 1 |
|---|---|---|
| [1](1.md) | baseline | - |
| [2](2.md) | `1m/s` -> `1.5m/s`; `0.01` -> `1e-03` | `constant/transportProperties`, `0/U` |
| [3](3.md) | `1m/s` -> `1.5m/s`; `0.01` -> `1e-02` | `constant/transportProperties`, `0/U` |
| [4](4.md) | `1m/s` -> `1.5m/s`; `0.01` -> `1e-01` | `constant/transportProperties`, `0/U` |
| [5](5.md) | `1m/s` -> `2m/s`; `0.01` -> `1e-03` | `constant/transportProperties`, `0/U` |
| [6](6.md) | `1m/s` -> `2m/s`; `0.01` -> `1e-02` | `constant/transportProperties`, `0/U` |
| [7](7.md) | `1m/s` -> `2m/s`; `0.01` -> `1e-01` | `constant/transportProperties`, `0/U` |
| [8](8.md) | `1m/s` -> `3m/s`; `0.01` -> `1e-03` | `constant/transportProperties`, `0/U` |
| [9](9.md) | `1m/s` -> `3m/s`; `0.01` -> `1e-02` | `constant/transportProperties`, `0/U` |
| [10](10.md) | `1m/s` -> `3m/s`; `0.01` -> `1e-01` | `constant/transportProperties`, `0/U` |

## Reference files (variant 1)

- `Allrun`
- `constant/turbulenceProperties`
- `constant/transportProperties`
- `0/p`
- `0/U`
- `system/fvSolution`
- `system/controlDict`
- `system/fvSchemes`
- `system/blockMeshDict`
