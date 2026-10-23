#!/usr/bin/env python3
"""Port the FoamBench reference cases from OpenFOAM Foundation v10 to OpenFOAM ESI v2412.

The script reads the original dataset JSON files (one dict per case, mapping a relative
file path to its text content, plus the natural-language ``usr_requirement``) and writes
new JSON files with the same keys and the same case order, where every reference case
has been rewritten so that it runs unchanged on OpenFOAM v2412 (openfoam.com).

Usage:
    python3 port_v10_to_v2412.py --src Dataset/v10 --dst Dataset [--report report.json]

Every transformation is a deterministic text rule; family-specific rules live in
``FAMILY_RULES`` so that the mapping table is readable in one place.
"""

import argparse
import json
import os
import re
import sys
from collections import OrderedDict

# ---------------------------------------------------------------------------
# Header handling
# ---------------------------------------------------------------------------

ESI_BANNER = (
    "/*--------------------------------*- C++ -*----------------------------------*\\\n"
    "| =========                 |                                                 |\n"
    "| \\\\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox           |\n"
    "|  \\\\    /   O peration     | Version:  v2412                                 |\n"
    "|   \\\\  /    A nd           | Website:  www.openfoam.com                      |\n"
    "|    \\\\/     M anipulation  |                                                 |\n"
    "\\*---------------------------------------------------------------------------*/\n"
)

SEPARATOR = "// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //\n"
FOOTER = "// ************************************************************************* //\n"

BANNER_RE = re.compile(r"\A\s*/\*-{10,}\*- C\+\+ -\*-{10,}\*\\\n.*?\n\\\*-{10,}\*/\n", re.S)


def replace_banner(text):
    """Replace a Foundation or old ESI banner by the v2412 banner, or prepend one."""
    if BANNER_RE.match(text):
        return BANNER_RE.sub(lambda m: ESI_BANNER, text, count=1)
    return ESI_BANNER + text.lstrip("\n")


def ensure_version(text):
    """Make sure the FoamFile header carries ``version 2.0;`` as its first entry."""
    m = re.search(r"FoamFile\s*\{\n", text)
    if not m:
        return text
    head = text[m.end():m.end() + 400]
    if re.match(r"\s*version\s", head):
        return text
    return text[: m.end()] + "    version     2.0;\n" + text[m.end():]


def set_object(text, name):
    return re.sub(r"(\n\s*object\s+)[^;]+;", r"\g<1>" + name + ";", text, count=1)


def set_location(text, location):
    if re.search(r"\n\s*location\s+", text):
        return re.sub(r'(\n\s*location\s+)"[^"]*";', r'\g<1>"' + location + '";', text, count=1)
    return text


def set_format_ascii(text):
    return re.sub(r"(\n\s*format\s+)binary;", r"\g<1>ascii;", text, count=1)


def drop_line(text, pattern):
    """Remove every whole line that matches ``pattern`` (a regex applied to the line)."""
    out = []
    for line in text.split("\n"):
        if re.search(pattern, line):
            continue
        out.append(line)
    return "\n".join(out)


def foamfile(cls, obj, location=None):
    loc = f'    location    "{location}";\n' if location else ""
    return (
        "FoamFile\n{\n    version     2.0;\n    format      ascii;\n"
        f"    class       {cls};\n{loc}    object      {obj};\n}}\n"
    )


def banner_note(text):
    """Return the free text (e.g. a literature reference) a banner carries after its logo, as // comments."""
    m = BANNER_RE.match(text)
    if not m:
        return ""
    lines = m.group(0).split("\n")
    note = []
    seen_rule = False
    for line in lines:
        if re.match(r"^-{60,}$", line):
            seen_rule = True
            continue
        if seen_rule and not line.startswith("\\*---") and line.strip():
            note.append("// " + line.rstrip())
    return ("\n".join(note) + "\n\n") if note else ""


def body_after_header(text):
    """Return the text after the banner, the FoamFile block and the separator line."""
    note = banner_note(text)
    text = BANNER_RE.sub("", text, count=1)
    m = re.search(r"FoamFile\s*\{.*?\n\}\n", text, re.S)
    rest = text[m.end():] if m else text
    rest = re.sub(r"\A(\s*// \*.*\*\s*//\n)", "", rest)
    return note + rest.lstrip("\n")


