# Porting FoamBench from OpenFOAM v10 to OpenFOAM v2412

The FoamBench reference cases shipped in `Dataset/FoamBench_basic.json` and
`Dataset/FoamBench_advanced.json` were written for OpenFOAM Foundation
version 10 (openfoam.org). This branch ports every reference case, the
prompts that name version-specific things, and the evaluation scripts to
OpenFOAM ESI **v2412** (openfoam.com), the version that installs with one
`apt` command on WSL2 / Ubuntu.

- The original v10 datasets are kept unchanged under `Dataset/v10/`.
- The port is produced by `tools/port_v10_to_v2412.py`; running it again on
  `Dataset/v10/` regenerates the v2412 JSON files byte for byte.
- Human-readable pages for every case live under `Dataset/md/` and are
  produced by `tools/json_to_markdown.py`.

## How the port was validated

OpenFOAM v2412 (`openfoam2412-default`, patch 260127) was installed in a
clean Ubuntu 24.04 container. First the original v10 reference cases were run
as they were, one representative per Basic family plus all 16 Advanced cases:
only `shallowWaterWithSquareBump` and the five Advanced cases that were already
in ESI v2012 format ran; everything else failed at start-up (missing
`transportProperties` / `thermophysicalProperties`, `buoyantFoam` not found,
`dynamicMeshDict` format, `#includeFunc` arguments, `refineMesh -dict` path).
Then every one of the 126 ported cases was run to completion with
`run_gt_cases.py` (about 1.2 CPU-hours in total); the per-case outcome and
run time are in `results/gt_run_v2412.csv`. The only case that failed on the
first pass was `squareBend/2` (negative temperature, see the corrections
below); after that change all 126 cases end with `End`.

## Mapping rules applied to every case

| Foundation v10 | ESI v2412 | Notes |
|---|---|---|
| banner `Website: https://openfoam.org`, `Version: 10` | `Website: www.openfoam.com`, `Version: v2412`, `version 2.0;` in `FoamFile` | cosmetic, but the file is what an agent sees as reference |
| `constant/momentumTransport` | `constant/turbulenceProperties` | `RAS { model X; }` -> `RAS { RASModel X; }`, `LES { model X; }` -> `LES { LESModel X; }` |
| `constant/physicalProperties` with `viscosityModel constant; nu ...` | `constant/transportProperties` with `transportModel Newtonian; nu ...` | unit suffix `nu 1e-05 [m^2/s]` and `nu [0 2 -1 0 0 0 0] 1e-05` normalised to `nu 1e-05` |
| `constant/physicalProperties` with `thermoType` | `constant/thermophysicalProperties` | content unchanged for pure mixtures |
| `laminar { model generalisedNewtonian; viscosityModel CrossPowerLaw; nuInf m n }` | `model generalizedNewtonian;` plus `tauStar 0;` | ESI spells the model with a z and reads `tauStar`; `tauStar 0` selects the same `nu = nuInf + (nu0 - nuInf)/(1 + (m*strainRate)^n)` law |
| `constant/phaseProperties` + `constant/physicalProperties.<phase>` | one `constant/transportProperties` with `phases`, per-phase `transportModel/nu/rho`, `sigma` | interFoam cases |
| `constant/dynamicMeshDict` with `topoChanger { type refiner; ... }` | `dynamicFvMesh dynamicRefineFvMesh;` with the same refinement controls, `unrefineLevel 10`, `correctFluxes` incl. `alphaPhi0.water`, `alphaPhiUn` | damBreakWithObstacle |
| `system/fvConstraints` with `limitPressure { minFactor; maxFactor; }` | `SIMPLE { pMinFactor; pMaxFactor; }` in `system/fvSolution` | squareBend; the file `fvConstraints` is removed |
| `#includeFunc patchAverage(patch=inlet, fields=(p U))` | `#includeFunc patchAverage(name=inlet,p,U)` | ESI's `#includeFunc` reads one word: no spaces inside the parentheses, the patch argument is `name` |
| `#includeFunc residuals(p_rgh)` | `#includeFunc solverInfo(p_rgh)` | |
| `#includeFunc streamlinesLine(...)` | explicit `streamLine` function-object dictionary in `controlDict` | vector arguments cannot be passed through `#includeFunc` in ESI |
| `#includeFunc Qdot` | removed | ESI `reactingFoam` creates and writes the `Qdot` field itself; `0/Qdot` is kept (read if present) |
| `system/functions` | removed | not read by either version; it duplicated the `controlDict` entries |
| `0/uniform/time` | removed | run-time artefact written by the solver, not an input |
| `solver incompressibleFluid;` in `controlDict`, `transportPredictionFirst` in `fvSolution` | removed | OpenFOAM-11/12 leftovers, ignored by v10, meaningless in ESI |
| `application buoyantFoam` (Boussinesq thermo) | `application buoyantBoussinesqPimpleFoam` with `transportProperties` (`nu beta TRef Pr Prt`), kinematic `p`/`p_rgh`, `alphatJayatillekeWallFunction` | BernardCells; v2412 ships the identical `heatTransfer/buoyantBoussinesqPimpleFoam/BenardCells` tutorial. ESI has no `eConst + Boussinesq` thermo, so `buoyantPimpleFoam` would also have required a change of energy variable |
| reactingFoam `mixture coefficientWilkeMultiComponentMixture`, `defaultSpecie`, `#include "thermo.compressibleGas"` | `mixture reactingMixture`, `inertSpecie`, `chemistryReader foamChemistryReader; foamChemistryFile; foamChemistryThermoFile` | counterFlowFlame2D |
| `species (...)` list inside `thermo.compressibleGas` | `elements` and `species` lists inside `reactions`; `elements` per specie in the thermo file | as in the ESI tutorial |
| reaction `type irreversibleArrhenius` | `type irreversibleArrheniusReaction` | |
| `chemistryProperties`: `#include "reactions"`, `EulerImplicitCoeffs { cTauChem 1; }`, `odeCoeffs { solver Rosenbrock43; }` | include removed, `equilibriumRateLimiter off;` added (mandatory in ESI), `Rosenbrock34` (valid name; block unused) | |
| `topoSetDict` `action delete` | `action subtract` | `delete` still works in v2412, `subtract` is the primary name |
| `subsetMesh ... -noFields` | option removed | not an ESI option |
| `topoSet -dict topoSetDict.1`, `refineMesh -dict refineMeshDict` | `-dict system/topoSetDict.1`, `-dict system/refineMeshDict` | ESI resolves `-dict` relative to the case |
| `refineMeshDict` directions `e1`, `e2` | `tan1`, `tan2` | |
| `div(phi,alpha) Gauss MPLIC` | `Gauss vanLeer` + `div(phirb,alpha) Gauss linear` + `cAlpha 1` | v2412 has no MPLIC scheme; this is the ESI `damBreakWithObstacle` tutorial setup |
| `0/U` `flowRateInletVelocity` with `profile turbulentBL` | `profile` entry removed | Foundation-only option; the prompt no longer mentions it |
| `0/p_rgh` `prghTotalPressure` with `psi none; gamma 1;` | entries removed | ignored by ESI |
| rhoCentralFoam `fvSolution` solver block `h` | renamed `e` | energy variable is `e`; block is unused when `mu = 0` |
| `div(phiv,hU) Gauss LUST un` | `Gauss LUST grad(hU)` | `un` was an undefined gradient-scheme name |

