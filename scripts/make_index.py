"""
Generate a PEP 503 'simple' index from a directory of .whl files.

PEP 503 layout:
    simple/
        index.html              -- lists all distributions
        pytorch3d/
            index.html          -- lists all wheels for pytorch3d

Each wheel is linked relative to its index.html.

Usage:
    python make_index.py --wheels wheels/ --out site/simple/
"""
from __future__ import annotations

import argparse
import hashlib
import html
import re
from collections import defaultdict
from pathlib import Path


WHEEL_NAME_RE = re.compile(
    r"^(?P<dist>[A-Za-z0-9_.\-]+?)-(?P<version>[^-]+)(?:-(?P<build>\d[^-]*))?-"
    r"(?P<py>[^-]+)-(?P<abi>[^-]+)-(?P<plat>[^-]+)\.whl$"
)


def sha256_of(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def normalize(name: str) -> str:
    # PEP 503 normalization
    return re.sub(r"[-_.]+", "-", name).lower()


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--wheels", required=True, help="directory of .whl files")
    p.add_argument("--out", required=True, help="output simple/ dir")
    args = p.parse_args()

    wheels_dir = Path(args.wheels).resolve()
    out_dir = Path(args.out).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    grouped: dict[str, list[Path]] = defaultdict(list)
    for whl in sorted(wheels_dir.glob("*.whl")):
        m = WHEEL_NAME_RE.match(whl.name)
        if not m:
            print(f"warning: skipping unrecognized wheel name {whl.name}")
            continue
        dist = normalize(m.group("dist"))
        grouped[dist].append(whl)

    # Root index
    root = ["<!DOCTYPE html><html><head><meta charset='utf-8'>"
            "<title>Simple Index</title></head><body>"]
    for dist in sorted(grouped):
        root.append(f'<a href="{html.escape(dist)}/">{html.escape(dist)}</a><br>')
    root.append("</body></html>\n")
    (out_dir / "index.html").write_text("\n".join(root), encoding="utf-8")
    print(f"Wrote {out_dir / 'index.html'}")

    # Per-distribution indexes
    for dist, files in grouped.items():
        dist_dir = out_dir / dist
        dist_dir.mkdir(exist_ok=True)
        page = ["<!DOCTYPE html><html><head><meta charset='utf-8'>"
                f"<title>Links for {html.escape(dist)}</title></head><body>"
                f"<h1>Links for {html.escape(dist)}</h1>"]
        for whl in files:
            target = dist_dir / whl.name
            if not target.exists() or target.stat().st_size != whl.stat().st_size:
                # copy wheel into the per-dist folder
                target.write_bytes(whl.read_bytes())
            digest = sha256_of(target)
            page.append(
                f'<a href="{html.escape(whl.name)}#sha256={digest}">'
                f"{html.escape(whl.name)}</a><br>"
            )
        page.append("</body></html>\n")
        (dist_dir / "index.html").write_text("\n".join(page), encoding="utf-8")
        print(f"Wrote {dist_dir / 'index.html'} with {len(files)} wheels")


if __name__ == "__main__":
    main()