# ---------------------------------------------------------------------------
# Generic rules shared by every case
# ---------------------------------------------------------------------------

def rule_turbulence_properties(text):
    """momentumTransport -> turbulenceProperties (Foundation ``model`` -> RASModel/LESModel)."""
    text = set_object(text, "turbulenceProperties")
    sim = re.search(r"simulationType\s+(\w+)\s*;", text)
    # The model keyword depends on the block it lives in, not on simulationType, because the
    # Foundation tutorials sometimes keep a dead RAS block under simulationType laminar.
    def fix_block(block_name, keyword):
        nonlocal text
        pat = re.compile(r"(\n" + block_name + r"\s*\{[^{}]*?\n\s*)model\s+(\w+;)")
        text = pat.sub(r"\g<1>" + keyword.ljust(16) + r"\g<2>", text)
    fix_block("RAS", "RASModel")
    fix_block("LES", "LESModel")
    text = text.replace("generalisedNewtonian", "generalizedNewtonian")
    if "viscosityModel CrossPowerLaw" in text and "tauStar" not in text:
        # ESI reads tauStar as well; tauStar 0 selects nu = nuInf + (nu0 - nuInf)/(1 + (m*strainRate)^n)
        text = re.sub(r"(\n(\s*)n\s+[^;]+;\n)", r"\g<1>\g<2>tauStar         0;\n", text, count=1)
    return text


def rule_transport_properties(text):
    """Incompressible physicalProperties -> transportProperties."""
    text = set_object(text, "transportProperties")
    text = re.sub(r"viscosityModel\s+constant\s*;", "transportModel  Newtonian;", text)
    # 'nu 1e-05 [m^2/s];' and 'nu [0 2 -1 0 0 0 0] 1e-05;' -> 'nu 1e-05;'
    text = re.sub(r"(\n\s*nu\s+)([-+0-9.eE]+)\s*\[[^\]]*\]\s*;", r"\g<1>\g<2>;", text)
    text = re.sub(r"(\n\s*nu\s+)\[[^\]]*\]\s*([-+0-9.eE]+)\s*;", r"\g<1>\g<2>;", text)
    return text


def rule_thermophysical_properties(text):
    text = set_object(text, "thermophysicalProperties")
    return text


def rule_control_dict(text):
    text = drop_line(text, r"^\s*solver\s+incompressibleFluid\s*;")
    return text


def rule_fv_solution(text):
    text = drop_line(text, r"^\s*transportPredictionFirst\s+\w+\s*;")
    return text


def rule_topo_set(text):
    return re.sub(r"(action\s+)delete;", r"\g<1>subtract;", text)


def rule_refine_mesh(text):
    text = re.sub(r"\be1\b", "tan1", text)
    text = re.sub(r"\be2\b", "tan2", text)
    return text


def rule_allrun(text):
    # ESI utilities resolve -dict relative to the case directory, not to system/.
    text = re.sub(r"-dict\s+(topoSetDict|refineMeshDict)", r"-dict system/\g<1>", text)
    # ESI subsetMesh has no -noFields option.
    text = text.replace(" -noFields", "")
    text = text.replace("runApplication buoyantFoam", "runApplication buoyantBoussinesqPimpleFoam")
    return text


# ---------------------------------------------------------------------------
# Family-specific rules
# ---------------------------------------------------------------------------

def parse_scalar(text, key):
    m = re.search(r"\n\s*" + key + r"\s+([-+0-9.eE]+)\s*;", text)
    return m.group(1) if m else None


def two_phase_transport_properties(files, phases):
    """Build an ESI transportProperties from phaseProperties + physicalProperties.<phase>."""
    phase_props = files["constant/phaseProperties"]
    sigma = parse_scalar(phase_props, "sigma")
    out = replace_banner(foamfile("dictionary", "transportProperties", "constant")) + SEPARATOR + "\n"
    out += "phases          (" + " ".join(phases) + ");\n\n"
    for ph in phases:
        pp = files[f"constant/physicalProperties.{ph}"]
        nu = parse_scalar(pp, "nu")
        rho = parse_scalar(pp, "rho")
        out += f"{ph}\n{{\n    transportModel  Newtonian;\n    nu              {nu};\n    rho             {rho};\n}}\n\n"
    out += f"sigma           {sigma};\n\n\n" + FOOTER
    return out


