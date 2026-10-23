# damBreakWithObstacle (Basic, 10 variants)

Solver `interFoam`, turbulence laminar.

## Baseline prompt (variant 1)

> do a laminar dam break with obstacle simulation. use interFoam solver. The domain extent is 1x1x1. Use 32 grid points in all directions. The obstacle is a block occupying the box from (0.375, 0.375, 0) to (0.625, 0.625, 0.25) m; remove these cells from the mesh and treat the obstacle surface as a wall. At the start, water fills the box from (0, 0, 0) to (0.6, 0.1875, 0.75) m and air fills the rest of the domain; gravity is (0, 0, -9.81) m/s^2. Use density of air to be 1 kg/m3 and density of water to be 1000 kg/m3. Take the viscosity of air to be 1.48e-5 and viscosity of water to be 1e-6. The simulation runs from t=0s to t=0.1s with a timestep of 0.001s and a write interval of 0.02.

## Variants

| Variant | Prompt change vs 1 | Files that differ from variant 1 |
|---|---|---|
| [1](1.md) | baseline | - |
| [2](2.md) | `1.48e-5` -> `0.0001`; `1e-6.` -> `0.001.` | `constant/transportProperties` |
| [3](3.md) | `1.48e-5` -> `0.0001`; `1e-6.` -> `0.0001.` | `constant/transportProperties` |
| [4](4.md) | `1.48e-5` -> `0.0001`; `1e-6.` -> `1e-05.` | `constant/transportProperties` |
| [5](5.md) | `1.48e-5` -> `0.001`; `1e-6.` -> `0.001.` | `constant/transportProperties` |
| [6](6.md) | `1.48e-5` -> `0.001`; `1e-6.` -> `0.0001.` | `constant/transportProperties` |
| [7](7.md) | `1.48e-5` -> `0.001`; `1e-6.` -> `1e-05.` | `constant/transportProperties` |
| [8](8.md) | `1.48e-5` -> `1.48e-05`; `1e-6.` -> `0.001.` | `constant/transportProperties` |
| [9](9.md) | `1.48e-5` -> `1.48e-05`; `1e-6.` -> `0.0001.` | `constant/transportProperties` |
| [10](10.md) | `1.48e-5` -> `1.48e-05`; `1e-6.` -> `1e-05.` | `constant/transportProperties` |

## Reference files (variant 1)

- `Allrun`
- `constant/g`
- `constant/transportProperties`
- `constant/turbulenceProperties`
- `constant/dynamicMeshDict`
- `0/p_rgh`
- `0/U.orig`
- `0/k`
- `0/alpha.water.orig`
- `0/U`
- `0/nut`
- `0/omega`
- `0/alpha.water`
- `system/fvSolution`
- `system/controlDict`
- `system/topoSetDict`
- `system/decomposeParDict`
- `system/fvSchemes`
- `system/blockMeshDict`
- `system/setFieldsDict`
