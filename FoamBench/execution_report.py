#!/usr/bin/env python3
"""Execution metric (M_exec): did the framework-generated case run to completion?

A case scores 1 when the solver log of the generated case (``log.<application>``
as named in its system/controlDict, or any ``log.*Foam``) ends with OpenFOAM's
final ``End`` line. The generated case is looked up in ``<case>/generated`` or,
failing that, in the first sub-directory of the case that is not ``GT_Files``.

    python3 execution_report.py            # -> results/basic_success_report.csv, results/advanced_success_report.csv
"""

import argparse
import csv
import os
import sys

from foambench_common import DATASET_DIR, RESULTS_DIR, ensure_dirs, generated_dir, iter_cases, solver_log_success


def analyze(dataset_dir, split):
    rows = []
    for _, dataset, directory, case_dir in iter_cases(dataset_dir, (split,)):
        gen = generated_dir(case_dir)
        success = 1 if gen and solver_log_success(gen) else 0
        rows.append([dataset, directory, success])
    return rows


def write_csv(path, rows):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["Dataset", "Directory", "Execution"])
        w.writerows(rows)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dataset", default=DATASET_DIR)
    ap.add_argument("--results", default=RESULTS_DIR)
    args = ap.parse_args()
    ensure_dirs()
    os.makedirs(args.results, exist_ok=True)
    for split, name in (("Basic", "basic_success_report.csv"), ("Advanced", "advanced_success_report.csv")):
        rows = analyze(args.dataset, split)
        out = os.path.join(args.results, name)
        write_csv(out, rows)
        print(f"{split}: {sum(r[2] for r in rows)}/{len(rows)} executed -> {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