def dam_break_dynamic_mesh(text):
    """Foundation topoChanger refiner -> ESI dynamicRefineFvMesh."""
    def val(key, default):
        v = parse_scalar(text, key)
        return v if v is not None else default
    field = re.search(r"\n\s*field\s+([\w.]+)\s*;", text).group(1)
    out = replace_banner(foamfile("dictionary", "dynamicMeshDict", "constant")) + SEPARATOR + "\n"
    out += "dynamicFvMesh   dynamicRefineFvMesh;\n\n"
    out += "// How often to refine\n"
    out += f"refineInterval  {val('refineInterval', '1')};\n\n"
    out += "// Field to be refinement on\n"
    out += f"field           {field};\n\n"
    out += "// Refine field in between lower..upper\n"
    out += f"lowerRefineLevel {val('lowerRefineLevel', '0.001')};\n"
    out += f"upperRefineLevel {val('upperRefineLevel', '0.999')};\n\n"
    out += "// If value < unrefineLevel unrefine\n"
    out += "unrefineLevel   10;\n\n"
    out += "// Have slower than 2:1 refinement\n"
    out += f"nBufferLayers   {val('nBufferLayers', '1')};\n\n"
    out += "// Refine cells only up to maxRefinement levels\n"
    out += f"maxRefinement   {val('maxRefinement', '2')};\n\n"
    out += "// Stop refinement if maxCells reached\n"
    out += f"maxCells        {val('maxCells', '200000')};\n\n"
    out += "// Flux field and corresponding velocity field. Fluxes on changed\n"
    out += "// faces get recalculated by interpolating the velocity. Use 'none'\n"
    out += "// on surfaceScalarFields that do not need to be reinterpolated.\n"
    out += "correctFluxes\n(\n    (phi none)\n    (nHatf none)\n    (rhoPhi none)\n"
    out += f"    (alphaPhi0.{field.split('.')[-1]} none)\n    (ghf none)\n    (alphaPhiUn none)\n);\n\n"
    out += "// Write the refinement level as a volScalarField\n"
    out += "dumpLevel       true;\n\n\n" + FOOTER
    return out


SPECIES_ELEMENTS = {
    "O2": {"O": 2},
    "H2O": {"H": 2, "O": 1},
    "CH4": {"C": 1, "H": 4},
    "CO2": {"C": 1, "O": 2},
    "N2": {"N": 2},
}


def combustion_thermo_file(text):
    """Foundation thermo.compressibleGas (with species list) -> ESI (no list, with elements)."""
    body = re.sub(r"(?:^|\n)\s*species\s*\([^)]*\)\s*;\s*\n", "\n", body_after_header(text), count=1)
    # add an elements sub-dictionary to every specie block that lacks one
    def add_elements(m):
        name = m.group(1)
        elems = SPECIES_ELEMENTS.get(name)
        if not elems or "elements" in body:
            return m.group(0)
        lines = "".join(f"        {e:<8}{n};\n" for e, n in elems.items())
        return m.group(0) + "    elements\n    {\n" + lines + "    }\n"
    body = re.sub(r"\n(\w+)\n\{\n    specie\n    \{\n[^}]*\}\n", add_elements, body)
    return replace_banner(foamfile("dictionary", "thermo.compressibleGas", "constant")) + SEPARATOR + body


