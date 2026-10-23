#!/usr/bin/env python3
"""Example benchmark driver for the MetaOpenFOAM framework.

This script is specific to MetaOpenFOAM (https://github.com/Terry-cyx/MetaOpenFOAM):
for every unpacked case it points MetaOpenFOAM at the case's YAML config (written by
``read_json.py --metaopenfoam-yaml``), runs the framework, and moves the files the
framework produced into ``<case>/generated`` where the report scripts expect them.
Other frameworks only need to reproduce that last step: put the generated OpenFOAM
case (including its log.* files) under ``<case>/generated``.

    source /usr/lib/openfoam/openfoam2412/etc/bashrc
    export OPENAI_API_KEY=...
    python3 read_json.py --metaopenfoam-yaml
    python3 run_benchmarks.py --mode basic
"""

import argparse
import os
import shutil
import subprocess
import sys

from foambench_common import DATASET_DIR, FOAMBENCH_DIR, GENERATED_DIRNAME, LOGS_DIR, ensure_dirs, iter_cases, openfoam_env

META_ROOT = os.path.join(FOAMBENCH_DIR, "algorithm", "MetaOpenFOAM")
SRC_DIR = os.path.join(META_ROOT, "src")
PYTHON = sys.executable

# One-time database builders (run once) and the per-case workflow.
DB_SCRIPTS = [
    ("postprocess", "Tutorial_postprocess.py"),
    ("db_add_summary", "Langchain_database_add_tutorial_summary.py"),
    ("db_add_tutorial", "Langchain_database_add_tutorial.py"),
    ("db_add_command", "Langchain_database_add_command.py"),
    ("db_add_allrun", "Langchain_database_add_allrun.py"),
]
CASE_SCRIPTS = [
    ("config_path", "config_path.py"),
    ("main", "metaOpenfoam_v2.py"),
]


def run_scripts(scripts, input_yaml, log):
    for label, script in scripts:
        script_path = os.path.join(SRC_DIR, script)
        cmd = [PYTHON, "-u", script_path] + ([input_yaml] if label == "config_path" else [])
        print(f"  running {label}: {script}")
        result = subprocess.run(cmd, stdout=log, stderr=subprocess.STDOUT)
        if result.returncode != 0:
            print(f"  step {label} failed with code {result.returncode}")
            return False
    return True


def run_workflow(input_yaml, case_dir, label):
    os.environ["CONFIG_FILE_PATH"] = input_yaml
    os.environ["INPUT_DIR"] = os.path.dirname(input_yaml)
    os.environ["INPUT_DIR_METAFOAM"] = os.path.dirname(input_yaml)

    run_source = os.path.join(META_ROOT, "run")
    if os.path.exists(run_source):
        shutil.rmtree(run_source)
    os.makedirs(run_source, exist_ok=True)

    log_path = os.path.join(LOGS_DIR, f"metaopenfoam_{label.replace('/', '_')}.log")
    with open(log_path, "w", encoding="utf-8") as log:
        ok = run_scripts(CASE_SCRIPTS, input_yaml, log)

    generated = os.path.join(case_dir, GENERATED_DIRNAME)
    if os.path.exists(generated):
        shutil.rmtree(generated)
    os.makedirs(generated, exist_ok=True)
    for item in os.listdir(run_source):
        shutil.move(os.path.join(run_source, item), os.path.join(generated, item))
    shutil.rmtree(run_source, ignore_errors=True)
    print(f"  {'done' if ok else 'FAILED'}; output in {generated}, log in {log_path}")
    return ok


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--mode", choices=["basic", "advanced", "all"], default="all")
    ap.add_argument("--dataset", default=DATASET_DIR)
    ap.add_argument("--skip-db", action="store_true", help="skip the one-time MetaOpenFOAM database build")
    ap.add_argument("--only", action="append", help="regex on '<family>/<n>' or the Advanced case name; repeatable")
    args = ap.parse_args()

    wm, version = openfoam_env()
    ensure_dirs()
    if not os.path.isdir(SRC_DIR):
        sys.exit(f"MetaOpenFOAM not found at {META_ROOT}; clone it into algorithm/ first")
    if not os.environ.get("OPENAI_API_KEY"):
        sys.exit("OPENAI_API_KEY is not set")
    print(f"OpenFOAM {version} at {wm}")

    splits = {"basic": ("Basic",), "advanced": ("Advanced",), "all": ("Basic", "Advanced")}[args.mode]
    cases = list(iter_cases(args.dataset, splits, args.only))
    if not cases:
        sys.exit("no unpacked cases found; run read_json.py --metaopenfoam-yaml first")

    if not args.skip_db:
        first_yaml = os.path.join(cases[0][3], f"{cases[0][1]}.yaml")
        with open(os.path.join(LOGS_DIR, "metaopenfoam_database.log"), "w", encoding="utf-8") as log:
            os.environ["CONFIG_FILE_PATH"] = first_yaml
            if not run_scripts([("config_path", "config_path.py")] + DB_SCRIPTS, first_yaml, log):
                sys.exit("MetaOpenFOAM database build failed; see logs/metaopenfoam_database.log")

    failures = 0
    for split, dataset, directory, case_dir in cases:
        label = f"{dataset}/{directory}" if split == "Basic" else dataset
        yaml_path = os.path.join(case_dir, f"{dataset}.yaml")
        if not os.path.isfile(yaml_path):
            print(f"{label}: no {dataset}.yaml (run read_json.py --metaopenfoam-yaml); skipped")
            failures += 1
            continue
        print(f"\n{split} case {label}")
        if not run_workflow(yaml_path, case_dir, label):
            failures += 1
    print(f"\nfinished {len(cases)} cases, {failures} failed")
    return 0 if failures == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
