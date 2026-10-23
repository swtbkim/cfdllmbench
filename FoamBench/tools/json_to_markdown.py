#!/usr/bin/env python3
"""Render the FoamBench dataset JSON files as human-readable Markdown.

For every case the Markdown page shows the natural-language prompt, the list of
reference files, and the content of each file in a fenced code block. For the
Basic split, variants 2..10 of a family additionally show a unified diff against
variant 1 (prompt and files), because that is the fastest way to see what a
variant changes.

Usage:
    python3 json_to_markdown.py --dataset Dataset --out Dataset/md

Output layout:
    <out>/README.md                      index of every case
    <out>/Basic/<family>/README.md       family overview + variant table
    <out>/Basic/<family>/<n>.md          one page per variant
    <out>/Advanced/<case>.md             one page per Advanced case
"""

import argparse
import difflib
import json
import os
import re
import shutil
import sys
from collections import OrderedDict

FENCE = "```"


def load(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f, object_pairs_hook=OrderedDict)


def solver_of(files):
    m = re.search(r"application\s+(\w+)\s*;", files.get("system/controlDict", ""))
    return m.group(1) if m else "?"


def turbulence_of(files):
    tp = files.get("constant/turbulenceProperties", files.get("constant/momentumTransport", ""))
    sim = re.search(r"simulationType\s+(\w+)\s*;", tp)
    model = re.search(r"(?:RASModel|LESModel|model)\s+(\w+)\s*;", tp)
    if not sim:
        return "-"
    if sim.group(1) == "laminar":
        lam = re.search(r"laminar\s*\{[^}]*?model\s+(\w+)", tp, re.S)
        return "laminar" + (f" ({lam.group(1)})" if lam else "")
    return f"{sim.group(1)} {model.group(1) if model else ''}".strip()


def time_controls(files):
    cd = files.get("system/controlDict", "")
    def get(key):
        m = re.search(r"\n\s*" + key + r"\s+([^;]+);", cd)
        return m.group(1).strip() if m else "?"
    return get("endTime"), get("deltaT"), get("writeInterval")


def mesh_cells(files):
    bm = files.get("system/blockMeshDict", "")
    total = 0
    for m in re.finditer(r"hex\s*\([^)]*\)\s*(?:\w+\s*)?\(\s*(\d+)\s+(\d+)\s+(\d+)\s*\)", bm):
        total += int(m.group(1)) * int(m.group(2)) * int(m.group(3))
    return total or "?"


def code_block(text, lang=""):
    fence = FENCE
    while fence in text:
        fence += "`"
    return f"{fence}{lang}\n{text.rstrip()}\n{fence}\n"


def file_sections(files):
    out = []
    for path, text in files.items():
        if path == "usr_requirement":
            continue
        lang = "sh" if path == "Allrun" else "cpp"
        out.append(f"### `{path}`\n\n{code_block(text, lang)}\n")
    return "".join(out)


def unified_diff(a, b, name):
    lines = list(difflib.unified_diff(a.splitlines(), b.splitlines(), fromfile=f"1/{name}", tofile=name, lineterm="", n=2))
    return "\n".join(lines)


def case_page(key, files, base=None, base_key=None):
    """Markdown for one case; ``base`` is the variant-1 case for diff rendering."""
    prompt = files["usr_requirement"]
    solver = solver_of(files)
    end, dt, wi = time_controls(files)
    md = [f"# {key}\n"]
    md.append("| | |\n|---|---|\n")
    md.append(f"| Solver | `{solver}` |\n")
    md.append(f"| Turbulence | {turbulence_of(files)} |\n")
    md.append(f"| Mesh cells (blockMesh) | {mesh_cells(files)} |\n")
    md.append(f"| endTime / deltaT / writeInterval | {end} / {dt} / {wi} |\n")
    md.append(f"| Reference files | {len(files) - 1} |\n\n")
    md.append("## Prompt (`usr_requirement`)\n\n")
    md.append("> " + prompt.strip().replace("\n", "\n> ") + "\n\n")

    if base is not None:
        md.append(f"## Differences from `{base_key}`\n\n")
        md.append("Prompt: " + prompt_word_diff(base["usr_requirement"], prompt) + "\n\n")
        changed = [p for p in files if p != "usr_requirement" and files[p] != base.get(p)]
        missing = [p for p in base if p != "usr_requirement" and p not in files]
        if not changed and not missing:
            md.append("Reference files: identical.\n\n")
        for p in changed:
            if p in base:
                md.append(f"`{p}`:\n\n" + code_block(unified_diff(base[p], files[p], p), "diff") + "\n")
            else:
                md.append(f"`{p}`: new in this variant.\n\n")
        for p in missing:
            md.append(f"`{p}`: present in variant 1 but not here.\n\n")

    md.append("## Reference files\n\n")
    md.append("".join(f"- `{p}`\n" for p in files if p != "usr_requirement") + "\n")
    md.append(file_sections(files))
    return "".join(md)


