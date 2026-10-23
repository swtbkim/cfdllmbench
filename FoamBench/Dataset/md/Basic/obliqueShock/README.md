# obliqueShock (Basic, 10 variants)

Solver `rhoCentralFoam`, turbulence laminar.

## Baseline prompt (variant 1)

> do a 2D oblique shock wave simulation using OpenFOAM with the rhoCentralFoam solver. The computational domain spans 4.1 m x 1.0 m x 0.1 m. Mesh it uniformly with 60 x 30 x 1 cells (60 in x, 30 in y, 1 in z). Use inlet velocity of 2.9 m/s and top velocity of (2.61933,-0.50632,0.0) m/s. Use an inlet temperature of 1.0 K and top boundary temperature of 1.25853 K, and an inlet pressure of 1.0 Pa. Use normalized thermodynamic properties where molWeight is set to 11640.3, Cp is 2.5, Pr is 1.0, and dynamic viscosity mu is 0. This corresponds to a gas constant R of 0.7143 and a specific heat ratio of 1.4. Use a time step of 0.0025 seconds, output results every 1.0 seconds, and run the simulation until a final time of 10 seconds.

## Variants

| Variant | Prompt change vs 1 | Files that differ from variant 1 |
|---|---|---|
| [1](1.md) | baseline | - |
| [2](2.md) | `(2.61933,-0.50632,0.0)` -> `(3.0,-0.50632,0.0)` | `0/U` |
| [3](3.md) | `2.9` -> `3.5` | `0/U` |
| [4](4.md) | `1.25853` -> `2.0` | `0/T` |
| [5](5.md) | `2.9` -> `3.5`; `1.25853` -> `2.0` | `0/U`, `0/T` |
| [6](6.md) | `(2.61933,-0.50632,0.0)` -> `(3.0,-0.50632,0.0)`; `1.0` -> `2.0` | `0/U`, `0/T` |
| [7](7.md) | `2.9` -> `4.0`; `(2.61933,-0.50632,0.0)` -> `(3.5,-0.50632,0.0)` | `0/U` |
| [8](8.md) | `2.9` -> `4.0`; `(2.61933,-0.50632,0.0)` -> `(3.5,-0.50632,0.0)`; `1.25853` -> `2.0` | `0/U`, `0/T` |
| [9](9.md) | `2.9` -> `4.0`; `(2.61933,-0.50632,0.0)` -> `(3.5,-0.50632,0.0)`; `1.0` -> `2.0`; `1.25853` -> `2.0` | `0/U`, `0/T` |
| [10](10.md) | `2.9` -> `4.0`; `(2.61933,-0.50632,0.0)` -> `(4.0,-0.50632,0.0)`; `1.0` -> `2.0`; `1.25853` -> `2.0` | `0/U`, `0/T` |

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
