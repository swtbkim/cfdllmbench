#!/usr/bin/env python3
"""Structural (M_struct) and file-content (M_file) similarity against the reference case.

For each of the sub-directories 0/, constant/ and system/ of the reference case,
every reference file is looked up at the same relative path in the generated
case. The share of reference files that exist in the generated case is the
tree score (M_struct); the mean ROUGE-L F-measure between the comment-stripped
reference and generated file texts is the file score (M_file). Both are then
averaged over the three sub-directories. Missing generated files score 0.

    python3 similarity_report.py    # -> results/similarity_report_basic.csv, results/similarity_report_advanced.csv
"""

import argparse
import csv
import os
import sys

from rouge_score import rouge_scorer

from foambench_common import DATASET_DIR, RESULTS_DIR, ensure_dirs, generated_dir, gt_dir, iter_cases

SUBDIRS = ["0", "constant", "system"]
SCORER = rouge_scorer.RougeScorer(["rougeL"], use_stemmer=True)


def read_cleaned_code(path):
    """File text without comment lines and without the banner before FoamFile."""
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            lines = f.readlines()
    except OSError:
        return ""
    filtered = [ln for ln in lines if not ln.strip().startswith(("//", "/*", "*"))]
    started = False
    cleaned = []
    for ln in filtered:
        if "FoamFile" in ln or "{" in ln:
            started = True
        if started:
            cleaned.append(ln)
    return "".join(cleaned)


def get_all_files(base_path):
    files = {}
    for root, _, names in os.walk(base_path):
        for name in names:
            if name.startswith("log"):
                continue
            full = os.path.join(root, name)
            rel = os.path.relpath(full, base_path).replace("\\", "/")
            if "polyMesh" in rel:
                continue
            files[rel] = full
    return files


def rouge_l(gt_file, gen_file):
    gt = read_cleaned_code(gt_file)
    gen = read_cleaned_code(gen_file)
    if not gt or not gen:
        return 0.0
    try:
        return SCORER.score(gt, gen)["rougeL"].fmeasure
    except Exception:
        return 0.0


def compare_dir_pair(gt_sub, gen_sub):
    gt_files = get_all_files(gt_sub)
    gen_files = get_all_files(gen_sub) if gen_sub and os.path.isdir(gen_sub) else {}
    if not gt_files:
        return 0.0, 0.0
    sims, matches = [], 0
    for rel, gt_path in gt_files.items():
        gen_path = gen_files.get(rel)
        if gen_path:
            sims.append(rouge_l(gt_path, gen_path))
            matches += 1
        else:
            sims.append(0.0)
    return sum(sims) / len(gt_files), matches / len(gt_files)


def score_case(case_dir):
    gt = gt_dir(case_dir)
    gen = generated_dir(case_dir)
    total_file, total_tree, count = 0.0, 0.0, 0
    for sub in SUBDIRS:
        gt_sub = os.path.join(gt, sub)
        if not os.path.isdir(gt_sub):
            continue
        file_score, tree_score = compare_dir_pair(gt_sub, os.path.join(gen, sub) if gen else None)
        total_file += file_score
        total_tree += tree_score
        count += 1
    if count == 0:
        return 0.0, 0.0
    return round(total_file / count, 4), round(total_tree / count, 4)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dataset", default=DATASET_DIR)
    ap.add_argument("--results", default=RESULTS_DIR)
    args = ap.parse_args()
    ensure_dirs()
    os.makedirs(args.results, exist_ok=True)
    for split, name in (("Basic", "similarity_report_basic.csv"), ("Advanced", "similarity_report_advanced.csv")):
        out = os.path.join(args.results, name)
        n = 0
        with open(out, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f, lineterminator="\n")
            w.writerow(["Dataset", "Directory", "RougeL", "TreeScore"])
            for _, dataset, directory, case_dir in iter_cases(args.dataset, (split,)):
                file_score, tree_score = score_case(case_dir)
                w.writerow([dataset, directory, file_score, tree_score])
                n += 1
        print(f"{split}: {n} cases -> {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
