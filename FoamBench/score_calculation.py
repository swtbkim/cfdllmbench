#!/usr/bin/env python3
"""Combine the three reports into the FoamBench metrics.

    M_exec   execution score (0/1)
    M_struct tree score: share of reference files present in the generated case
    M_file   ROUGE-L similarity of the generated files to the reference files
    M_NMSE   1 if NMSE < 0.1, 0.5 if NMSE < 0.3, else 0
    Success  1 if M_exec == 1 and M_NMSE == 1

Every case of a split counts; a case missing from a report scores 0 for that
metric (and 9999 NMSE).

    python3 score_calculation.py    # -> results/final_benchmark_scores.csv, results/per_case_scores.csv
"""

import argparse
import os
import sys

import pandas as pd

from foambench_common import RESULTS_DIR, ensure_dirs


def score_nmse(val):
    if val < 0.1:
        return 1.0
    if val < 0.3:
        return 0.5
    return 0.0


def load(path, columns):
    if not os.path.isfile(path):
        return pd.DataFrame(columns=["Dataset", "Directory"] + columns)
    return pd.read_csv(path)


def evaluate(split, results_dir):
    tag = split.lower()
    exec_df = load(os.path.join(results_dir, f"{tag}_success_report.csv"), ["Execution"])
    sim_df = load(os.path.join(results_dir, f"similarity_report_{tag}.csv"), ["RougeL", "TreeScore"])
    nmse_df = load(os.path.join(results_dir, f"{tag}_nmse_report.csv"), ["NMSE"])
    for df in (exec_df, sim_df, nmse_df):
        df["Dataset"] = df["Dataset"].astype(str)
        df["Directory"] = df["Directory"].astype(int)
    merged = exec_df.merge(sim_df, on=["Dataset", "Directory"], how="outer")
    merged = merged.merge(nmse_df, on=["Dataset", "Directory"], how="outer")
    merged = merged.fillna({"Execution": 0, "RougeL": 0.0, "TreeScore": 0.0, "NMSE": 9999.0})
    merged["NMSE_Score"] = merged["NMSE"].apply(score_nmse)
    merged["Success"] = ((merged["Execution"] == 1) & (merged["NMSE_Score"] == 1)).astype(float)
    merged.insert(0, "Split", split)
    summary = pd.DataFrame({
        "Split": [split],
        "Cases": [len(merged)],
        "M_exec": [merged["Execution"].mean()],
        "M_struct": [merged["TreeScore"].mean()],
        "M_file": [merged["RougeL"].mean()],
        "M_NMSE": [merged["NMSE_Score"].mean()],
        "Success Ratio": [merged["Success"].mean()],
    })
    return summary, merged.sort_values(["Dataset", "Directory"])


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--results", default=RESULTS_DIR)
    args = ap.parse_args()
    ensure_dirs()
    summaries, per_case = [], []
    for split in ("Basic", "Advanced"):
        s, m = evaluate(split, args.results)
        summaries.append(s)
        per_case.append(m)
    final = pd.concat(summaries, ignore_index=True)
    final.to_csv(os.path.join(args.results, "final_benchmark_scores.csv"), index=False)
    pd.concat(per_case, ignore_index=True).to_csv(os.path.join(args.results, "per_case_scores.csv"), index=False)
    print(final.to_string(index=False))
    print(f"\nwritten: {os.path.join(args.results, 'final_benchmark_scores.csv')} and per_case_scores.csv")
    return 0


if __name__ == "__main__":
    sys.exit(main())
