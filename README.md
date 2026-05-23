# pytorch3d-wheels

Prebuilt [PyTorch3D](https://github.com/facebookresearch/pytorch3d) wheels
for Windows, Linux, and macOS (Apple Silicon), served from a PEP 503 simple
index hosted on GitHub Pages.

## Why this exists

PyTorch3D doesn't publish wheels for Windows on PyPI, and Linux/macOS
support upstream is limited. Installing it normally requires compiling
from source with a matching CUDA toolkit and host compiler — a painful
experience for users who just want to `pip install pytorch3d`.

This repo builds those wheels in CI for a bounded set of (Python, torch,
CUDA, OS) combinations and serves them through a simple index.

## Install

```bash
pip install pytorch3d \
  --extra-index-url https://ImageMindAnalytics.github.io/pytorch3d-wheels/simple/
```

If you have a specific torch + CUDA already installed and want pip to
pick the matching wheel, pin to the local-version tag:

```bash
# torch 2.8.0 + CUDA 12.9
pip install "pytorch3d==0.7.9+pt280cu129" \
  --extra-index-url https://ImageMindAnalytics.github.io/pytorch3d-wheels/simple/

# torch 2.8.0 + CPU only (e.g. macOS arm64)
pip install "pytorch3d==0.7.9+pt280cpu" \
  --extra-index-url https://ImageMindAnalytics.github.io/pytorch3d-wheels/simple/
```

The local-version tag format is `+pt<torch>cu<CUDA>` (or `+pt<torch>cpu`),
with dots stripped — `pt280cu129` for torch 2.8.0 + CUDA 12.9.

## Supported matrix

This is the support contract. Combinations outside this list are not built;
requests to add new combinations are evaluated based on CI cost and demand.

| OS                 | Python                 | torch  | CUDA  |
|--------------------|------------------------|--------|-------|
| Windows x86_64     | 3.10, 3.11, 3.12, 3.13 | 2.8.0  | 12.9  |
| Windows x86_64     | 3.10, 3.11, 3.12, 3.13 | 2.12.0 | 13.2  |
| Linux x86_64 (\*)  | 3.10, 3.11, 3.12, 3.13 | 2.8.0  | 12.9  |
| Linux x86_64 (\*)  | 3.10, 3.11, 3.12, 3.13 | 2.12.0 | 13.2  |
| macOS arm64        | 3.10, 3.11, 3.12, 3.13 | 2.8.0  | CPU   |

(\*) Linux wheels are `manylinux_2_28_x86_64`.

PyTorch3D version: **0.7.9** (the latest upstream release).

## Scope

- This repo only ships wheels — runtime bugs belong on the
  [upstream pytorch3d tracker](https://github.com/facebookresearch/pytorch3d/issues).
- Issues here should be about wheel availability, build failures, or
  installation problems caused by the wheels themselves.

## Building locally

You shouldn't need to. CI builds on push to `main` and on manual
workflow dispatch. If you do, see `scripts/build_one.py` and the
matching workflow in `.github/workflows/`.

## License

The build scripts here are MIT. The wheels they produce are PyTorch3D,
which is BSD-3-Clause.
