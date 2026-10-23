# counterFlowFlame2D (Basic, 10 variants)

Solver `reactingFoam`, turbulence laminar.

## Baseline prompt (variant 1)

> do a counterflow flame simulation using OpenFOAM reactingFoam solver, employing a compressible flow solver for detailed combustion modeling. Define the computational domain as a 2D rectangular region with a width of 0.02 meters and a height of 0.02 meters. Mesh it uniformly with 100 x 40 x 1 cells (100 across the width in x, 40 across the height in y, 1 in z). Use CH4, O2 and N2 as species. Include chemical kinetics using the reaction mechanism. velocity of fuel is 0.1 m/s and velocity of air is -0.1 m/s. Set the simulation runtime from 0 to 0.5 seconds with a write interval of 0.05 seconds and deltaT of 1e-6. Use adaptive time stepping with a maximum Courant number of 0.4, starting from deltaT = 1e-6 s

## Variants

| Variant | Prompt change vs 1 | Files that differ from variant 1 |
|---|---|---|
| [1](1.md) | baseline | - |
| [2](2.md) | `0.1` -> `0.2` | `0/U` |
| [3](3.md) | `-0.1` -> `-0.2` | `0/U` |
| [4](4.md) | `0.1` -> `0.3` | `0/U` |
| [5](5.md) | `0.1` -> `0.3`; `-0.1` -> `-0.2` | `0/U` |
| [6](6.md) | `0.1` -> `0.3`; `-0.1` -> `-0.3` | `0/U` |
| [7](7.md) | `0.1` -> `0.4` | `0/U` |
| [8](8.md) | `0.1` -> `0.4`; `-0.1` -> `-0.2` | `0/U` |
| [9](9.md) | `0.1` -> `0.4`; `-0.1` -> `-0.3` | `0/U` |
| [10](10.md) | `0.1` -> `0.4`; `-0.1` -> `-0.4` | `0/U` |

## Reference files (variant 1)

- `Allrun`
- `constant/combustionProperties`
- `constant/turbulenceProperties`
- `constant/chemistryProperties`
- `constant/thermophysicalProperties`
- `constant/thermo.compressibleGas`
- `constant/reactions`
- `0/Ydefault`
- `0/H2O`
- `0/p`
- `0/CH4`
- `0/Qdot`
- `0/CO2`
- `0/U`
- `0/T`
- `0/O2`
- `0/alphat`
- `0/N2`
- `system/fvSolution`
- `system/controlDict`
- `system/fvSchemes`
- `system/blockMeshDict`
