# wedge (Basic, 10 variants)

Solver `rhoCentralFoam`, turbulence laminar.

## Baseline prompt (variant 1)

> Perform a 2D supersonic flow simulation over a wedge. Create a 3D geometry spanning from -0.15242 m to 0.3048 m in the x-direction, 0 m to 0.1524 m in the y-direction, and -0.005 m to 0.005 m in the z-direction. The simulation starts at 0.0 seconds and runs until 0.2 seconds with a time step (deltaT) of 0.0001 seconds. The results are written every 0.02 seconds. The inlet velocity is 5 m/s, inlet temperature is 1 K and inlet pressure is 1 Pa. The wedge boundary uses slip boundary condition for velocity. Use normalized thermodynamic properties where molWeight is set to 11640.3, Cp is 2.5, Pr is 1.0, and dynamic viscosity mu is 0. This corresponds to a gas constant R of 0.7143 and a specific heat ratio of 1.4. Use rhoCentralFoam solver. Do not use more than 4800 cells in your mesh.

## Variants

| Variant | Prompt change vs 1 | Files that differ from variant 1 |
|---|---|---|
| [1](1.md) | baseline | - |
| [2](2.md) | `5` -> `10` | `0/U` |
| [3](3.md) | `5` -> `10`; `1` -> `2` | `0/U`, `0/T` |
| [4](4.md) | `5` -> `10`; `1` -> `3` | `0/U`, `0/T` |
| [5](5.md) | `0.0001` -> `0.00005`; `5` -> `15`; `1` -> `3` | `0/U`, `0/T`, `system/controlDict` |
| [6](6.md) | `0.0001` -> `0.00005`; `5` -> `15`; `1` -> `2` | `0/U`, `0/T`, `system/controlDict` |
| [7](7.md) | `0.0001` -> `0.00005`; `5` -> `15`; `1` -> `2`; `1.0,` -> `0.71,` | `constant/thermophysicalProperties`, `0/U`, `0/T`, `system/controlDict` |
| [8](8.md) | `0.0001` -> `0.00005`; `5` -> `20`; `1` -> `3`; `1.0,` -> `0.71,` | `constant/thermophysicalProperties`, `0/U`, `0/T`, `system/controlDict` |
| [9](9.md) | `0.0001` -> `0.00005`; `5` -> `20`; `1` -> `3` | `constant/thermophysicalProperties`, `0/U`, `0/T`, `system/controlDict` |
| [10](10.md) | `0.0001` -> `0.00005`; `5` -> `20`; `1` -> `3`; `1.0,` -> `1.5,` | `constant/thermophysicalProperties`, `0/U`, `0/T`, `system/controlDict` |

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
