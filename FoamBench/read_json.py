#!/usr/bin/env python3
"""Unpack the FoamBench JSON datasets into OpenFOAM case trees.

    python3 read_json.py                 # both splits -> Dataset/Basic, Dataset/Advanced
    python3 read_json.py --split basic   # one split only
    python3 read_json.py --metaopenfoam-yaml   # also write the MetaOpenFOAM config YAML per case

Layout written for every case:
    Dataset/Basic/<family>/<n>/GT_Files/...      reference OpenFOAM case (Allrun, 0/, constant/, system/)
    Dataset/Basic/<family>/<n>/usr_requirement.txt
    Dataset/Advanced/<name>/GT_Files/...
    Dataset/Advanced/<name>/usr_requirement.txt

No credential is stored in the repository. With ``--metaopenfoam-yaml`` the
per-case YAML that MetaOpenFOAM needs is written from the OPENAI_API_KEY /
OPENAI_BASE_URL / METAGPT_PATH / OPENAI_MODEL environment variables at unpack
time (placeholders if unset); the unpacked Dataset/Basic and Dataset/Advanced
trees are ignored by git.
"""

import argparse
import json
import os
import sys

from foambench_common import DATASET_DIR, GT_DIRNAME

METAOPENFOAM_BASE_CONFIG = {
    "MetaGPT_PATH": os.environ.get("METAGPT_PATH", "<path to MetaGPT>"),
    "OPENAI_API_KEY": os.environ.get("OPENAI_API_KEY", "<set OPENAI_API_KEY>"),
    "OPENAI_BASE_URL": os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1"),
    "OPENAI_PROXY": "",
    "batchsize": 10,
    "max_loop": 10,
    "model": os.environ.get("OPENAI_MODEL", "gpt-4o"),
    "run_times": 1,
    "searchdocs": 2,
    "temperature": 0.0,
}


def unpack(json_path, out_root, write_yaml=False):
    with open(json_path, encoding="utf-8") as f:
        data = json.load(f)

    count = 0
    for case_key, files in data.items():
        case_root = os.path.join(out_root, case_key)
        gt_root = os.path.join(case_root, GT_DIRNAME)
        os.makedirs(gt_root, exist_ok=True)
        for rel_path, content in files.items():
            if rel_path == "usr_requirement":
                with open(os.path.join(case_root, "usr_requirement.txt"), "w", encoding="utf-8") as f:
                    f.write(content)
                if write_yaml:
                    import yaml  # optional dependency, only needed for MetaOpenFOAM
                    config = dict(METAOPENFOAM_BASE_CONFIG)
                    config["usr_requirment"] = content  # MetaOpenFOAM spells the key this way
                    dataset_name = case_key.split("/")[0]
                    with open(os.path.join(case_root, f"{dataset_name}.yaml"), "w", encoding="utf-8") as yf:
                        yaml.dump(config, yf, default_flow_style=False, sort_keys=False)
                continue
            full_path = os.path.join(gt_root, rel_path)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            with open(full_path, "w", encoding="utf-8", newline="\n") as f:
                f.write(content)
            if os.path.basename(rel_path) in ("Allrun", "Allclean"):
                os.chmod(full_path, 0o755)
        count += 1
    return count


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--split", choices=["basic", "advanced", "all"], default="all")
    ap.add_argument("--dataset", default=DATASET_DIR, help="directory holding the JSON files and receiving Basic/ Advanced/")
    ap.add_argument("--metaopenfoam-yaml", action="store_true", help="also write <family>.yaml for MetaOpenFOAM")
    args = ap.parse_args()

    jobs = []
    if args.split in ("basic", "all"):
        jobs.append(("FoamBench_basic.json", "Basic"))
    if args.split in ("advanced", "all"):
        jobs.append(("FoamBench_advanced.json", "Advanced"))
    for name, split in jobs:
        n = unpack(os.path.join(args.dataset, name), os.path.join(args.dataset, split), args.metaopenfoam_yaml)
        print(f"{name}: {n} cases unpacked into {os.path.join(args.dataset, split)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
