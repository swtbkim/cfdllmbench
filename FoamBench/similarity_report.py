#!/usr/bin/env python3
"""Structural (M_struct) and file-content (M_file) similarity against the reference case.

For each of the sub-directories 0/, constant/ and system/ of the reference case,
every reference file is looked up at the same relative path in the generated
case. The share of reference files that exist in the generated case is the
tree score (M_struct); the mean ROUGE-L F-measure between the comment-stripped
reference and generated file texts is the file score (M_file). Both are then
averaged over the three sub-directories. Missing generated files score 0.

By default the reference files are read from GT_Files on disk, i.e. in the
state run_gt_cases.py left them (setFields, subsetMesh and refineMesh rewrite
0/ fields in place, exactly as they do in the framework's own case), which is
how the original benchmark scored. With --pristine the reference files are
taken from the JSON datasets instead, untouched by any run.

    python3 similarity_report.py    # -> results/similarity_report_basic.csv, results/similarity_report_advanced.csv
    python3 similarity_report.py --pristine
"""

import argparse
import csv
import json
import os
import sys

from rouge_score import rouge_scorer

from foambench_common import DATASET_DIR, RESULTS_DIR, ensure_dirs, generated_dir, gt_dir, iter_cases

SUBDIRS = ["0", "constant", "system"]
SCORER = rouge_scorer.RougeScorer(["rougeL"], use_stemmer=True)


def read_cleaned_code(path_or_text):
    """File text without comment lines and without the banner before FoamFile.

    ``path_or_text`` is a file path or a ("text", content) tuple.
    """
    if isinstance(path_or_text, tuple):
        lines = path_or_text[1].splitlines(keepends=True)
    else:
        try:
            with open(path_or_text, encoding="utf-8", errors="replace") as f:
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


def compare_dir_pair(gt_sub, gen_sub, gt_files=None):
    """``gt_files`` maps relative path -> file path or ("text", content); default: files under gt_sub."""
    if gt_files is None:
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


def pristine_files(dataset_dir, split, dataset, directory):
    """Reference files of one case straight from the JSON dataset, keyed by sub-directory."""
    name = "FoamBench_basic.json" if split == "Basic" else "FoamBench_advanced.json"
    cache = pristine_files.cache
    if name not in cache:
        with open(os.path.join(dataset_dir, name), encoding="utf-8") as f:
            cache[name] = json.load(f)
    key = f"{dataset}/{directory}" if split == "Basic" else dataset
    files = cache[name].get(key, {})
    by_sub = {}
    for rel, text in files.items():
        sub = rel.split("/")[0]
        if sub in SUBDIRS and "polyMesh" not in rel:
            by_sub.setdefault(sub, {})["/".join(rel.split("/")[1:])] = ("text", text)
    return by_sub


pristine_files.cache = {}


def score_case(case_dir, pristine=None):
    gt = gt_dir(case_dir)
    gen = generated_dir(case_dir)
    total_file, total_tree, count = 0.0, 0.0, 0
    for sub in SUBDIRS:
        gt_sub = os.path.join(gt, sub)
        if pristine is not None:
            if sub not in pristine:
                continue
            file_score, tree_score = compare_dir_pair(gt_sub, os.path.join(gen, sub) if gen else None, pristine[sub])
            total_file += file_score
            total_tree += tree_score
            count += 1
            continue
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
    ap.add_argument("--pristine", action="store_true",
                    help="compare against the reference files in the JSON datasets instead of GT_Files on disk")
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
                pristine = pristine_files(args.dataset, split, dataset, directory) if args.pristine else None
                file_score, tree_score = score_case(case_dir, pristine)
                w.writerow([dataset, directory, file_score, tree_score])
                n += 1
        print(f"{split}: {n} cases -> {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