def combustion_reactions_file(text, species):
    body = body_after_header(text)
    body = body.replace("irreversibleArrhenius;", "irreversibleArrheniusReaction;")
    if re.search(r"\n\s*species\s*\(", "\n" + body) or not species:
        # already in the ESI layout (species list inside the reactions file)
        return replace_banner(foamfile("dictionary", "reactions", "constant")) + SEPARATOR + "\n" + body.lstrip("\n")
    elements = []
    for sp in species:
        for e in SPECIES_ELEMENTS.get(sp, {}):
            if e not in elements:
                elements.append(e)
    head = "elements\n(\n" + "".join(f"    {e}\n" for e in elements) + ");\n\n"
    head += "species\n(\n" + "".join(f"    {s}\n" for s in species) + ");\n\n"
    return replace_banner(foamfile("dictionary", "reactions", "constant")) + SEPARATOR + "\n" + head + body.lstrip("\n")


def combustion_thermophysical_properties(text):
    text = set_object(text, "thermophysicalProperties")
    text = re.sub(r"mixture\s+coefficientWilkeMultiComponentMixture;", "mixture         reactingMixture;", text)
    text = re.sub(r"mixture\s+multiComponentMixture;", "mixture         reactingMixture;", text)
    text = re.sub(r"\n\s*defaultSpecie\s+(\w+);", r"\ninertSpecie         \g<1>;", text)
    text = re.sub(
        r'\n\s*#include\s+"thermo.compressibleGas"\s*\n',
        "\nchemistryReader     foamChemistryReader;\n\n"
        'foamChemistryFile   "<constant>/reactions";\n\n'
        'foamChemistryThermoFile "<constant>/thermo.compressibleGas";\n',
        text,
    )
    return text


def combustion_chemistry_properties(text):
    text = re.sub(r'\n\s*#include\s+"reactions"\s*\n', "\n", text)
    if "equilibriumRateLimiter" not in text:
        text = re.sub(
            r"(EulerImplicitCoeffs\s*\{\s*\n\s*cTauChem\s+[^;]+;\n)",
            r"\g<1>    equilibriumRateLimiter off;\n",
            text,
        )
    text = text.replace("Rosenbrock43", "Rosenbrock34")
    return text


def species_list(thermo_text):
    m = re.search(r"\n\s*species\s*\(([^)]*)\)", thermo_text)
    return m.group(1).split() if m else []


def squarebend_pressure_limits(fv_solution, fv_constraints):
    pmin = parse_scalar(fv_constraints, "minFactor")
    pmax = parse_scalar(fv_constraints, "maxFactor")
    return re.sub(
        r"(SIMPLE\s*\{\s*\n)",
        r"\g<1>" + f"    pMinFactor      {pmin};\n    pMaxFactor      {pmax};\n\n",
        fv_solution,
        count=1,
    )


def bernard_transport_properties(physical_properties):
    mu = float(parse_scalar(physical_properties, "mu"))
    rho0 = float(parse_scalar(physical_properties, "rho0"))
    beta = parse_scalar(physical_properties, "beta")
    t0 = parse_scalar(physical_properties, "T0")
    pr = parse_scalar(physical_properties, "Pr")
    nu = mu / rho0
    out = replace_banner(foamfile("dictionary", "transportProperties", "constant")) + SEPARATOR + "\n"
    out += "transportModel  Newtonian;\n\n"
    out += f"// Laminar viscosity\nnu              {nu:g};\n\n"
    out += f"// Thermal expansion coefficient\nbeta            {beta};\n\n"
    out += f"// Reference temperature\nTRef            {t0};\n\n"
    out += f"// Laminar Prandtl number\nPr              {pr};\n\n"
    out += "// Turbulent Prandtl number\nPrt             1;\n\n\n" + FOOTER
    return out


BERNARD_FUNCTIONS = """functions
{
    #includeFunc solverInfo(p_rgh)

    streamlines
    {
        type            streamLine;
        libs            (fieldFunctionObjects);
        writeControl    writeTime;
        setFormat       vtk;
        U               U;
        fields          (U);
        lifeTime        10000;
        nSubCycle       5;
        direction       bidirectional;
        seedSampleSet
        {
            type        uniform;
            axis        x;
            start       (0 0.5 0);
            end         (9 0.5 0);
            nPoints     24;
        }
    }
}
"""


def bernard_control_dict(text):
    text = text.replace("application     buoyantFoam;", "application     buoyantBoussinesqPimpleFoam;")
    text = re.sub(r"functions\s*\{.*?\n\}\n", BERNARD_FUNCTIONS, text, count=1, flags=re.S)
    return text


