#!/usr/bin/env python3
"""Run every reference (GT) case with the OpenFOAM installation in the environment.

The NMSE metric compares a framework's result against the reference solution, so
the reference cases must have been executed once on the same OpenFOAM version.
This script runs ``GT_Files/Allrun`` for every unpacked case, in parallel, and
writes a CSV summary plus one log per case.

    source /usr/lib/openfoam/openfoam2412/etc/bashrc
    python3 read_json.py
    python3 run_gt_cases.py -j 4                      # all 126 cases
    python3 run_gt_cases.py --only 'Cavity/' --only Cylinder_SA
    python3 run_gt_cases.py --clean                   # remove old results first

Outputs:
    results/gt_run_<WM_PROJECT_VERSION>.csv    Split, Dataset, Directory, Success, Seconds, Application, Error
    logs/gt_<split>_<case>.log                 stdout/stderr of Allrun
"""

import argparse
import csv
import os
import re
import shutil
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

from foambench_common import (
    DATASET_DIR, LOGS_DIR, RESULTS_DIR, application_of, ensure_dirs, gt_dir,
    iter_cases, openfoam_env, solver_log_success,
)

TIME_DIR_RE = re.compile(r"^[0-9]+(\.[0-9]+)?([eE][-+]?[0-9]+)?$")


def clean_case(case_root):
    """Remove results of a previous run (time directories, logs, polyMesh, postProcessing)."""
    for name in os.listdir(case_root):
        path = os.path.join(case_root, name)
        if os.path.isfile(path) and (name.startswith("log.") or name.endswith(".foam")):
            os.remove(path)
        elif not os.path.isdir(path):
            continue
        elif TIME_DIR_RE.match(name) and name != "0":
            shutil.rmtree(path, ignore_errors=True)
        elif name == "postProcessing" or name.startswith("processor"):
            shutil.rmtree(path, ignore_errors=True)
    poly = os.path.join(case_root, "constant", "polyMesh")
    if os.path.isdir(poly):
        shutil.rmtree(poly, ignore_errors=True)


def first_fatal_error(case_root):
    for root, dirs, files in os.walk(case_root):
        for name in sorted(files):
            if not name.startswith("log."):
                continue
            try:
                with open(os.path.join(root, name), encoding="utf-8", errors="replace") as f:
                    text = f.read()
            except OSError:
                continue
            m = re.search(r"--> FOAM FATAL[^\n]*\n(.*?)(?:\n\n|\n    From)", text, re.S)
            if m:
                msg = " ".join(m.group(1).split())
                return f"{name}: {msg[:300]}"
    return ""


def run_one(split, dataset, directory, case_dir, timeout, clean):
    case_root = gt_dir(case_dir)
    label = f"{dataset}/{directory}" if split == "Basic" else dataset
    log_path = os.path.join(LOGS_DIR, f"gt_{split}_{label.replace('/', '_')}.log")
    if clean:
        clean_case(case_root)
    allrun = os.path.join(case_root, "Allrun")
    if not os.path.isfile(allrun):
        return [split, dataset, directory, 0, 0.0, "", "Allrun missing"]
    os.chmod(allrun, 0o755)
    start = time.time()
    error = ""
    try:
        with open(log_path, "w", encoding="utf-8") as log:
            subprocess.run(["sh", "./Allrun"], cwd=case_root, stdout=log, stderr=subprocess.STDOUT,
                           timeout=timeout, check=False)
    except subprocess.TimeoutExpired:
        error = f"timeout after {timeout}s"
    seconds = round(time.time() - start, 1)
    success = 1 if solver_log_success(case_root) else 0
    if not success and not error:
        error = first_fatal_error(case_root) or "solver log did not end with 'End'"
    return [split, dataset, directory, success, seconds, application_of(case_root) or "", error]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("-j", "--jobs", type=int, default=max(1, (os.cpu_count() or 2) - 1))
    ap.add_argument("--timeout", type=int, default=7200, help="seconds per case (default 7200)")
    ap.add_argument("--split", choices=["basic", "advanced", "all"], default="all")
    ap.add_argument("--only", action="append", help="regex on '<family>/<n>' or the Advanced case name; repeatable")
    ap.add_argument("--clean", action="store_true", help="delete previous results in each GT case first")
    ap.add_argument("--dataset", default=DATASET_DIR)
    ap.add_argument("--out", help="CSV path (default results/gt_run_<version>.csv)")
    args = ap.parse_args()

    wm, version = openfoam_env()
    ensure_dirs()
    splits = {"basic": ("Basic",), "advanced": ("Advanced",), "all": ("Basic", "Advanced")}[args.split]
    cases = list(iter_cases(args.dataset, splits, args.only))
    if not cases:
        sys.exit("no unpacked cases found; run read_json.py first")
    print(f"OpenFOAM {version} at {wm}; running {len(cases)} GT cases with {args.jobs} workers")

    rows = []
    with ThreadPoolExecutor(max_workers=args.jobs) as pool:
        futures = {pool.submit(run_one, *c, args.timeout, args.clean): c for c in cases}
        for fut in as_completed(futures):
            row = fut.result()
            rows.append(row)
            status = "ok " if row[3] else "FAIL"
            print(f"[{len(rows):3d}/{len(cases)}] {status} {row[0]}/{row[1]}/{row[2]} {row[4]:7.1f}s {row[6]}")

    rows.sort(key=lambda r: (r[0], r[1], r[2]))
    out = args.out or os.path.join(RESULTS_DIR, f"gt_run_{version}.csv")
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["Split", "Dataset", "Directory", "Success", "Seconds", "Application", "Error"])
        w.writerows(rows)
    ok = sum(r[3] for r in rows)
    print(f"\n{ok}/{len(rows)} GT cases finished with 'End'. Summary: {out}")
    return 0 if ok == len(rows) else 1


if __name__ == "__main__":
    sys.exit(main())
