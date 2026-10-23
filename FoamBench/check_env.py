#!/usr/bin/env python3
"""Check that this machine can run and evaluate FoamBench on OpenFOAM v2412.

    source /usr/lib/openfoam/openfoam2412/etc/bashrc
    python3 check_env.py
"""

import importlib
import os
import shutil
import sys

SOLVERS = [
    "blockMesh", "setFields", "topoSet", "subsetMesh", "refineMesh",
    "pisoFoam", "pimpleFoam", "rhoCentralFoam", "rhoSimpleFoam", "interFoam",
    "reactingFoam", "buoyantBoussinesqPimpleFoam", "shallowWaterFoam",
]
PYTHON_MODULES = ["numpy", "pandas", "pyvista", "rouge_score"]


def main():
    ok = True
    wm = os.environ.get("WM_PROJECT_DIR", "")
    version = os.environ.get("WM_PROJECT_VERSION", "")
    if not wm:
        print("FAIL  WM_PROJECT_DIR is not set: source /usr/lib/openfoam/openfoam2412/etc/bashrc first")
        ok = False
    else:
        print(f"ok    WM_PROJECT_DIR={wm} (WM_PROJECT_VERSION={version})")
        if not version.startswith("v24"):
            print("warn  the reference cases were ported for OpenFOAM v2412 (openfoam.com); other versions may fail")
    for exe in SOLVERS:
        if shutil.which(exe):
            print(f"ok    {exe}")
        else:
            print(f"FAIL  {exe} not found in PATH")
            ok = False
    for mod in PYTHON_MODULES:
        try:
            importlib.import_module(mod)
            print(f"ok    python module {mod}")
        except ImportError:
            print(f"FAIL  python module {mod} missing (pip install -r requirements.txt)")
            ok = False
    cwd = os.getcwd()
    if cwd.startswith("/mnt/"):
        print("warn  the working directory is on a Windows drive (/mnt/...); OpenFOAM is much faster on the WSL2 Linux filesystem (e.g. ~/)")
    print("\nEnvironment OK" if ok else "\nEnvironment has problems (see FAIL lines)")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
