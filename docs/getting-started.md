# Getting Started

This guide will help you set up and run CFDLLMBench to evaluate Large Language Models on CFD tasks.

## Prerequisites

- Python 3.9 or higher
- Git
- OpenFOAM v2412 from openfoam.com (for FoamBench evaluation; works on WSL2)

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/NREL-Theseus/cfdllmbench.git
cd cfdllmbench
```

### 2. Install Dependencies

```bash
pip install -r FoamBench/requirements.txt      # numpy, pandas, pyvista, rouge-score, PyYAML
pip install -r CFDCodeBench/requirements.txt   # for CFDCodeBench
```

### 3. Set Up OpenFOAM (for FoamBench)

The FoamBench reference cases run on OpenFOAM v2412 (openfoam.com). On Ubuntu
or WSL2 (Ubuntu):

```bash
curl https://dl.openfoam.com/add-debian-repo.sh | sudo bash
sudo apt-get install openfoam2412-default
echo 'source /usr/lib/openfoam/openfoam2412/etc/bashrc' >> ~/.bashrc
```

On WSL2 keep the repository on the Linux filesystem (for example
`~/cfdllmbench`), not under `/mnt/c`. `python3 FoamBench/check_env.py`
verifies the installation.

## Quick Start

### Running CFDQuery

Evaluate conceptual understanding with multiple-choice questions:

```bash
python run_cfdquery.py --model gpt-3.5-turbo --output results/
```

### Running CFDCodeBench

Test code generation capabilities:

```bash
python run_cfdcodebench.py --model gpt-3.5-turbo --output results/
```

### Running FoamBench

Assess end-to-end OpenFOAM automation (see [FoamBench](components/foambench.md)):

```bash
cd FoamBench
python3 read_json.py            # unpack the 126 cases
python3 run_gt_cases.py -j 4    # run the reference cases once
# run your framework; its case goes to <case>/generated
python3 execution_report.py && python3 similarity_report.py && python3 nmse_report.py && python3 score_calculation.py
```

## Configuration

Configure your LLM API keys and settings in `config.yaml`:

```yaml
models:
  openai:
    api_key: "your-api-key-here"
    model: "gpt-3.5-turbo"
  
evaluation:
  timeout: 300
  max_retries: 3
```

## Next Steps

- [Explore Benchmark Components](components/overview.md)
- [View Results and Analysis](results.md)
- [Check API Reference](api.md)
