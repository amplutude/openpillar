#!/usr/bin/env python3
"""
Build script: walks the pillars/ directory tree and emits dist/data.json.

Directory convention:
  pillars/{pillar_num}/                       → Pillar (P-{pillar_num})
  pillars/{pillar_num}/{sub_num}/             → Sub-pillar (P-{pillar_num}-{sub_num})
  pillars/{pillar_num}/{sub_num}/policy.md    → Policy content for the sub-pillar
  pillars/{pillar_num}/{sub_num}/metadata.yaml

Each level has its own metadata.yaml.  The script merges all levels into a
single data.json that the static front-end fetches from S3.
"""

import json
import os
import sys
from pathlib import Path

import yaml


def load_yaml(path: Path) -> dict:
    with path.open() as f:
        return yaml.safe_load(f) or {}


def load_markdown(path: Path) -> str:
    with path.open() as f:
        return f.read()


def build(pillars_root: Path) -> dict:
    data: dict = {"pillars": []}

    for pillar_dir in sorted(pillars_root.iterdir()):
        if not pillar_dir.is_dir():
            continue

        pillar_meta_path = pillar_dir / "metadata.yaml"
        if not pillar_meta_path.exists():
            continue

        pillar = load_yaml(pillar_meta_path)
        pillar["sub_pillars"] = []

        for sub_dir in sorted(pillar_dir.iterdir()):
            if not sub_dir.is_dir():
                continue

            sub_meta_path = sub_dir / "metadata.yaml"
            if not sub_meta_path.exists():
                continue

            sub_pillar = load_yaml(sub_meta_path)

            policy_path = sub_dir / "policy.md"
            sub_pillar["policy_markdown"] = (
                load_markdown(policy_path) if policy_path.exists() else ""
            )

            pillar["sub_pillars"].append(sub_pillar)

        data["pillars"].append(pillar)

    return data


def main() -> None:
    repo_root = Path(__file__).parent.parent
    pillars_root = repo_root / "pillars"
    dist_dir = repo_root / "dist"
    dist_dir.mkdir(exist_ok=True)

    if not pillars_root.exists():
        print(f"ERROR: pillars directory not found at {pillars_root}", file=sys.stderr)
        sys.exit(1)

    data = build(pillars_root)
    out_path = dist_dir / "data.json"
    with out_path.open("w") as f:
        json.dump(data, f, indent=2, default=str)

    pillar_count = len(data["pillars"])
    sub_count = sum(len(p["sub_pillars"]) for p in data["pillars"])
    print(f"Built {pillar_count} pillars, {sub_count} sub-pillars → {out_path}")


if __name__ == "__main__":
    main()
