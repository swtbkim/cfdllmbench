"""Shared helpers for the FoamBench scripts (paths, case discovery, log checks).

Every script resolves paths relative to this file so that it works from any
current directory, and reads the OpenFOAM installation from the environment
that ``source /usr/lib/openfoam/openfoam2412/etc/bashrc`` sets up.
"""

import os
import re
import sys

FOAMBENCH_DIR = os.path.dirname(os.path.abspath(__file__))
DATASET_DIR = os.path.join(FOAMBENCH_DIR, "Dataset")
RESULTS_DIR = os.path.join(FOAMBENCH_DIR, "results")
LOGS_DIR = os.path.join(FOAMBENCH_DIR, "logs")

GT_DIRNAME = "GT_Files"
GENERATED_DIRNAME = "generated"

SPLITS = ("Basic", "Advanced")


def ensure_dirs():
    os.makedirs(RESULTS_DIR, exist_ok=True)
    os.makedirs(LOGS_DIR, exist_ok=True)


def openfoam_env():
    """Return (WM_PROJECT_DIR, WM_PROJECT_VERSION) or exit with a clear message."""
    wm = os.environ.get("WM_PROJECT_DIR", "")
    if not wm or not os.path.isfile(os.path.join(wm, "bin", "tools", "RunFunctions")):
        sys.exit(
            "OpenFOAM environment not found. Run\n"
            "    source /usr/lib/openfoam/openfoam2412/etc/bashrc\n"
            "in this shell first (WM_PROJECT_DIR must point to an OpenFOAM installation)."
        )
    return wm, os.environ.get("WM_PROJECT_VERSION", "?")


def iter_cases(dataset_dir=DATASET_DIR, splits=SPLITS, only=None):
    """Yield (split, dataset, directory_label, case_dir) for every unpacked case.

    ``only`` is a list of regular expressions searched (not anchored) in the case
    label '<family>/<n>' or the Advanced case name; anchor them ('^Cavity/1$')
    for an exact match.

    Basic cases live at Dataset/Basic/<family>/<1..10>/, Advanced cases at
    Dataset/Advanced/<name>/. ``directory_label`` is the variant number for Basic
    and 1 for Advanced, matching the CSV layout of the original scripts.
    """
    for split in splits:
        split_dir = os.path.join(dataset_dir, split)
        if not os.path.isdir(split_dir):
            continue
        for dataset in sorted(os.listdir(split_dir)):
            dataset_dir_ = os.path.join(split_dir, dataset)
            if not os.path.isdir(dataset_dir_):
                continue
            if split == "Basic":
                variants = sorted(
                    (d for d in os.listdir(dataset_dir_) if d.isdigit()), key=int
                )
                for v in variants:
                    case_dir = os.path.join(dataset_dir_, v)
                    label = f"{dataset}/{v}"
                    if only and not any(re.search(o, label) for o in only):
                        continue
                    yield split, dataset, int(v), case_dir
            else:
                label = dataset
                if only and not any(re.search(o, label) for o in only):
                    continue
                yield split, dataset, 1, dataset_dir_


def gt_dir(case_dir):
    return os.path.join(case_dir, GT_DIRNAME)


def generated_dir(case_dir):
    """Directory holding the framework-generated case, or None.

    A folder named ``generated`` wins; otherwise the first sub-directory that is
    not GT_Files (sorted, so the choice is deterministic).
    """
    preferred = os.path.join(case_dir, GENERATED_DIRNAME)
    if os.path.isdir(preferred):
        return _descend_to_case(preferred)
    others = sorted(
        d for d in os.listdir(case_dir)
        if os.path.isdir(os.path.join(case_dir, d)) and d != GT_DIRNAME
    )
    return _descend_to_case(os.path.join(case_dir, others[0])) if others else None


def _descend_to_case(path):
    """If ``path`` is not itself an OpenFOAM case but wraps exactly one directory that is, return that.

    Frameworks such as MetaOpenFOAM write run/<caseName>/..., so the moved output
    is one level deeper than the reports expect.
    """
    for _ in range(3):
        if os.path.isdir(os.path.join(path, "system")) or os.path.isdir(os.path.join(path, "constant")):
            return path
        subdirs = [d for d in os.listdir(path) if os.path.isdir(os.path.join(path, d))]
        if len(subdirs) != 1:
            return path
        path = os.path.join(path, subdirs[0])
    return path


def application_of(case_root):
    """Solver named by ``application`` in the case's system/controlDict.

    ``case_root/system/controlDict`` is used when present; otherwise the first
    system/controlDict found walking the tree (sorted, shallowest first).
    """
    candidates = [os.path.join(case_root, "system", "controlDict")]
    for root, dirs, files in os.walk(case_root):
        dirs.sort()
        if "controlDict" in files and os.path.basename(root) == "system":
            candidates.append(os.path.join(root, "controlDict"))
    for path in candidates:
        if not os.path.isfile(path):
            continue
        try:
            with open(path, encoding="utf-8", errors="replace") as f:
                m = re.search(r"\n\s*application\s+(\w+)\s*;", f.read())
        except OSError:
            continue
        if m:
            return m.group(1)
    return None


def log_ended(path):
    """True if an OpenFOAM log ends with the solver's final 'End' line."""
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            tail = [ln.strip() for ln in f.readlines()[-4:]]
    except OSError:
        return False
    return "End" in tail


def solver_log_success(case_root):
    """True if a solver log under ``case_root`` (any depth) finished with 'End'.

    Prefers ``log.<application>`` where the application is read from controlDict;
    falls back to any ``log.*Foam`` file, which is how the original benchmark
    scored execution.
    """
    app = application_of(case_root)
    app_logs, fallback = [], []
    for root, dirs, files in os.walk(case_root):
        for name in files:
            if app and name == f"log.{app}":
                app_logs.append(os.path.join(root, name))
            elif name.startswith("log.") and name.endswith("Foam"):
                fallback.append(os.path.join(root, name))
    if app_logs:
        # the solver named in controlDict decides; other *Foam logs are pre-processing tools
        return any(log_ended(p) for p in app_logs)
    return any(log_ended(p) for p in fallback)