def bernard_fv_solution(text):
    text = re.sub(r'\n\s*"rho\.\*"\s*\{[^}]*\}\n', "\n", text, count=1)
    text = text.replace('"(U|e|k|epsilon)"', '"(U|T|k|epsilon)"')
    text = text.replace('"(U|e|k|epsilon)Final"', '"(U|T|k|epsilon)Final"')
    return text


def bernard_fv_schemes(text):
    text = re.sub(r"div\(phi,e\)(\s+)", r"div(phi,T)\g<1>", text)
    text = drop_line(text, r"div\(phi,\(p\|rho\)\)")
    text = drop_line(text, r"div\(phi,K\)")
    text = text.replace("div(((rho*nuEff)*dev2(T(grad(U)))))", "div((nuEff*dev2(T(grad(U)))))")
    return text


def kinematic_pressure(text):
    return text.replace("dimensions      [1 -1 -2 0 0 0 0];", "dimensions      [0 2 -2 0 0 0 0];")


def bernard_p_rgh(text):
    text = kinematic_pressure(text)
    text = re.sub(
        r"(type\s+fixedFluxPressure;\n)",
        r"\g<1>        rho             rhok;\n",
        text,
        count=1,
    )
    return text


def bernard_alphat(text):
    text = text.replace("dimensions      [1 -1 -1 0 0 0 0];", "dimensions      [0 2 -1 0 0 0 0];")
    text = text.replace("compressible::alphatJayatillekeWallFunction", "alphatJayatillekeWallFunction")
    return text


def rhocentral_fv_solution(text):
    # The energy variable of a sensibleInternalEnergy thermo is e, not h.
    return re.sub(r"\n(\s*)h\n(\s*)\{", r"\n\g<1>e\n\g<2>{", text, count=1)


def counterflow_variant9_U(text):
    text = re.sub(r"(fuel\s*\{[^}]*?value\s+uniform\s*)\([^)]*\)", r"\g<1>(0.4 0 0)", text, flags=re.S)
    text = re.sub(r"(air\s*\{[^}]*?value\s+uniform\s*)\([^)]*\)", r"\g<1>(-0.3 0 0)", text, flags=re.S)
    return text


# ---------------------------------------------------------------------------
# Spalart-Allmaras nuTilda corrections
# ---------------------------------------------------------------------------
# The prompts of these Advanced cases prescribe nuTilda, but the shipped 0/nuTilda
# files were left at zero / zeroGradient (so the model was inert), or used a nut
# wall-function type on the nuTilda field. The reference is aligned with the prompt
# and with the standard SA wall condition (nuTilda = 0 at no-slip walls).
NUTILDA_FIXES = {
    # case name: (internal value, {patch: (type, value)})
    "Cavity_SA": ("3e-05", {"movingWall": ("fixedValue", "0"), "fixedWalls": ("fixedValue", "0")}),
    "Cavity_geometry_1": ("3e-05", {"movingWall": ("fixedValue", "0"), "fixedWalls": ("fixedValue", "0")}),
    "Cylinder_SA": ("0.03", {"left": ("fixedValue", "0.03"), "right": ("inletOutlet", "0.03"),
                             "up": ("fixedValue", "0"), "down": ("fixedValue", "0"), "cylinder": ("fixedValue", "0")}),
    "nozzleFlow2D_SA": ("1.7856e-05", {"inlet": ("fixedValue", "1.7856e-05"), "walls": ("fixedValue", "0")}),
    "Diamond_Obstacle_SA": (None, {"wall1": ("fixedValue", "0"), "wall2": ("fixedValue", "0"), "cylinder": ("fixedValue", "0")}),
    "Rectangular_Obstacle_SA": (None, {"wall1": ("fixedValue", "0"), "wall2": ("fixedValue", "0"), "cylinder": ("fixedValue", "0")}),
    "Double_Square_SA": (None, {"bottomWall": ("fixedValue", "0"), "topWall": ("fixedValue", "0"), "posts": ("fixedValue", "0")}),
}


