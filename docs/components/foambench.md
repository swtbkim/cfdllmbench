# FoamBench: OpenFOAM Automation

FoamBench evaluates end-to-end automation of OpenFOAM simulations from
natural-language instructions. An agent receives one prompt per case, must
write the complete OpenFOAM case (mesh, boundary conditions, physical
properties, numerics, run script), run it, and is scored against a reference
case prepared by CFD experts.

The reference cases target **OpenFOAM v2412 (openfoam.com)**. The datasets
used in the paper were written for OpenFOAM v10 (openfoam.org); they are kept
under `FoamBench/Dataset/v10/` and the port is described in
[`FoamBench/PORTING_NOTES.md`](https://github.com/NREL-Theseus/cfdllmbench/blob/main/FoamBench/PORTING_NOTES.md).

## Overview

- **126 cases**: 110 Basic + 16 Advanced
- **One prompt per case**: problem, geometry, solver, boundary conditions,
  physical parameters, time step and output interval
- **Reference OpenFOAM case per case**: `Allrun`, `0/`, `constant/`, `system/`
- **Real execution**: the agent's case is run with OpenFOAM and its final flow
  field is compared with the reference solution

## Basic split (110 cases)

Eleven flow families derived from OpenFOAM tutorials, each with ten variants
that change boundary values or physical parameters (and the matching reference
files) on a case-specific basis.

| Family | Solver | Physics |
|---|---|---|
| BernardCells | buoyantBoussinesqPimpleFoam | Rayleigh-Benard convection |
| Cavity | pisoFoam, k-epsilon | lid-driven cavity |
| Cylinder | pimpleFoam, Cross-Power-Law viscosity | laminar flow past an offset cylinder |
| counterFlowFlame2D | reactingFoam | laminar methane counter-flow flame |
| damBreakWithObstacle | interFoam | 3D two-phase dam break with adaptive refinement |
| forwardStep | rhoCentralFoam | supersonic flow over a forward step |
| obliqueShock | rhoCentralFoam | oblique shock reflection |
| pitzDaily | pimpleFoam, k-epsilon | backward-facing step |
| shallowWaterWithSquareBump | shallowWaterFoam | shallow water over a bump |
| squareBend | rhoSimpleFoam, k-epsilon | 3D compressible flow through a square bend |
| wedge | rhoCentralFoam | supersonic flow over a wedge |

## Advanced split (16 cases)

Hand-crafted cases that are not tutorials: new geometries (diamond, rectangle
and two square obstacles in a channel, a nozzle) and turbulence-model variants
(Spalart-Allmaras, k-omega SST, LES) of the Basic flows. The agent has to
choose the mesh topology and turbulence set-up from the prompt alone.

## Example prompt

> do an incompressible lid driven cavity flow using pisoFoam. The cavity is a
> square with dimensions normalized to 1 unit on both the x and y axes and very
> thin in the z-direction (0.1 units) and entire domain scaled down by a factor
> of 0.1 making it effectively 2D. Use a grid of 20X20 in x and y direction and
> 1 cell in z-direction. The top wall ('movingWall') moves in the x-direction
> with a uniform velocity of 1 m/s. [...] Model turbulence with the standard
> k-epsilon RAS model (simulationType RAS, RASModel kEpsilon), with uniform
> initial values k = 0.00375 m^2/s^2 and epsilon = 0.00754 m^2/s^3 [...]

Every case, with the differences between its variants, can be browsed under
[`FoamBench/Dataset/md/`](https://github.com/NREL-Theseus/cfdllmbench/blob/main/FoamBench/Dataset/md/README.md).

## Metrics

| Metric | Definition |
|---|---|
| `M_exec` | 1 if the solver log of the generated case ends with OpenFOAM's `End` line |
| `M_struct` | share of reference files (`0/`, `constant/`, `system/`) present at the same relative path in the generated case |
| `M_file` | mean ROUGE-L similarity between reference and generated file text |
| `M_NMSE` | normalised mean squared error of `U`, `p`, `rho`, `T` at the final time against the reference solution: 1 if NMSE < 0.1, 0.5 if NMSE < 0.3, else 0 |
| Success Ratio | share of cases with `M_exec` = 1 and `M_NMSE` = 1 |

## Running FoamBench

```bash
source /usr/lib/openfoam/openfoam2412/etc/bashrc
cd FoamBench
pip install -r requirements.txt
python3 check_env.py
python3 read_json.py            # unpack Dataset/Basic and Dataset/Advanced
python3 run_gt_cases.py -j 4    # run the reference cases once (needed for NMSE)
# ... run your framework; its case goes to <case>/generated ...
python3 execution_report.py
python3 similarity_report.py
python3 nmse_report.py
python3 score_calculation.py    # results/final_benchmark_scores.csv
```

See [`FoamBench/README.md`](https://github.com/NREL-Theseus/cfdllmbench/blob/main/FoamBench/README.md)
for the full description.

## Prerequisites

- OpenFOAM v2412 (`sudo apt-get install openfoam2412-default` after adding the
  openfoam.com repository); works on WSL2 when the repository is kept on the
  Linux filesystem
- Python 3.9+ with numpy, pandas, pyvista, rouge-score, PyYAML
- About 1.2 CPU-hours (30 minutes on four cores) to run the 126 reference cases once
