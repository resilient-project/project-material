# Project Material - Presentation Slides

This repository contains LaTeX presentation slides for the RESILIENT project (https://resilient-project.github.io/).

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

- pixi package management tool: https://pixi.sh
- LaTeX distribution (TeX Live, MiKTeX, etc.)
- Python 3.x (for pre-commit hooks)
- pre-commit tool

### Setting up pixi environment and pre-commit

- After installing pixi and cloning the repo for the first time, run `pixi shell`. This will also install pre-commit
- To run the pre-commit hooks, use `pre-commit run --all-files`