Advanced cases that were already in ESI v2012 format (`Diamond_Obstacle_*`,
`Rectangular_Obstacle_*`, `Double_Square_SA`) only received the header update
and the clean-ups listed below.

## Reference-case corrections beyond the version port

These were found while auditing every case and are documented here because
they change what the benchmark compares against.

| Case(s) | Problem | Change |
|---|---|---|
| `counterFlowFlame2D/9` | GT identical to variant 1 while the prompt asks for fuel 0.4 m/s and air -0.3 m/s | `0/U` set to the prompt values |
| `Cavity_SA`, `Cavity_geometry_1` | prompt prescribes nuTilda = 3e-05 in the domain and 0 (fixedValue) on the walls; GT had 0 and `zeroGradient` (model inert) | `0/nuTilda` set to the prompt values |
| `Cylinder_SA` | prompt prescribes nuTilda = 0.03 in the domain/inlet, 0 on walls; GT had 0 everywhere | `0/nuTilda` set to the prompt values |
| `nozzleFlow2D_SA` | prompt prescribes nuTilda = 1.7856e-05 in the domain/inlet, 0 on walls; GT had 0 and `zeroGradient` walls | `0/nuTilda` set to the prompt values |
| `Diamond_Obstacle_SA`, `Rectangular_Obstacle_SA`, `Double_Square_SA` | `0/nuTilda` used `nutkWallFunction` (a nut wall function) on the walls | standard SA wall condition `fixedValue 0` |
| `Rectangular_Obstacle_SA` | `0/nuTilda` names the empty patch `defaultfaces` while the mesh patch is `defaultFaces` | spelling fixed |
| `obliqueShock_KE`, `obliqueShock_LES` | prompt states `mu` = 1.6646e-4 (viscous, so the turbulence model acts) while the files had `mu 0` | `mu 1.6646e-4` |
| `obliqueShock_KE` | `kEpsilonCoeffs` entry spelled `sigmaK` (ignored by both versions; the keyword is `sigmak`) | spelling fixed |
| `squareBend/2` | with inlet T = 1500 K, rhoSimpleFoam v2412 aborts after four iterations with a negative temperature when `h` is relaxed with 0.9 | enthalpy relaxation factor 0.7 for this variant only (a steady SIMPLE solution does not depend on the relaxation factor; the other nine variants are unchanged) |
| `Double_Square_SA` | stray token `in` in `system/controlDict` | removed |
| five Advanced cases | unused `system/blockMeshDict1` (a different geometry in millimetres) | removed |
| `nozzleFlow2D_SA` | unused `0/data/ptrace`, `0/data/Ubulk` | removed |

