# squareBend (Basic, 10 variants)

Solver `rhoSimpleFoam`, turbulence RAS kEpsilon.

## Baseline prompt (variant 1)

> Conduct a 3D squarebend flow simulation using OpenFOAM. The computational domain includes multiple regions, with vertices defined as inlet points at (-50, 25, 25) and (-50, 25, -25), outlet points at (-500, -75, 25) and (-500, -75, -25), and mid-bend points like (25, 0, 25) and (25, 0, -25). Follow the same geometry as the tutorial. Use a start time of 0 seconds, an end time of 500 seconds, a time step of 1 second, and write results every 100 seconds. Use a massflow rate inlet of 0.5. Outlet is pressureInletOutletVelocity. Temperature has an inlet value of 1000. Pressure is fixed at 110000 Pa at the outlet (zero-gradient at the inlet), and the domain is initialised to 110000 Pa. use kepsilon turbulence model. Use rhoSimpleFoam solver. Use Pr value of 0.71. Use mu value of 1.82e-5. Do not use more than 120000 cells in your mesh.

## Variants

| Variant | Prompt change vs 1 | Files that differ from variant 1 |
|---|---|---|
| [1](1.md) | baseline | - |
| [2](2.md) | `1000.` -> `1500.` | `0/T` |
| [3](3.md) | `0.71.` -> `1.0.` | `constant/thermophysicalProperties` |
| [4](4.md) | `1.82e-5.` -> `2.5e-5.` | `constant/thermophysicalProperties` |
| [5](5.md) | `0.71.` -> `1.0.`; `1.82e-5.` -> `2.5e-5.` | `constant/thermophysicalProperties` |
| [6](6.md) | `1000.` -> `1100.`; `0.71.` -> `1.0.`; `1.82e-5.` -> `2.5e-5.` | `constant/thermophysicalProperties`, `0/T` |
| [7](7.md) | `1` -> `0.5`; `1000.` -> `1100.`; `1.82e-5.` -> `5.0e-5.` | `constant/thermophysicalProperties`, `0/T`, `system/controlDict` |
| [8](8.md) | `1` -> `0.5`; `1.82e-5.` -> `5.0e-5.` | `constant/thermophysicalProperties`, `system/controlDict` |
| [9](9.md) | `1` -> `0.5`; `1.82e-5.` -> `1e-4.` | `constant/thermophysicalProperties`, `system/controlDict` |
| [10](10.md) | `1` -> `0.5`; `0.71.` -> `1.0.`; `1.82e-5.` -> `1e-4.` | `constant/thermophysicalProperties`, `system/controlDict` |

## Reference files (variant 1)

- `Allrun`
- `constant/turbulenceProperties`
- `constant/thermophysicalProperties`
- `0/p`
- `0/epsilon`
- `0/k`
- `0/U`
- `0/nut`
- `0/T`
- `0/alphat`
- `system/fvSolution`
- `system/controlDict`
- `system/decomposeParDict`
- `system/fvSchemes`
- `system/blockMeshDict`