# Other reference-file corrections (each aligned with the case's own prompt or with the mesh)
# obliqueShock_KE / obliqueShock_LES prompts state "dynamic viscosity mu is 1.6646e-4" but the files had mu 0
VISCOSITY_FIXES = {"obliqueShock_KE": "1.6646e-4", "obliqueShock_LES": "1.6646e-4"}
# squareBend/2 (inlet T 1500 K) aborts in v2412 with a negative temperature after four SIMPLE
# iterations when the enthalpy equation is relaxed with 0.9; 0.7 lets it run (the converged
# solution of a steady SIMPLE run does not depend on the relaxation factor).
ENTHALPY_RELAXATION_FIXES = {"squareBend/2": ("0.9", "0.7")}


def fix_nutilda(text, internal, patches):
    if internal is not None:
        text = re.sub(r"(\n\s*internalField\s+uniform\s+)[^;]+;", r"\g<1>" + internal + ";", text, count=1)
    for patch, (bc_type, value) in patches.items():
        if bc_type == "inletOutlet":
            block = (f"    {patch}\n    {{\n        type            inletOutlet;\n"
                     f"        inletValue      uniform {value};\n        value           uniform {value};\n    }}\n")
        else:
            block = (f"    {patch}\n    {{\n        type            {bc_type};\n"
                     f"        value           uniform {value};\n    }}\n")
        # replace the whole patch block, tolerating a trailing comment after the patch name
        text, n = re.subn(r"\n    " + re.escape(patch) + r"\s*(?://[^\n]*)?\n    \{[^}]*\}\n", "\n" + block, text, count=1)
        if n == 0:
            raise ValueError(f"patch {patch} not found in nuTilda file")
    return text


# ---------------------------------------------------------------------------
# Prompt edits (only where the prompt names something that does not exist in ESI)
# ---------------------------------------------------------------------------

PROMPT_RULES = {
    "BernardCells": [("buoyantFoam", "buoyantBoussinesqPimpleFoam")],
    "Cavity": [("model kEpsilon", "RASModel kEpsilon")],
    "Cylinder": [
        ("use constant viscosity model with nu value of", "use a Newtonian transport model with nu value of"),
        ("in physical properties", "in transportProperties"),
    ],
    "squareBend": [(" with turbulentBL profile", "")],
}

DELETE_FILES = {
    "0/uniform/time",
    "system/functions",
    "system/fvConstraints",
    "system/blockMeshDict1",
    "constant/phaseProperties",
}

DELETE_PREFIXES = ("0/data/",)


def family_of(key):
    return key.split("/")[0]


# ---------------------------------------------------------------------------
# Case conversion
# ---------------------------------------------------------------------------