Prompt edits (only where the prompt named something that does not exist in
ESI):

| Family | Old wording | New wording |
|---|---|---|
| BernardCells | `buoyantFoam` | `buoyantBoussinesqPimpleFoam` |
| Cavity | `model kEpsilon` | `RASModel kEpsilon` |
| Cylinder | `use constant viscosity model with nu value of ... in physical properties` | `use a Newtonian transport model with nu value of ... in transportProperties` |
| squareBend | `with turbulentBL profile` | removed |

## Things that differ numerically between the two versions

The port is syntactic; the following are known to make v2412 reference
solutions differ from v10 ones, which is why the reference results must be
regenerated with `run_gt_cases.py` on v2412 and never reused from v10:

- interFoam: geometric MPLIC advection replaced by vanLeer with interface
  compression, and ESI's own adaptive-refinement implementation.
- Spalart-Allmaras: ESI includes the `ft2` term and a `k()` estimate that
  feeds `nutkWallFunction`.
- reactingFoam: `reactingMixture` mixes transport properties linearly instead
  of Wilke's rule; the `EulerImplicit` chemistry solvers are different
  implementations.
- rhoSimpleFoam: the inlet profile `turbulentBL` is gone (uniform plug inlet).
- Wall functions and linear solvers have different defaults (blending,
  agglomeration), so even unchanged cases are not bit-identical.

## Evaluation scripts

| Script | Change |
|---|---|
| `read_json.py` (+ thin `read_json_basic.py` / `read_json_advanced.py` wrappers) | one script for both splits; no API key or personal path in the repository; `Allrun` made executable; MetaOpenFOAM YAML only with `--metaopenfoam-yaml` |
| `run_gt_cases.py` (new) | runs every reference case in parallel, writes `results/gt_run_<version>.csv` and `logs/` |
| `check_env.py` (new) | verifies the sourced OpenFOAM, the solvers the dataset needs and the Python modules |
| `execution_report.py` | looks at the generated case itself (not only its sub-directories); prefers `log.<application>`; column renamed to `Execution` to match `score_calculation.py` (the two scripts disagreed before) |
| `similarity_report.py` | every case gets a row (missing generated case = 0); column `CodeBLEU` renamed `RougeL` (it always was ROUGE-L) |
| `nmse_report.py` | no longer leaves `.foam` marker files inside the reference cases; failures are caught; `--self-check` compares each reference with itself |
| `score_calculation.py` | outer merge so that every case counts; writes `results/final_benchmark_scores.csv` and `results/per_case_scores.csv` |
| `run_benchmarks.py` | takes `WM_PROJECT_DIR` from the environment instead of overwriting it; one-time MetaOpenFOAM database build; output in `<case>/generated` |
| `foambench_common.py` (new) | shared case discovery and log checks |
| `Dockerfile` | `opencfd/openfoam-default:2412` base image |
| `.gitattributes` | LF line endings for every text file so a Windows clone still runs under WSL2 |

All reports are written to `results/`; the generated case of a framework is
expected in `<case>/generated` (any other sub-directory name still works, as
before).

## WSL2 notes

- Install with `curl https://dl.openfoam.com/add-debian-repo.sh | sudo bash`
  then `sudo apt-get install openfoam2412-default`; the environment is
  `source /usr/lib/openfoam/openfoam2412/etc/bashrc`.
- Keep the repository on the Linux filesystem (for example `~/cfdllmbench`),
  not under `/mnt/c`: OpenFOAM writes many small files and is several times
  slower on the Windows drive, and the executable bit of `Allrun` is not kept
  there.
- Clone with the repository's `.gitattributes` in effect (or `git config
  core.autocrlf false`) so that `Allrun` and the dictionaries keep LF line
  endings.
- pyvista reads OpenFOAM results without a display; no X server is needed.