def family_page(fam, cases):
    first_key, first = next(iter(cases.items()))
    md = [f"# {fam} (Basic, {len(cases)} variants)\n\n"]
    md.append(f"Solver `{solver_of(first)}`, turbulence {turbulence_of(first)}.\n\n")
    md.append("## Baseline prompt (variant 1)\n\n> " + first["usr_requirement"].strip().replace("\n", "\n> ") + "\n\n")
    md.append("## Variants\n\n| Variant | Prompt change vs 1 | Files that differ from variant 1 |\n|---|---|---|\n")
    for key, files in cases.items():
        n = key.split("/")[1]
        if key == first_key:
            md.append(f"| [{n}]({n}.md) | baseline | - |\n")
            continue
        words = prompt_word_diff(first["usr_requirement"], files["usr_requirement"])
        changed = [p for p in files if p != "usr_requirement" and files[p] != first.get(p)]
        md.append(f"| [{n}]({n}.md) | {words} | {', '.join(f'`{c}`' for c in changed) or '-'} |\n")
    md.append("\n## Reference files (variant 1)\n\n" + "".join(f"- `{p}`\n" for p in first if p != "usr_requirement"))
    return "".join(md)


def prompt_word_diff(a, b):
    """Compact word-level description of what changed in the prompt."""
    sm = difflib.SequenceMatcher(None, a.split(), b.split())
    parts = []
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "equal":
            continue
        old = " ".join(a.split()[i1:i2])
        new = " ".join(b.split()[j1:j2])
        parts.append(f"`{old}` -> `{new}`" if old and new else (f"+`{new}`" if new else f"-`{old}`"))
    s = "; ".join(parts) if parts else "identical"
    return s.replace("|", "\\|")


def write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dataset", required=True, help="directory containing FoamBench_basic.json and FoamBench_advanced.json")
    ap.add_argument("--out", required=True, help="output directory for the Markdown tree")
    ap.add_argument("--clean", action="store_true", help="delete the output directory first")
    args = ap.parse_args()

    if args.clean and os.path.isdir(args.out):
        shutil.rmtree(args.out)

    basic = load(os.path.join(args.dataset, "FoamBench_basic.json"))
    advanced = load(os.path.join(args.dataset, "FoamBench_advanced.json"))

    families = OrderedDict()
    for key, files in basic.items():
        families.setdefault(key.split("/")[0], OrderedDict())[key] = files
    families = OrderedDict(sorted(families.items(), key=lambda kv: kv[0].lower()))
    # variants sorted numerically inside each family
    for fam in families:
        families[fam] = OrderedDict(sorted(families[fam].items(), key=lambda kv: int(kv[0].split("/")[1])))

    index = ["# FoamBench dataset (human-readable)\n\n",
             "Generated from `FoamBench_basic.json` and `FoamBench_advanced.json` by `tools/json_to_markdown.py`. ",
             "Do not edit these pages by hand; edit the JSON and regenerate.\n\n",
             f"## Basic ({len(basic)} cases, {len(families)} families)\n\n",
             "| Family | Solver | Turbulence | Variants |\n|---|---|---|---|\n"]
    for fam, cases in families.items():
        first_key, first = next(iter(cases.items()))
        write(os.path.join(args.out, "Basic", fam, "README.md"), family_page(fam, cases))
        for key, files in cases.items():
            n = key.split("/")[1]
            base = None if key == first_key else first
            write(os.path.join(args.out, "Basic", fam, f"{n}.md"), case_page(key, files, base, first_key))
        links = " ".join(f"[{k.split('/')[1]}](Basic/{fam}/{k.split('/')[1]}.md)" for k in cases)
        index.append(f"| [{fam}](Basic/{fam}/README.md) | `{solver_of(first)}` | {turbulence_of(first)} | {links} |\n")

    index.append(f"\n## Advanced ({len(advanced)} cases)\n\n| Case | Solver | Turbulence | Mesh cells |\n|---|---|---|---|\n")
    for key, files in advanced.items():
        write(os.path.join(args.out, "Advanced", f"{key}.md"), case_page(key, files))
        index.append(f"| [{key}](Advanced/{key}.md) | `{solver_of(files)}` | {turbulence_of(files)} | {mesh_cells(files)} |\n")

    write(os.path.join(args.out, "README.md"), "".join(index))
    print(f"wrote Markdown for {len(basic)} Basic and {len(advanced)} Advanced cases under {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
