# Setup guide

## One-time setup of the wheel-building repo

1. Create a public GitHub repo at `ImageMindAnalytics/pytorch3d-wheels`
   and push these files to its `main` branch.

2. In the repo settings:
   - **Pages** → Source: "Deploy from a branch", Branch: `gh-pages` /
     `(root)`. The first publish workflow run will create the
     `gh-pages` branch.
   - **Actions** → General → Workflow permissions: "Read and write
     permissions". Needed for the publish step to push to `gh-pages`.

## Verify the build matrix is real

Before the first run, walk each row in `matrix-windows.yml`,
`matrix-linux.yml`, `matrix-macos.yml` and confirm that:

1. `pip install torch==<X> torchvision==<Y> --index-url
   https://download.pytorch.org/whl/cu<NNN>` actually resolves. If
   upstream doesn't publish that combination, the row will fail
   immediately at build time.
2. For Linux: the corresponding
   `pytorch/manylinux2_28-builder:cuda<X>.<Y>` image is on Docker Hub.
3. The `pytorch3d` git tag (`v0.7.9` by default) exists upstream.

The cu132 rows are placeholders — verify them against
`https://download.pytorch.org/whl/cu132/` before depending on them.

## First build

From the GitHub Actions tab, dispatch each workflow (`Build Windows
wheels`, `Build Linux wheels`, `Build macOS wheels`) manually with
`publish: true`. Each:

1. Spins up runners in parallel — one per matrix row.
2. Each runner installs CUDA (if needed), the right host compiler,
   torch, and builds pytorch3d 0.7.9 from source. Expect 25-40 minutes
   per wheel on Windows/Linux, 10-15 on macOS.
3. After all build jobs finish, the publish job downloads the
   artifacts, merges with whatever's already on `gh-pages`, regenerates
   the PEP 503 index, and pushes.

All three publish jobs share the `gh-pages-deploy` concurrency group so
they queue rather than race. Whichever finishes last has the up-to-date
view of everyone's wheels.

When everything's done, browse to
`https://ImageMindAnalytics.github.io/pytorch3d-wheels/`. You should see
a landing page and `simple/pytorch3d/` listing all `.whl` files.

## Testing the install end-to-end

After publish completes, from a clean Python env that matches one of
the matrix rows:

```bash
pip install "pytorch3d==0.7.9+pt280cu129" \
  --extra-index-url https://ImageMindAnalytics.github.io/pytorch3d-wheels/simple/
python -c "import pytorch3d; print(pytorch3d.__version__)"
python -c "import pytorch3d.ops; print('ops OK')"
```

## Updating the matrix

Edit the appropriate `matrix-*.yml`, push, and re-run the workflow.
Publishing is additive — `gh-pages` is regenerated from existing
wheels merged with this run's artifacts, so workflows for one OS don't
wipe wheels from another. Wheels from the current run overwrite
same-named existing wheels.

To drop a row, delete it from the matrix and manually remove the
corresponding `.whl` files from the `gh-pages` branch (the additive
merge will otherwise keep them indefinitely).

## Troubleshooting

**Windows build fails with "Thrust requires at least C++17" or nvcc
warning about `-std=c++20`.** MSVC toolset is too old for the C++
standard PyTorch requests. Ensure `ilammy/msvc-dev-cmd` has no
`toolset:` pin so the runner uses default v143 (VS 2022). This is the
default for `msvc_toolset: ""` in the matrix.

**Build fails during nvcc compilation with OOM.** Reduce `MAX_JOBS` in
`scripts/build_one.py` from 4 to 2.

**Linux: `auditwheel repair` fails with "cannot find libtorch.so".**
auditwheel found a torch lib reference it doesn't know how to vendor.
Add the offending library to the `--exclude` list in
`build-linux.yml` — torch's libs ship with the user's torch install,
not in our wheel.

**Smoke test fails with "undefined symbol" when importing pytorch3d.**
The wheel was built against a different torch ABI than what got
installed for the smoke test. Pin `torchvision` to a version that's
known to be released for your exact torch (check
`https://download.pytorch.org/whl/<cu*>/torchvision/`).

**Linux wheel is many GB.** auditwheel bundled CUDA runtime libs.
Add them to `--exclude` (libcudart, libcublas, libcudnn, etc.) — the
user gets these via torch.

**User on different glibc reports `version GLIBC_X.YZ not found` when
importing.** The manylinux container's glibc floor is higher than the
user's distro. Rebuild against an older manylinux image (e.g.
`pytorch/manylinux2014-builder` if available for that CUDA version)
and update `arch:` accordingly.
