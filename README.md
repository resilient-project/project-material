# Project Material - Presentation Slides

This repository contains LaTeX presentation slides for the RESILIENT project.

## Repository Structure

```
slides/
├── *.tex                   # LaTeX source files for presentations
├── *.pdf                   # Compiled PDF presentations (gitignored)
├── graphics/               # Centralized graphics folder
│   ├── logos/             # Logo files
│   └── *.{pdf,png,jpg}    # All other graphics
├── references.bib         # Bibliography file
└── beamer*.sty            # Beamer theme files
```

## Setup

### Prerequisites

- LaTeX distribution (TeX Live, MiKTeX, etc.)
- Python 3.x (for pre-commit hooks)
- pre-commit tool

### Installing Pre-commit

```bash
# Install pre-commit
pip install pre-commit

# Install the pre-commit hooks
pre-commit install

# (Optional) Run on all files
pre-commit run --all-files
```
