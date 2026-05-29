# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

python == 3.11
starfile
warpylib

## Installation with pip

`torch-projectors` is published on a separate index per CUDA variant. Pick the
extra that matches your hardware and pass the matching `--extra-index-url`:

```bash
pip install ".[cpu]"   --extra-index-url https://warpem.github.io/torch-projectors/cpu/simple/
pip install ".[cu126]" --extra-index-url https://warpem.github.io/torch-projectors/cu126/simple/
pip install ".[cu128]" --extra-index-url https://warpem.github.io/torch-projectors/cu128/simple/
pip install ".[cu129]" --extra-index-url https://warpem.github.io/torch-projectors/cu129/simple/
```

With `uv sync --extra <variant>` the index is selected automatically from
`pyproject.toml`; the `--extra-index-url` is only needed for plain `pip`.
