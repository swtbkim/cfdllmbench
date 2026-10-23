#!/usr/bin/env python3
"""Relative error metric (M_NMSE): generated solution versus the reference solution.

Both cases are read with pyvista's OpenFOAM reader at the last written time of
the reference (the generated case is read at its closest time). For every
field in ``--fields`` that both cases carry as cell data, the normalised mean
squared error sum((y - y_hat)^2) / sum(y^2) is computed; the case score is the
mean over those fields. If the generated mesh has a different cell count, the
generated solution is sampled at the reference cell centres first (value of
the generated cell containing each centre). A generated case without a
written solution (only time 0) and any read failure give the sentinel 9999
(scored as 0 later).

The reference cases must have been run with run_gt_cases.py before this script.

    python3 nmse_report.py    # -> results/basic_nmse_report.csv, results/advanced_nmse_report.csv
"""

import argparse
import csv
import os
import sys

import numpy as np

from foambench_common import DATASET_DIR, RESULTS_DIR, ensure_dirs, generated_dir, gt_dir, iter_cases

DEFAULT_FIELDS = ["U", "p", "rho", "T"]
SENTINEL = 9999.0


def nmse(ref, gen):
    denom = float(np.sum(ref ** 2))
    if denom == 0.0:
        return SENTINEL
    return float(np.sum((ref - gen) ** 2) / denom)


class FoamMarker:
    """Context manager creating the empty .foam file pyvista needs, and removing it again."""

    def __init__(self, case_root):
        self.path = os.path.join(case_root, os.path.basename(case_root.rstrip("/")) + ".foam")
        self.created = False

    def __enter__(self):
        if not os.path.exists(self.path):
            open(self.path, "w").close()
            self.created = True
        return self.path

    def __exit__(self, *exc):
        if self.created:
            try:
                os.remove(self.path)
            except OSError:
                pass


def read_last(case_root, time_value=None):
    import pyvista as pv
    try:
        # VTK prints verbose errors for unreadable cases; the sentinel score already reports them
        import vtk
        vtk.vtkObject.GlobalWarningDisplayOff()
    except Exception:
        pass
    with FoamMarker(case_root) as marker:
        reader = pv.OpenFOAMReader(marker)
        # time 0 holds the initial condition, not a solution
        times = [t for t in reader.time_values if t > 0]
        if not times:
            raise RuntimeError("no solution time directories")
        if time_value is None:
            t = times[-1]
        else:
            t = min(times, key=lambda x: abs(x - time_value))
        reader.set_active_time_value(t)
        multiblock = reader.read()
        internal = multiblock[0]
        return internal, t


def align_and_scale(ref_mesh, gen_mesh):
    ref_b = np.array(ref_mesh.bounds).reshape(3, 2)
    gen_b = np.array(gen_mesh.bounds).reshape(3, 2)
    if np.allclose(ref_b, gen_b, atol=1e-6):
        return gen_mesh
    ref_size = ref_b[:, 1] - ref_b[:, 0]
    gen_size = gen_b[:, 1] - gen_b[:, 0]
    scaling = np.divide(ref_size, gen_size, out=np.ones_like(ref_size), where=gen_size != 0)
    aligned = gen_mesh.copy()
    aligned.points = (aligned.points - gen_b[:, 0]) * scaling + ref_b[:, 0]
    return aligned


def cell_map(ref, gen):
    """Index of the generated cell containing (or closest to) each reference cell centre."""
    centres = ref.cell_centers().points
    idx = np.asarray(gen.find_containing_cell(centres))
    missing = idx < 0
    if missing.any():
        idx[missing] = np.asarray(gen.find_closest_cell(centres[missing]))
    return idx


def evaluate(gt_root, gen_root, fields):
    try:
        ref, t_ref = read_last(gt_root)
        gen, _ = read_last(gen_root, t_ref)
        gen = align_and_scale(ref, gen)
    except Exception:
        return SENTINEL
    scores = []
    for field in fields:
        if field not in ref.cell_data or field not in gen.cell_data:
            continue
        try:
            ref_data = np.asarray(ref.cell_data[field], dtype=float)
            if ref.n_cells != gen.n_cells:
                gen_data = np.asarray(gen.cell_data[field], dtype=float)[cell_map(ref, gen)]
            else:
                gen_data = np.asarray(gen.cell_data[field], dtype=float)
            if ref_data.shape != gen_data.shape:
                scores.append(SENTINEL)
                continue
            scores.append(nmse(ref_data, gen_data))
        except Exception:
            scores.append(SENTINEL)
    return float(np.mean(scores)) if scores else SENTINEL


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dataset", default=DATASET_DIR)
    ap.add_argument("--results", default=RESULTS_DIR)
    ap.add_argument("--fields", nargs="+", default=DEFAULT_FIELDS)
    ap.add_argument("--self-check", action="store_true",
                    help="compare every reference case against itself (expected NMSE 0); writes results/<split>_nmse_selfcheck.csv")
    args = ap.parse_args()
    ensure_dirs()
    os.makedirs(args.results, exist_ok=True)
    suffix = "_nmse_selfcheck.csv" if args.self_check else "_nmse_report.csv"
    for split in ("Basic", "Advanced"):
        out = os.path.join(args.results, split.lower() + suffix)
        n, scored = 0, 0
        with open(out, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f, lineterminator="\n")
            w.writerow(["Dataset", "Directory", "NMSE"])
            for _, dataset, directory, case_dir in iter_cases(args.dataset, (split,)):
                gt_root = gt_dir(case_dir)
                gen_root = gt_root if args.self_check else generated_dir(case_dir)
                if gen_root and os.path.isdir(gt_root):
                    score = evaluate(gt_root, gen_root, args.fields)
                else:
                    score = SENTINEL
                w.writerow([dataset, directory, score])
                n += 1
                scored += score < SENTINEL
        print(f"{split}: {scored}/{n} cases scored -> {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