def convert_case(key, files, log):
    """Return the converted OrderedDict for one case."""
    fam = family_of(key)
    variant = key.split("/")[1] if "/" in key else None
    is_combustion = "constant/reactions" in files
    is_two_phase = "constant/phaseProperties" in files
    is_bernard = fam == "BernardCells"
    is_rho_central = "rhoCentralFoam" in files.get("system/controlDict", "")

    out = OrderedDict()
    phases = []
    if is_two_phase:
        phases = re.search(r"phases\s*\(([^)]*)\)", files["constant/phaseProperties"]).group(1).split()
    species = species_list(files.get("constant/thermo.compressibleGas", "")) if is_combustion else []

    for path, text in files.items():
        if path == "usr_requirement":
            prompt = text
            rules = PROMPT_RULES.get(fam) or next((r for f, r in PROMPT_RULES.items() if fam.startswith(f + "_")), [])
            for old, new in rules:
                if old in prompt:
                    prompt = prompt.replace(old, new)
                    log.append(f"{key}: prompt '{old}' -> '{new}'")
            out[path] = prompt
            continue

        if path in DELETE_FILES or path.startswith(DELETE_PREFIXES):
            if path == "constant/phaseProperties":
                out["constant/transportProperties"] = two_phase_transport_properties(files, phases)
                log.append(f"{key}: phaseProperties + physicalProperties.* -> transportProperties")
            else:
                log.append(f"{key}: deleted {path}")
            continue

        if path.startswith("constant/physicalProperties.") and is_two_phase:
            continue  # merged into transportProperties above

        new_path = path
        if path == "Allrun":
            text = rule_allrun(text)
            out[new_path] = text
            continue

        if path == "constant/momentumTransport":
            new_path = "constant/turbulenceProperties"
            text = rule_turbulence_properties(text)
            if "sigmaK" in text:
                text = text.replace("sigmaK", "sigmak")  # the coefficient is spelled sigmak; sigmaK was ignored
                log.append(f"{key}: kEpsilonCoeffs sigmaK -> sigmak")
        elif path == "constant/physicalProperties":
            if is_bernard:
                new_path = "constant/transportProperties"
                text = bernard_transport_properties(text)
                log.append(f"{key}: physicalProperties (Boussinesq thermo) -> transportProperties")
            elif is_combustion:
                new_path = "constant/thermophysicalProperties"
                text = combustion_thermophysical_properties(text)
            elif "thermoType" in text:
                new_path = "constant/thermophysicalProperties"
                text = rule_thermophysical_properties(text)
                if key in VISCOSITY_FIXES:
                    text = re.sub(r"(\n\s*mu\s+)0\s*;", r"\g<1>" + VISCOSITY_FIXES[key] + ";", text, count=1)
                    log.append(f"{key}: mu 0 -> {VISCOSITY_FIXES[key]} as the prompt states")
            else:
                new_path = "constant/transportProperties"
                text = rule_transport_properties(text)
        elif path == "constant/thermo.compressibleGas":
            text = combustion_thermo_file(text)
        elif path == "constant/reactions":
            text = combustion_reactions_file(text, species)
        elif path == "constant/chemistryProperties":
            text = combustion_chemistry_properties(text)
        elif path == "constant/dynamicMeshDict" and "topoChanger" in text:
            text = dam_break_dynamic_mesh(text)
            log.append(f"{key}: dynamicMeshDict topoChanger -> dynamicRefineFvMesh")
        elif path == "system/controlDict":
            text = rule_control_dict(text)
            if is_bernard:
                text = bernard_control_dict(text)
            if is_combustion:
                text = re.sub(r"\nfunctions\s*\{\s*\n\s*#includeFunc Qdot\s*\n\}\n", "\n", text)
                log.append(f"{key}: removed '#includeFunc Qdot' (ESI reactingFoam writes Qdot itself)")
            text = text.replace(
                "#includeFunc patchAverage(patch=inlet, fields=(p U))",
                "#includeFunc patchAverage(name=inlet,p,U)",
            )
            # stray token left in one Advanced controlDict
            text = re.sub(r"\nin\n", "\n", text)
        elif path == "system/fvSolution":
            text = rule_fv_solution(text)
            if is_bernard:
                text = bernard_fv_solution(text)
            if "system/fvConstraints" in files and "SIMPLE" in text:
                text = squarebend_pressure_limits(text, files["system/fvConstraints"])
                log.append(f"{key}: fvConstraints limitPressure -> SIMPLE pMinFactor/pMaxFactor")
            if is_rho_central:
                text = rhocentral_fv_solution(text)
            if key in ENTHALPY_RELAXATION_FIXES:
                old_f, new_f = ENTHALPY_RELAXATION_FIXES[key]
                text, n = re.subn(r"(\n\s*h\s+)" + re.escape(old_f) + r"\s*;", r"\g<1>" + new_f + ";", text, count=1)
                if n:
                    log.append(f"{key}: enthalpy relaxation factor {old_f} -> {new_f} (negative T otherwise)")
            if is_two_phase and "cAlpha" not in text:
                text = re.sub(
                    r'((?:"alpha\.[^"]*"|alpha\.\w+)\s*\{\s*\n)',
                    r"\g<1>        cAlpha          1;\n",
                    text,
                    count=1,
                )
                log.append(f"{key}: added cAlpha 1 to the alpha solver dictionary (mandatory in ESI interFoam)")
        elif path == "system/fvSchemes":
            if is_bernard:
                text = bernard_fv_schemes(text)
            if is_two_phase:
                # ESI v2412 has no MPLIC scheme; vanLeer + interface compression is the ESI tutorial setup
                text = re.sub(r"(div\(phi,alpha\)\s+Gauss\s+)MPLIC;", r"\g<1>vanLeer;", text)
                if "div(phirb,alpha)" not in text:
                    text = re.sub(
                        r"(\n\s*div\(phi,alpha\)[^\n]*\n)",
                        r"\g<1>    div(phirb,alpha) Gauss linear;\n",
                        text,
                        count=1,
                    )
                    log.append(f"{key}: added div(phirb,alpha) scheme (read by ESI interFoam)")
            text = re.sub(r"Gauss LUST un;", "Gauss LUST grad(hU);", text)
        elif path == "system/topoSetDict" or re.match(r"system/topoSetDict\.\d+$", path):
            text = rule_topo_set(text)
        elif path == "system/refineMeshDict":
            text = rule_refine_mesh(text)
        elif path == "0/U" and "profile         turbulentBL;" in text:
            text = drop_line(text, r"profile\s+turbulentBL;")
            log.append(f"{key}: removed 'profile turbulentBL' (Foundation-only flowRateInletVelocity option)")
        elif path == "0/U" and is_combustion and variant == "9":
            text = counterflow_variant9_U(text)
            log.append(f"{key}: variant 9 0/U corrected to fuel (0.4 0 0) / air (-0.3 0 0) as the prompt states")
        elif path == "0/p_rgh" and is_two_phase:
            text = drop_line(text, r"^\s*psi\s+none;")
            text = drop_line(text, r"^\s*gamma\s+1;")
        elif path == "0/alpha.water":
            text = set_object(text, "alpha.water")
        elif path == "0/nuTilda" and key in NUTILDA_FIXES:
            internal, patches = NUTILDA_FIXES[key]
            text = fix_nutilda(text, internal, patches)
            if "\n    defaultfaces\n" in text:
                text = text.replace("\n    defaultfaces\n", "\n    defaultFaces\n")  # mesh patch is defaultFaces
            log.append(f"{key}: 0/nuTilda aligned with the prompt / standard SA wall condition")
        elif is_bernard and path in ("0/p",):
            text = kinematic_pressure(text)
        elif is_bernard and path == "0/p_rgh":
            text = bernard_p_rgh(text)
        elif is_bernard and path == "0/alphat":
            text = bernard_alphat(text)

        text = replace_banner(text)
        text = ensure_version(text)
        text = set_format_ascii(text)
        if new_path != path:
            log.append(f"{key}: {path} -> {new_path}")
        out[new_path] = text

    return out


