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
# torch 2.11.0 + CUDA 12.6 (Windows / Linux)
pip install "pytorch3d==0.7.9+pt2110cu126" \
  --extra-index-url https://ImageMindAnalytics.github.io/pytorch3d-wheels/simple/

# torch 2.11.0 + CUDA 12.8 (Windows / Linux)
pip install "pytorch3d==0.7.9+pt2110cu128" \
  --extra-index-url https://ImageMindAnalytics.github.io/pytorch3d-wheels/simple/

# torch 2.12.0 + CUDA 12.6 (Windows / Linux)
pip install "pytorch3d==0.7.9+pt2120cu126" \
  --extra-index-url https://ImageMindAnalytics.github.io/pytorch3d-wheels/simple/

# torch 2.8.0 + CPU only (macOS arm64)
pip install "pytorch3d==0.7.9+pt280cpu" \
  --extra-index-url https://ImageMindAnalytics.github.io/pytorch3d-wheels/simple/
```

The local-version tag format is `+pt<torch>cu<CUDA>` (or `+pt<torch>cpu`),
with dots stripped — `pt280cu129` for torch 2.8.0 + CUDA 12.9.

## Supported matrix

This is the support contract. Combinations outside this list are not built;
requests to add new combinations are evaluated based on CI cost and demand.

| OS                 | Python                 | torch  | CUDA       |
|--------------------|------------------------|--------|------------|
| Windows x86_64     | 3.10, 3.11, 3.12, 3.13 | 2.11.0 | 12.6, 12.8 |
| Windows x86_64     | 3.10, 3.11, 3.12, 3.13 | 2.12.0 | 12.6       |
| Linux x86_64 (\*)  | 3.10, 3.11, 3.12, 3.13 | 2.11.0 | 12.6, 12.8 |
| Linux x86_64 (\*)  | 3.10, 3.11, 3.12, 3.13 | 2.12.0 | 12.6       |
| macOS arm64        | 3.10, 3.11, 3.12, 3.13 | 2.8.0  | CPU        |

torch 2.12 has no cu128 builds on PyPI's torch index — that's why
torch 2.12 here is cu126-only.

(\*) Linux wheels are `manylinux_2_28_x86_64`.

PyTorch3D version: **0.7.9** (the latest upstream release).

### CUDA 13.x — currently blocked upstream

CUDA 13.x wheels (torch 2.12 + cu132) are **not shipped** while
pytorch3d's pulsar backend has a linker incompatibility with CUDA 13's
compilation model: pulsar's explicit template instantiations are
declared with hidden visibility but never emitted as defined symbols,
so `pytorch3d._C` fails to link. The matrix and workflows for cu132
live in `matrix-{windows,linux}-cu132.yml` and
`.github/workflows/build-{windows,linux}-cu132.yml` so we can pick
them back up once a fix is available (either upstream, or by patching
pytorch3d to disable pulsar). These workflows default to
`publish: false`.

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
