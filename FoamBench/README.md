# FoamBench

FoamBench measures how well an LLM agent can set up and run an OpenFOAM
simulation from a natural-language request. Every case is a prompt plus a
reference OpenFOAM case; the agent's case is scored on whether it runs, how
closely its files match the reference, and how closely its final flow field
matches the reference solution.

The reference cases target **OpenFOAM v2412 (openfoam.com)**. They were
ported from the OpenFOAM v10 (openfoam.org) cases used in the paper; see
[PORTING_NOTES.md](PORTING_NOTES.md) for every change. The original v10
datasets are kept in `Dataset/v10/`. Published results (paper and the
[V2 page](https://nithinsomu.github.io/cfdllmbench_v2/)) were obtained with
OpenFOAM v10 and are not directly comparable with scores measured on this
port.

## Dataset

| Split | Cases | Content |
|---|---|---|
| Basic | 110 | 11 flow families derived from OpenFOAM tutorials, 10 variants each (boundary values, viscosity, temperatures, ...) |
| Advanced | 16 | new geometries (diamond, rectangle, two squares, nozzle) and turbulence-model variants (Spalart-Allmaras, k-omega SST, LES) |

| Family | Solver | Variants change |
|---|---|---|
| BernardCells | buoyantBoussinesqPimpleFoam | floor / ceiling temperature |
| Cavity | pisoFoam (k-epsilon) | lid velocity, viscosity |
| Cylinder | pimpleFoam (Cross-Power-Law) | inlet velocity, viscosity |
| counterFlowFlame2D | reactingFoam | fuel / air inlet velocity |
| damBreakWithObstacle | interFoam | phase viscosities |
| forwardStep | rhoCentralFoam | inlet velocity |
| obliqueShock | rhoCentralFoam | inlet / top velocity and temperature |
| pitzDaily | pimpleFoam (k-epsilon) | inlet velocity, viscosity |
| shallowWaterWithSquareBump | shallowWaterFoam | water depth |
| squareBend | rhoSimpleFoam (k-epsilon) | inlet temperature, viscosity, Prandtl number, time step |
| wedge | rhoCentralFoam | inlet velocity, temperature, Prandtl number, time step |

Each case in `Dataset/FoamBench_basic.json` / `Dataset/FoamBench_advanced.json`
is a dictionary `{"usr_requirement": <prompt>, "Allrun": ..., "0/U": ...,
"system/controlDict": ..., ...}`. A readable version of every case, with the
differences between variants, is under [`Dataset/md/`](Dataset/md/README.md).

## Layout

```
FoamBench/
├── Dataset/
│   ├── FoamBench_basic.json       110 Basic cases (OpenFOAM v2412)
│   ├── FoamBench_advanced.json    16 Advanced cases (OpenFOAM v2412)
│   ├── md/                        one Markdown page per case (generated)
│   ├── v10/                       original OpenFOAM v10 datasets
│   ├── Basic/<family>/<n>/        unpacked cases (read_json.py)
│   │   ├── usr_requirement.txt    the prompt
│   │   ├── GT_Files/              reference case
│   │   └── generated/             the framework's case goes here
│   └── Advanced/<case>/           same layout
├── tools/
│   ├── port_v10_to_v2412.py       v10 -> v2412 converter (regenerates the JSON files)
│   └── json_to_markdown.py        JSON -> Dataset/md
├── algorithm/example/             how to plug a framework in (Foam-Agent style)
├── foambench_common.py            shared helpers
├── read_json.py                   unpack the JSON datasets
├── check_env.py                   verify OpenFOAM + Python environment
├── run_gt_cases.py                run all reference cases (needed for NMSE)
├── run_benchmarks.py              example driver for MetaOpenFOAM
├── execution_report.py            M_exec
├── similarity_report.py           M_struct, M_file
├── nmse_report.py                 M_NMSE
├── score_calculation.py           final scores
├── results/                       CSV outputs
├── logs/                          run logs
├── Dockerfile                     OpenFOAM v2412 image with the scripts
└── requirements.txt
```

## Prerequisites

- OpenFOAM v2412 from openfoam.com. On WSL2 / Ubuntu:

  ```bash
  curl https://dl.openfoam.com/add-debian-repo.sh | sudo bash
  sudo apt-get install openfoam2412-default
  source /usr/lib/openfoam/openfoam2412/etc/bashrc     # add to ~/.bashrc
  ```

  Keep the repository on the Linux filesystem (for example `~/cfdllmbench`),
  not under `/mnt/c`.

- Python 3.9+ with `pip install -r requirements.txt` (numpy, pandas, pyvista,
  rouge-score, PyYAML). A virtual environment is recommended:

  ```bash
  python3 -m venv ~/foambench-venv && source ~/foambench-venv/bin/activate
  pip install -r requirements.txt
  ```

- `python3 check_env.py` reports anything missing.

## Running the benchmark

All commands run from this directory with the OpenFOAM environment sourced.

1. Unpack the datasets and run the reference cases once (the NMSE metric needs
   reference results; about 1.2 CPU-hours in total, roughly 30 minutes on four cores):

   ```bash
   python3 read_json.py
   python3 run_gt_cases.py -j 4
   ```

   `results/gt_run_v2412.csv` lists the outcome and run time of every case.

2. Run your framework on every case. For each case the framework gets
   `usr_requirement.txt` (the prompt) and must leave its complete OpenFOAM
   case, including the `log.*` files of the tools it ran, under
   `<case>/generated/` (another sub-directory name also works, but `generated`
   is preferred). `run_benchmarks.py` does this for MetaOpenFOAM;
   `algorithm/example/foambench_main.py` shows the Foam-Agent interface. A
   minimal loop for any framework:

   ```bash
   for case in Dataset/Basic/*/* Dataset/Advanced/*; do
       my_framework --prompt "$case/usr_requirement.txt" --output "$case/generated"
   done
   ```

3. Score:

   ```bash
   python3 execution_report.py     # results/{basic,advanced}_success_report.csv
   python3 similarity_report.py    # results/similarity_report_{basic,advanced}.csv
   python3 nmse_report.py          # results/{basic,advanced}_nmse_report.csv
   python3 score_calculation.py    # results/final_benchmark_scores.csv, per_case_scores.csv
   ```

   `python3 nmse_report.py --self-check` compares every reference case with
   itself (NMSE 0, written to `results/*_nmse_selfcheck.csv`) and is a quick
   test of the pipeline.

## Metrics

| Metric | Definition |
|---|---|
| `M_exec` | 1 if the solver log of the generated case (`log.<application>` from its `controlDict`, or any `log.*Foam`) ends with `End` |
| `M_struct` | share of reference files (under `0/`, `constant/`, `system/`) that exist at the same relative path in the generated case, averaged over the three directories |
| `M_file` | mean ROUGE-L F-measure between reference and generated file text (comments and banner removed); a missing file counts 0. The reference files are `GT_Files` as left by `run_gt_cases.py` (fields rewritten by setFields / subsetMesh on both sides, as in the original benchmark); `similarity_report.py --pristine` uses the untouched JSON content instead |
| `M_NMSE` | NMSE of the fields `U`, `p`, `rho`, `T` (those present in both) at the last reference time, mean over fields; 1 if NMSE < 0.1, 0.5 if NMSE < 0.3, else 0. If the cell counts differ, the generated field is sampled at the reference cell centres; a case that wrote no solution scores 0 |
| Success Ratio | share of cases with `M_exec` = 1 and `M_NMSE` = 1 |

## Regenerating the datasets

```bash
python3 tools/port_v10_to_v2412.py --src Dataset/v10 --dst Dataset --report results/port_report.json
python3 tools/json_to_markdown.py --dataset Dataset --out Dataset/md --clean
```

## Docker

```bash
docker build -t foam-bench .          # from this directory
docker run -it --rm foam-bench        # OpenFOAM v2412 is sourced in the shell
```