def convert_dataset(data, log):
    out = OrderedDict()
    for key, files in data.items():
        out[key] = convert_case(key, files, log)
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--src", required=True, help="directory holding the v10 FoamBench_basic.json / FoamBench_advanced.json")
    ap.add_argument("--dst", required=True, help="directory to write the v2412 JSON files into")
    ap.add_argument("--report", help="optional path for a JSON log of every change")
    args = ap.parse_args()

    log = []
    for name in ("FoamBench_basic.json", "FoamBench_advanced.json"):
        src = os.path.join(args.src, name)
        with open(src, encoding="utf-8") as f:
            data = json.load(f, object_pairs_hook=OrderedDict)
        converted = convert_dataset(data, log)
        dst = os.path.join(args.dst, name)
        with open(dst, "w", encoding="utf-8") as f:
            json.dump(converted, f, indent=1, ensure_ascii=False)
            f.write("\n")
        print(f"{name}: {len(converted)} cases -> {dst}")

    if args.report:
        with open(args.report, "w", encoding="utf-8") as f:
            json.dump(log, f, indent=1, ensure_ascii=False)
    counts = {}
    for entry in log:
        kind = entry.split(": ", 1)[1]
        kind = re.sub(r"[-+0-9.eE() ]+$", "", kind)
        counts[kind] = counts.get(kind, 0) + 1
    for kind, n in sorted(counts.items(), key=lambda kv: -kv[1]):
        print(f"{n:5d}  {kind}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
