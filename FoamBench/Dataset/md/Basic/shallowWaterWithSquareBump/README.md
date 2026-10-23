# shallowWaterWithSquareBump (Basic, 10 variants)

Solver `shallowWaterFoam`, turbulence -.

## Baseline prompt (variant 1)

> do a shallow water simulation over a square bump using the shallowWaterFoam solver. The domain spans 1 x 1 x 0.1, discretized into 20 x 20 x 1 grid points. The simulation initializes with a uniform water depth of 0.01 m and a uniform momentum field of (0.001,0,0). The simulation runs from 0 s to 100 s with a timestep of 0.1 s and writes results every 1 s. The square bump occupies the box (0.45, 0.45) to (0.55, 0.55) with bed elevation h0 = 0.001 m; initialise the free surface flat and the velocity uniform, i.e. over the bump h = 0.009 m and hU = (0.0009, 0, 0), applied with setFields.

## Variants

| Variant | Prompt change vs 1 | Files that differ from variant 1 |
|---|---|---|
| [1](1.md) | baseline | - |
| [2](2.md) | `0.01` -> `0.02`; `0.009` -> `0.019`; `(0.0009,` -> `(0.00095,` | `0/hTotal`, `0/hU`, `0/h.orig`, `0/h`, `system/setFieldsDict` |
| [3](3.md) | `0.01` -> `0.03`; `0.009` -> `0.029`; `(0.0009,` -> `(0.000966667,` | `0/hTotal`, `0/hU`, `0/h.orig`, `0/h`, `system/setFieldsDict` |
| [4](4.md) | `0.01` -> `0.04`; `0.009` -> `0.039`; `(0.0009,` -> `(0.000975,` | `0/hTotal`, `0/hU`, `0/h.orig`, `0/h`, `system/setFieldsDict` |
| [5](5.md) | `0.01` -> `0.05`; `0.009` -> `0.049`; `(0.0009,` -> `(0.00098,` | `0/hTotal`, `0/hU`, `0/h.orig`, `0/h`, `system/setFieldsDict` |
| [6](6.md) | `0.01` -> `0.06`; `0.009` -> `0.059`; `(0.0009,` -> `(0.000983333,` | `0/hTotal`, `0/hU`, `0/h.orig`, `0/h`, `system/setFieldsDict` |
| [7](7.md) | `0.01` -> `0.07`; `0.009` -> `0.069`; `(0.0009,` -> `(0.000985714,` | `0/hTotal`, `0/hU`, `0/h.orig`, `0/h`, `system/setFieldsDict` |
| [8](8.md) | `0.01` -> `0.08`; `0.009` -> `0.079`; `(0.0009,` -> `(0.0009875,` | `0/hTotal`, `0/hU`, `0/h.orig`, `0/h`, `system/setFieldsDict` |
| [9](9.md) | `0.01` -> `0.09`; `0.009` -> `0.089`; `(0.0009,` -> `(0.000988889,` | `0/hTotal`, `0/hU`, `0/h.orig`, `0/h`, `system/setFieldsDict` |
| [10](10.md) | `0.01` -> `0.1`; `0.009` -> `0.099`; `(0.0009,` -> `(0.00099,` | `0/hTotal`, `0/hU`, `0/h.orig`, `0/h`, `system/setFieldsDict` |

## Reference files (variant 1)

- `Allrun`
- `constant/h0`
- `constant/h0.orig`
- `constant/gravitationalProperties`
- `0/hTotal`
- `0/hU`
- `0/h.orig`
- `0/h`
- `0/hU.orig`
- `system/fvSolution`
- `system/controlDict`
- `system/fvSchemes`
- `system/blockMeshDict`
- `system/setFieldsDict`
